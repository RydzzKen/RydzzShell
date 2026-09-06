import difflib
import getpass
import io
import os
import shutil
import subprocess
import sys
import time

try:
    import readline
except ImportError:
    readline = None

from . import ai, commands, completions, config, gadgets, i18n, kits, pipe, snippets, tools, webclone
from .i18n import t


class _OutputCapturer:
    """Tee stdout: output tetap tampil, sekaligus disalin ke buffer.
    Dipakai untuk menangkap error terakhir bagi `ai error`."""

    def __init__(self):
        self.real = sys.stdout
        self.buf = io.StringIO()

    def write(self, s):
        self.real.write(s)
        self.buf.write(s)
        return len(s)

    def flush(self):
        self.real.flush()

    def isatty(self):
        return self.real.isatty()


def handle_dl(arg):
    args = arg.split() if arg else []
    if not args:
        print(config.wrap_text(t("dl.usage_help")))
        return

    if args[0] == "list":
        tools.list_downloads(args[1:])
        return
    if args[0] == "update":
        print(t("dl.updating"))
        tools.update_ytdlp()
        return
    if args[0] == "redo":
        tools.redownload(args[1:])
        return

    audio_only = "-q" in args or "--audio" in args
    dry_run = "--dry" in args or "-s" in args
    force = "--redo" in args or "--force" in args
    urls = [a for a in args if not a.startswith("-")]
    if not urls:
        print(config.wrap_text(t("dl.usage_simple")))
        return
    tools.download_batch(
        urls, audio_only=audio_only, dry_run=dry_run, force=force
    )


def handle_qr(arg):
    out_file = None
    parts = arg.split() if arg else []
    text_parts = []
    i = 0
    while i < len(parts):
        p = parts[i]
        if p in ("-o", "--output"):
            if i + 1 < len(parts):
                out_file = parts[i + 1]
                i += 2
            else:
                i += 1
            continue
        text_parts.append(p)
        i += 1
    tools.gen_qr(" ".join(text_parts).strip("\"'"), out_file)


def handle_ascii(arg):
    args = arg.split() if arg else []
    if not args or args[0] not in ("enc", "encode", "dec", "decode"):
        print(t("ascii.usage"))
        return

    mode = args[0]
    base, label, flag_remaining = tools._parse_ascii_flags(args[1:])
    if not flag_remaining:
        print(t("ascii.need_input", base=base))
        return

    input_text = " ".join(flag_remaining).strip("\"'")

    if mode in ("enc", "encode"):
        print(tools.ascii_encode(input_text, base))
    else:
        print(tools.ascii_decode(input_text, base))


def show_banner():
    """Menampilkan Tampilan Awal / ASCII Art"""
    config.clear_screen()
    if config.term_width() < 44:
        print(
            f"{config.GREEN_NEON}=== RydzzShell v2.4 ==={config.RESET}\n"
            f"{config.YELLOW}  {t('banner.hint')}{config.RESET}"
        )
        return
    banner = f"""{config.GREEN_NEON}
██████╗ ██╗   ██╗██████╗ ███████╗███████╗
██╔══██╗╚██╗ ██╔╝██╔══██╗╚══███╔╝╚══███╔╝
██████╔╝ ╚████╔╝ ██║  ██║  ███╔╝   ███╔╝
██╔══██╗  ╚██╔╝  ██║  ██║ ███╔╝   ███╔╝
██║  ██║   ██║   ██████╔╝███████╗███████╗
╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚══════╝╚══════╝
{config.CYAN}    --- Custom Interactive Shell v2.4 ---{config.RESET}
{config.YELLOW}  {t('banner.hint')}{config.RESET}
"""
    print(banner)


def show_help():
    print(config.divider())
    print(t("help.title"))
    print(config.divider())
    print(config.wrap_text(t("help.body")))
    print(config.divider())


# Mode bantuan terpisah untuk auto-cd (cegah kebingungan nama command)
def handle_ai(arg):
    """Perintah AI Pemandu (RydzAgent): ai <tanya> | ai tour | ai error."""
    arg = arg.strip()
    if not arg:
        print(t("ai.usage_help"))
        return
    low = arg.lower()
    if low == "tour":
        ai.tour()
    elif low == "error":
        ai.explain_last_error()
    else:
        ai.chat(arg)


def handle_custom_ls(arg):
    args = arg.split() if arg else []
    commands.custom_ls(*args)


def text_generator():
    while True:
        config.clear_screen()
        print(config.divider())
        print(t("tg.title"))
        print(config.divider() + "\n")
        print(t("tg.exit") + "\n")
        try:
            text = input(t("tg.input_text"))
            if text.lower() == "exit":
                break
            jumlah = int(input(t("tg.input_count")))
            for i in range(1, jumlah + 1):
                print(f"{i}. {text}")
            input(t("tg.press_enter"))
        except ValueError:
            print(t("tg.count_error"))
            input(t("tg.press_enter"))
        except KeyboardInterrupt:
            print("\n^C")
            break


def handle_sudo(single_command):
    """Menangani semua varian perintah sudo."""
    # 1. Ganti Password Sudo (sudo newpass)
    if single_command == "sudo newpass":
        try:
            old_pass = getpass.getpass(t("sudo.old_pass"))
            if old_pass == config.CUSTOM_SUDO_PASS:
                new_pass = getpass.getpass(t("sudo.new_pass"))
                confirm_pass = getpass.getpass(t("sudo.confirm_pass"))
                if new_pass == confirm_pass:
                    if new_pass.strip():
                        config.CUSTOM_SUDO_PASS = new_pass.strip()
                        with open(config.PASS_FILE_PATH, "w") as f:
                            f.write(config.CUSTOM_SUDO_PASS)
                        print(t("sudo.changed"))
                    else:
                        print(t("sudo.empty_pass"))
                else:
                    print(t("sudo.confirm_mismatch"))
            else:
                print(t("sudo.wrong_old"))
        except KeyboardInterrupt:
            print("\n^C")
            config.reset_terminal()
        return True

    # 2. Edit File Terproteksi (sudo edit <file>)
    elif single_command.startswith("sudo edit"):
        target_file = single_command.replace("sudo edit ", "", 1).strip()
        if target_file:
            try:
                pass_input = getpass.getpass(t("sudo.edit_pass"))
                if pass_input == config.CUSTOM_SUDO_PASS:
                    print(t("sudo.access_granted"))
                    config.run_system_cmd(f'nano "{target_file}"')
                else:
                    print(t("sudo.access_denied"))
            except KeyboardInterrupt:
                print("\n^C")
                config.reset_terminal()
        else:
            print(t("sudo.usage_edit"))
        return True

    # 3. Perilaku Sudo Biasa
    is_real_linux = shutil.which("sudo") and os.path.exists("/usr/bin/sudo")

    if is_real_linux:
        config.run_system_cmd(single_command)
    else:
        try:
            sudo_pass = getpass.getpass(t("sudo.password_prompt"))
            if sudo_pass == config.CUSTOM_SUDO_PASS:
                print("\n[sudo] password accepted.")
                if single_command == "sudo apt update":
                    repos = [
                        "Get:1 http://security.debian.org/debian-security stable-security InRelease",
                        "Get:2 http://deb.debian.org/debian stable InRelease",
                        "Get:3 http://deb.debian.org/debian stable-updates InRelease",
                    ]
                    for repo in repos:
                        print(repo)
                        time.sleep(0.4)
                    for i in range(100):
                        print(
                            f"Reading package lists... {i + 1}%",
                            end="\r",
                        )
                        time.sleep(0.01)
                    print("\nAll packages are up to date.")
                else:
                    cmd_tanpa_sudo = single_command.replace("sudo ", "", 1)
                    print(t("sudo.exec_fake", cmd=cmd_tanpa_sudo))
                    config.run_system_cmd(cmd_tanpa_sudo)
            else:
                print("sudo: 1 incorrect password attempt")
        except KeyboardInterrupt:
            print("\n^C")
            config.reset_terminal()
    return True


# Builtin yang boleh dipipe (agar `help | grep`, `history | grep`, dst. jalan)
PIPE_BUILTINS = {
    "help", "?", "list", "history", "echo", "alias", "aliases",
    "tree", "pwd", "cat", "calc", "ascii", "weather", "ai", "lang",
}


def _run_builtin_capture(seg):
    """Jalankan segmen sebagai builtin & kembalikan stdout-nya (atan None)."""
    parts = seg.split(maxsplit=1)
    cmd = parts[0] if parts else ""
    if cmd not in PIPE_BUILTINS:
        return None
    old_stdout = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        handle_command(seg)
    finally:
        sys.stdout = old_stdout
    return buf.getvalue()


def handle_command(single_command):
    """Menangani satu perintah (setelah dipisah dari &&/|)."""

    # --- PIPE SUPPORT ---
    if pipe.has_pipe(single_command) and len(pipe.split_pipes(single_command)) > 1:
        pipe.execute_pipeline(single_command, builtin_runner=_run_builtin_capture)
        return

    # --- REDIRECT SUPPORT (> dan >>) ---
    redirect_file = None
    redirect_append = False
    for op in [">>", "1>>", ">", "1>"]:
        idx = single_command.find(op)
        if idx == -1:
            continue
        # Abaikan 2> (redirect stderr) — bukan bagian dari fitur ini
        if op == ">" and idx > 0 and single_command[idx - 1].isdigit():
            continue
        if op in (">>", "1>>"):
            redirect_append = True
        else:
            redirect_append = False
        right = single_command[idx + len(op):].strip()
        # Ambil token pertama setelah operator sebagai nama file
        if right:
            first_token = right.split()[0] if right.split() else right
            redirect_file = first_token
            single_command = single_command[:idx].strip()
            break

    import io

    if redirect_file:
        old_stdout = sys.stdout
        buffer = io.StringIO()
        sys.stdout = buffer
        try:
            handle_command(single_command)
        finally:
            sys.stdout = old_stdout
        mode = "a" if redirect_append else "w"
        try:
            with open(redirect_file, mode) as f:
                f.write(buffer.getvalue())
        except Exception as e:
            print(t("redirect.failed", e=e), file=old_stdout)
        return

    parts = single_command.split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    # --- CEK RYDZZ ALIAS DARI .rydzzrc ---
    rydzz_alias = config.CONFIG.get("rydzz_aliases", {}).get(cmd)
    if rydzz_alias:
        alias_cmd = f"{rydzz_alias} {arg}".strip()
        handle_command(alias_cmd)
        return

    # --- CEK ALIAS DARI ~/.bashrc ---
    bashrc_alias = config.USER_ALIASES.get(cmd)
    if bashrc_alias:
        alias_cmd = f"{bashrc_alias} {arg}".strip()
        handle_command(alias_cmd)
        return

    # --- TAMPILAN LS KHUSUS ---
    if cmd in ["ls", "dir"]:
        handle_custom_ls(arg)

    elif cmd == "pwd":
        print(os.getcwd())

    # --- TREE ---
    elif cmd == "tree":
        target = "."
        depth = 0
        args = arg.split() if arg else []
        targs = []
        for a in args:
            if a == "-L":
                continue
            if a.isdigit():
                depth = int(a)
            elif a.startswith("-L"):
                depth = int(a[2:]) if a[2:].isdigit() else 0
            else:
                targs.append(a)
        if targs:
            target = targs[0]
        commands.custom_tree(target, depth=depth, _level=0)

    elif cmd == "mv":
        args = arg.split(maxsplit=1)
        if len(args) == 2:
            src, dst = args[0], args[1]
            if os.path.exists(src):
                if dst.endswith("/") and not os.path.exists(dst):
                    print(t("err.mv_dest_dir", dst=dst))
                    return
                try:
                    shutil.move(src, dst)
                    if os.path.isdir(dst):
                        print(t("ok.mv_dir", src=src, dst=dst))
                    else:
                        print(t("ok.mv_rename", src=src, dst=dst))
                except Exception as e:
                    print(t("err.mv_fail", e=e))
                    return
            else:
                print(t("err.src_not_found", src=src))
                return
        else:
            print(t("usage.mv"))

    elif cmd == "cp":
        args = arg.split(maxsplit=1)
        if len(args) == 2:
            src, dst = args[0], args[1]
            if os.path.exists(src):
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    print(t("ok.cp", src=src, dst=dst))
                except Exception as e:
                    print(t("err.cp_fail", e=e))
                    return
            else:
                print(t("err.src_not_found", src=src))
                return
        else:
            print(t("usage.cp"))

    elif cmd == "cd":
        if arg:
            try:
                os.chdir(arg)
            except FileNotFoundError:
                print(t("err.cd_not_found", arg=arg))
                return
            except NotADirectoryError:
                print(t("err.cd_not_dir", arg=arg))
                return
            except Exception as e:
                print(t("err.cd_fail", e=e))
                return
        else:
            os.chdir(config.CUSTOM_HOME)

    elif cmd == "mkdir":
        if arg:
            try:
                os.mkdir(arg)
                print(t("ok.mkdir", arg=arg))
            except FileExistsError:
                print(t("err.mkdir_exists", arg=arg))
            except Exception as e:
                print(t("err.mkdir_fail", e=e))
                return
        else:
            print(t("usage.mkdir"))

    elif cmd in ["rm", "hapus"]:
        if arg:
            if os.path.exists(arg):
                try:
                    if os.path.isdir(arg):
                        shutil.rmtree(arg)
                        print(t("ok.rm_dir", arg=arg))
                    else:
                        os.remove(arg)
                        print(t("ok.rm_file", arg=arg))
                except Exception as e:
                    print(t("err.rm_fail", e=e))
                    return
            else:
                print(t("err.not_found_generic"))
                return
        else:
            print(t("usage.rm"))

    elif cmd == "touch":
        if arg:
            try:
                open(arg, "a").close()
                print(t("ok.touch", arg=arg))
            except Exception as e:
                print(t("err.touch_fail", e=e))
        else:
            print(t("usage.touch"))

    elif cmd == "cat":
        if arg:
            if os.path.exists(arg) and os.path.isfile(arg):
                if config.is_protected(arg):
                    print(t("err.protected_access"))
                else:
                    try:
                        with open(arg, "r") as f:
                            print(f.read())
                    except Exception as e:
                        print(t("err.cat_read", e=e))
            else:
                print(t("err.cat_not_found", arg=arg))
        else:
            print(t("usage.cat"))

    elif cmd == "nano":
        if arg:
            if config.is_protected(arg):
                print(t("err.protected_access"))
            else:
                config.run_system_cmd(f'nano "{arg}"')
        else:
            print(t("usage.nano"))

    elif cmd == "history":
        args = arg.split()
        if "-c" in args or "--clear" in args:
            config.COMMAND_HISTORY.clear()
            config._flush_history_buffer()
            try:
                readline.clear_history()
            except Exception:
                pass
            print(
                t(
                    "history.cleared",
                    green=config.GREEN_NEON,
                    reset=config.RESET,
                )
            )
            return
        history = config.COMMAND_HISTORY
        if not history:
            print(t("history.empty"))
            return
        total = len(history)
        print(t("history.title", total=total))
        last = total - 1
        for i, h_cmd in enumerate(history):
            line = f"  {config.DIM}{i + 1:>4}{config.RESET}  {h_cmd}"
            if i == last:
                line = f"  {config.DIM}{i + 1:>4}{config.RESET}  {config.CYAN}{h_cmd}{config.RESET}"
            print(line)
        print(t("history.hint"))

    elif cmd == "echo":
        print(arg)

    elif cmd in ["python", "py", "PY"]:
        if arg:
            config.run_system_cmd(f'python3 "{arg}"')
        else:
            print(t("usage.python"))

    elif cmd in ["pip", "pip3"]:
        config.run_system_cmd(single_command)

    elif cmd == "node":
        if arg:
            config.run_system_cmd(f'node "{arg}"')
        else:
            print(t("usage.node"))

    # --- SHORTCUT GIT (dicek sebelum passthrough git) ---
    elif cmd in ["gs", "ga", "gl", "gb", "gd", "gp", "gpl", "gst", "gc", "gco", "gclone"]:
        if not commands.run_git_shortcut(cmd, arg):
            print(t("err.cmd_not_found", cmd=cmd))

    elif cmd in ["gh", "git"]:
        # Pakai HOME asli agar kredensial gh/git di terminal utama terbawa
        config.run_system_cmd_real_home(single_command)

    elif cmd in [
        "curl", "wget", "ssh", "sshd", "ping", "zip", "unzip", "tar",
        "grep", "find", "df", "free", "ps", "neofetch", "fastfetch",
    ]:
        config.run_system_cmd(single_command)

    elif cmd == "whoami":
        config.run_system_cmd("whoami")

    elif cmd in ["passwd", "passw"]:
        config.run_system_cmd("passwd")

    elif cmd == "source":
        if arg in ("~/.bashrc", os.path.expanduser("~/.bashrc")):
            config.USER_ALIASES = config.load_bashrc_aliases()
            completions.refresh()
            print(t("source.ok_bashrc"))
        elif arg in ("~/.rydzzrc", config.RYDZZRC_PATH):
            config.load_rydzzrc()
            completions.refresh()
            print(t("source.ok_rydzzrc"))
        else:
            print(t("usage.source"))

    elif single_command.startswith("sudo"):
        handle_sudo(single_command)

    elif cmd in ["alias", "aliases"]:
        merged = {}
        merged.update(config.CONFIG.get("rydzz_aliases", {}))
        merged.update(config.USER_ALIASES)
        if merged:
            print(t("alias.title"))
            for k, v in merged.items():
                print(f"  {k} -> '{v}'")
        else:
            print(t("alias.empty"))

    elif cmd in ["list", "help", "?"]:
        show_help()

    elif cmd == "clear":
        config.clear_screen()

    elif cmd == "htop":
        config.run_system_cmd("htop")

    elif cmd == "TG":
        text_generator()

    elif cmd == "dl":
        handle_dl(arg)

    elif cmd == "qr":
        handle_qr(arg)

    elif cmd == "ascii":
        handle_ascii(arg)

    elif cmd in ("wclone", "wcode"):
        webclone.clone_site(arg)

    elif cmd in ("ai", "rydza"):
        handle_ai(arg)

    elif cmd == "timer":
        gadgets.timer(arg)

    elif cmd == "stopwatch":
        gadgets.stopwatch(arg)

    elif cmd == "calc":
        gadgets.calc(arg)

    elif cmd == "weather":
        gadgets.weather(arg)

    elif cmd == "lang":
        handle_lang(arg)

    elif cmd == "trash":
        kits.trash(arg)

    elif cmd in ("bk", "backup"):
        kits.backup(arg)

    elif cmd == "hash":
        kits.hashit(arg)

    elif cmd == "freq":
        kits.freq(arg)

    elif cmd == "clip":
        kits.clip(arg)

    elif cmd == "todo":
        kits.todo(arg)

    elif cmd == "serve":
        kits.serve(arg)

    elif cmd == "pick":
        kits.pick(arg)

    elif cmd == "task":
        snippets.task(arg, runner=handle_command)

    elif cmd == "exit":
        sys.exit()

    elif cmd == "restart":
        config.clear_screen()
        os.environ.pop("RYDZZ_INIT", None)
        os.environ.pop("RYDZZ_LEVEL", None)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cli_path = os.path.join(repo_root, "CLI.py")
        if os.name == "posix":
            os.execv(sys.executable, [sys.executable, cli_path])
        else:
            subprocess.Popen([sys.executable, cli_path])
            sys.exit()

    else:
        # --- AUTO-CDF (fallback) ---
        if config.CONFIG.get("auto_cd", True):
            candidate = arg if arg else cmd
            cand_path = os.path.expanduser(candidate)
            if os.path.isdir(cand_path):
                try:
                    os.chdir(cand_path)
                    return
                except Exception:
                    pass
            if os.path.isdir(cmd):
                try:
                    os.chdir(cmd)
                    return
                except Exception:
                    pass

        if shutil.which(cmd):
            config.run_system_cmd(single_command)
        else:
            msg = t("err.cmd_not_found", cmd=cmd)
            suggestions = difflib.get_close_matches(
                cmd, completions.build_command_list(), n=3, cutoff=0.55
            )
            if suggestions:
                msg += t("err.suggest", list=", ".join(suggestions))
            print(msg)
            config.LAST_CMD = single_command
            config.LAST_ERROR = msg


def handle_lang(arg):
    """Perintah multi-bahasa: lang | lang list | lang -C <kode> | lang set <kode>."""
    args = arg.split() if arg else []

    if not args:
        print(t("lang.current", name=i18n.language_name(), code=i18n.get_language()))
        print(t("lang.usage_help"))
        print(t("lang.usage_hint"))
        return

    action = args[0].lower()
    rest = args[1:]

    # lang list | lang -l
    if action in ("list", "-l", "--list"):
        languages = i18n.list_languages()
        if not languages:
            print(t("lang.cancelled"))
            return
        print(t("lang.list_title"))
        for code, name in languages:
            active = " *" if code == i18n.get_language() else "  "
            print(f"{active} {code:<6} {name}")
        return

    # lang -C <kode> / lang set <kode> / ganti bahasa
    if action in ("-c", "-C", "--change", "set", "change"):
        if rest:
            code = rest[0].strip().lower()
            if not config.apply_language(code):
                print(t("lang.not_found", code=code))
                print(t("lang.usage_hint"))
                return
            print(
                t(
                    "lang.changed",
                    green=config.GREEN_NEON,
                    reset=config.RESET,
                    name=i18n.language_name(),
                    code=i18n.get_language(),
                )
            )
            return

        # Picker interaktif
        languages = i18n.list_languages()
        if not languages:
            return
        print(t("lang.list_title"))
        for i, (code, name) in enumerate(languages, 1):
            active = " *" if code == i18n.get_language() else "  "
            print(f"  {i}. {code:<6} {name}{active}")
        try:
            choice = input(t("lang.choose")).strip()
        except (KeyboardInterrupt, EOFError):
            print()
            return
        if choice == "0" or not choice:
            print(t("lang.cancelled"))
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(languages)):
            print(t("lang.invalid_choice"))
            return
        code = languages[int(choice) - 1][0]
        config.apply_language(code)
        print(
            t(
                "lang.changed",
                green=config.GREEN_NEON,
                reset=config.RESET,
                name=i18n.language_name(),
                code=i18n.get_language(),
            )
        )
        return

    print(t("lang.current", name=i18n.language_name(), code=i18n.get_language()))
    print(config.wrap_text(t("lang.usage_help")))
    print(config.wrap_text(t("lang.usage_hint")))


def main():
    # Setup environment
    os.chdir(config.CUSTOM_HOME)

    # Muat alias & konfigurasi
    config.USER_ALIASES = config.load_bashrc_aliases()
    config.load_rydzzrc()

    # Muat riwayat permanen antar-sesi
    config.load_history()

    # Setup readline / tab completion
    completions.setup_readline()
    completions.setup_readline_history()

    # Tampilkan banner (kecuali dimatikan via .rydzzrc)
    if config.CONFIG.get("banner", True) and "RYDZZ_INIT" not in os.environ:
        os.environ["RYDZZ_INIT"] = "1"
        show_banner()

    # Jalankan init command dari .rydzzrc
    init_cmd = config.CONFIG.get("init_command")
    if init_cmd:
        print(f"$ {init_cmd}")
        handle_command(init_cmd)

    while True:
        cwd = os.path.basename(os.getcwd()) or os.getcwd()
        git_info = config.get_git_branch()
        level_str = f" L{config.SHELL_LEVEL}" if config.SHELL_LEVEL > 1 else ""
        prompt_color = config.get_prompt_color()

        try:
            prompt = config.wrap_ansi(
                f"{prompt_color}RydzzShell{level_str}:[{cwd}]{git_info}$ "
                f"{config.RESET}"
            )
            raw_input = input(prompt).strip()

            if not raw_input:
                continue

            config.append_history(raw_input)

            # --- FITUR DOUBLE COMMAND (&&) ---
            commands_seq = [c.strip() for c in raw_input.split("&&")]

            for single_command in commands_seq:
                if not single_command:
                    continue
                capturer = _OutputCapturer()
                sys.stdout = capturer
                try:
                    handle_command(single_command)
                finally:
                    sys.stdout = capturer.real
                output = capturer.buf.getvalue()
                if i18n.is_error_output(output):
                    config.LAST_CMD = single_command
                    config.LAST_ERROR = output.strip()[:2000]

        except KeyboardInterrupt:
            print("\n^C")
            config.reset_terminal()
            continue
        except EOFError:
            print(t("eof.exit_hint"))
            continue
