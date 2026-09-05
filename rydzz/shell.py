import getpass
import os
import shutil
import sys
import time

try:
    import readline
except ImportError:
    readline = None

from . import commands, completions, config, pipe, tools


def handle_dl(arg):
    args = arg.split() if arg else []
    if not args:
        print("Guna: dl <url> [-q] | dl list | dl update")
        return

    if args[0] == "list":
        tools.list_downloads()
        return
    if args[0] == "update":
        print("Meng-update yt-dlp...")
        tools.update_ytdlp()
        return

    url = args[0]
    audio_only = "-q" in args or "--audio" in args
    dry_run = "--dry" in args or "-s" in args
    tools.download_video(url, audio_only=audio_only, dry_run=dry_run)


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
        print(
            "Guna: ascii enc|-x|-b \"teks\"  |  ascii dec [-x|-b] \"angka ...\""
        )
        return

    mode = args[0]
    base, label, flag_remaining = tools._parse_ascii_flags(args[1:])
    if not flag_remaining:
        print(f"ASCII mode butuh input. Basis: {label}")
        return

    input_text = " ".join(flag_remaining).strip("\"'")

    if mode in ("enc", "encode"):
        print(tools.ascii_encode(input_text, base))
    else:
        print(tools.ascii_decode(input_text, base))


def show_banner():
    """Menampilkan Tampilan Awal / ASCII Art"""
    config.clear_screen()
    banner = f"""{config.GREEN_NEON}
  _____ydzz   _____ _          _ 
 |  __ \\     / ____| |        | |
 | |__) |   | (___ | |__   ___| |
 |  _  /     \\___ \\| '_ \\ / _ \\ |
 | | \\ \\ _   ____) | | | |  __/ |
 |_|  \\_(_) |_____/|_| |_|\\___|_|
{config.CYAN}    --- Custom Interactive Shell v2.0 ---{config.RESET}
{config.YELLOW}  Ketik 'help' atau '?' untuk daftar perintah.{config.RESET}
"""
    print(banner)


def show_help():
    print("=" * 65)
    print("                  DAFTAR PERINTAH RYDZZ SHELL")
    print("=" * 65)
    print("• ls [path] [-a] [-l]      - Lihat isi folder (-a hidden, -l detail)")
    print("• tree [path] [-L n]       - Tampilkan struktur folder dalam pohon")
    print("• cd [folder]              - Pindah folder (cd doang = balik ke Home)")
    print("• pwd                      - Menampilkan path lokasi direktori aktif")
    print("• mkdir <folder>           - Membuat folder baru")
    print("• rm <file/folder>         - Menghapus file atau folder")
    print("• mv <asal> <tujuan>       - Pindah atau rename file/folder")
    print("• cp <asal> <tujuan>       - Menyalin file atau folder")
    print("• cat / nano <file>        - Baca / edit file teks")
    print("• touch <file>             - Membuat/update timestamp file")
    print("• echo <teks>              - Mencetak teks")
    print("• history                  - Melihat riwayat perintah")
    print("• python / py <file.py>    - Menjalankan script Python")
    print("• pip / node               - Pipeline Python & Node")
    print("• git / curl / wget        - Download & Network tools")
    print("• ssh / sshd / ping        - Remote & Connectivity")
    print("• whoami / passwd          - Informasi user & ubah password")
    print("• df / free / ps / htop    - Informasi memori & sistem")
    print("• neofetch / fastfetch     - Tampilan sistem aesthetic")
    print("• sudo edit <file>         - Akses terproteksi untuk edit file rahasia")
    print("• sudo newpass             - Mengubah password Sudo khusus secara permanen")
    print("• source ~/.bashrc         - Reload alias dari ~/.bashrc")
    print("• alias / aliases          - Menampilkan alias yang dibaca dari ~/.bashrc")
    print("• TG                       - Membuka Text Generator")
    print("• dl <url>                 - Unduh video/lagu ke download/rydzzMedia")
    print("    dl <url> -q            -   audio saja (mp3)")
    print("    dl list                 -   lihat file ter-unduh")
    print("    dl update               -   update yt-dlp")
    print("• qr <teks>                - Tampilkan QR di terminal")
    print("    qr <teks> -o file.png  -   simpan QR (png/svg)")
    print(
        "• ascii enc|dec [-x|-b]     - Konversi ASCII (desimal/hex/biner)"
    )
    print("    ascii enc \"kata\"          -   kata → kode")
    print("    ascii dec \"104 101 ...\"   -   kode → kata")
    print("• clear                    - Membersihkan layar")
    print("• exit                     - Keluar dari shell")
    print("• <cmd1> && <cmd2>         - Menjalankan 2 perintah sekaligus")
    print("• cmd1 | cmd2              - Pipe output cmd1 ke cmd2")
    print("")
    print("--- SHORTCUT GIT ---")
    print("• gs=status ga=add gl=log gb=branch gd=diff")
    print("• gp=push gpl=pull gst=stash gc=<msg> gco=<branch> gclone=<url>")
    print("")
    print("--- FITUR LANJUTAN ---")
    print("• Tab completion            - Lengkapi command/file otomatis (Tab)")
    print("• Auto-cd: ketik nama folder - Otomatis pindah ke folder itu")
    print("• ~/.rydzzrc                - Konfigurasi prompt, banner, hidden, init")
    print("=" * 65)


# Mode bantuan terpisah untuk auto-cd (cegah kebingungan nama command)
def handle_custom_ls(arg):
    args = arg.split() if arg else []
    commands.custom_ls(*args)


def text_generator():
    while True:
        config.clear_screen()
        print("=" * 42)
        print("         Text Generator")
        print("=" * 42 + "\n")
        print("Ketik 'exit' pada teks untuk keluar!\n")
        try:
            text = input("Masukkan Kata: ")
            if text.lower() == "exit":
                break
            jumlah = int(input("Masukkan Jumlah: "))
            for i in range(1, jumlah + 1):
                print(f"{i}. {text}")
            input("\nTekan Enter Untuk Lanjut...")
        except ValueError:
            print("Jumlah Harus Berupa Angka!!")
            input("\nTekan Enter Untuk Lanjut...")
        except KeyboardInterrupt:
            print("\n^C")
            break


def handle_sudo(single_command):
    """Menangani semua varian perintah sudo."""
    # 1. Ganti Password Sudo (sudo newpass)
    if single_command == "sudo newpass":
        try:
            old_pass = getpass.getpass("Masukkan Sudo Password Lama: ")
            if old_pass == config.CUSTOM_SUDO_PASS:
                new_pass = getpass.getpass("Masukkan Sudo Password Baru: ")
                confirm_pass = getpass.getpass("Konfirmasi Password Baru: ")
                if new_pass == confirm_pass:
                    if new_pass.strip():
                        config.CUSTOM_SUDO_PASS = new_pass.strip()
                        with open(config.PASS_FILE_PATH, "w") as f:
                            f.write(config.CUSTOM_SUDO_PASS)
                        print("\n[SUCCESS] Sudo Password berhasil diubah!")
                    else:
                        print("\n[ERROR] Password tidak boleh kosong!")
                else:
                    print("\n[ERROR] Konfirmasi password tidak cocok!")
            else:
                print("\n[ERROR] Password lama salah!")
        except KeyboardInterrupt:
            print("\n^C")
            config.reset_terminal()
        return True

    # 2. Edit File Terproteksi (sudo edit <file>)
    elif single_command.startswith("sudo edit"):
        target_file = single_command.replace("sudo edit ", "", 1).strip()
        if target_file:
            try:
                pass_input = getpass.getpass("Masukkan Custom Sudo Password: ")
                if pass_input == config.CUSTOM_SUDO_PASS:
                    print("\nAkses Diterima!")
                    config.run_system_cmd(f'nano "{target_file}"')
                else:
                    print("\nAkses Ditolak: Password Salah!")
            except KeyboardInterrupt:
                print("\n^C")
                config.reset_terminal()
        else:
            print("Guna: sudo edit <nama_file>")
        return True

    # 3. Perilaku Sudo Biasa
    is_real_linux = shutil.which("sudo") and os.path.exists("/usr/bin/sudo")

    if is_real_linux:
        config.run_system_cmd(single_command)
    else:
        try:
            sudo_pass = getpass.getpass("Rydzz Password: ")
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
                    print(f"Executing with fake-root: {cmd_tanpa_sudo}")
                    config.run_system_cmd(cmd_tanpa_sudo)
            else:
                print("sudo: 1 incorrect password attempt")
        except KeyboardInterrupt:
            print("\n^C")
            config.reset_terminal()
    return True


def handle_command(single_command):
    """Menangani satu perintah (setelah dipisah dari &&/|)."""

    # --- PIPE SUPPORT ---
    if pipe.has_pipe(single_command) and len(pipe.split_pipes(single_command)) > 1:
        pipe.execute_pipeline(single_command)
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
            print(f"Redirect gagal: {e}", file=old_stdout)
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
                    print(f"Error: Folder tujuan '{dst}' tidak ditemukan!")
                    return
                try:
                    shutil.move(src, dst)
                    if os.path.isdir(dst):
                        print(f"'{src}' berhasil dipindahkan ke folder '{dst}'.")
                    else:
                        print(f"'{src}' berhasil di-rename menjadi '{dst}'.")
                except Exception as e:
                    print(f"Gagal memindahkan: {e}")
                    return
            else:
                print(f"File/Folder asal '{src}' tidak ditemukan!")
                return
        else:
            print("Guna: mv <asal> <tujuan>")

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
                    print(f"'{src}' berhasil disalin ke '{dst}'.")
                except Exception as e:
                    print(f"Gagal menyalin: {e}")
                    return
            else:
                print(f"File/Folder asal '{src}' tidak ditemukan!")
                return
        else:
            print("Guna: cp <asal> <tujuan>")

    elif cmd == "cd":
        if arg:
            try:
                os.chdir(arg)
            except FileNotFoundError:
                print(f"Folder '{arg}' tidak ditemukan!")
                return
            except NotADirectoryError:
                print(f"'{arg}' bukan sebuah folder!")
                return
            except Exception as e:
                print(f"Gagal pindah folder: {e}")
                return
        else:
            os.chdir(config.CUSTOM_HOME)

    elif cmd == "mkdir":
        if arg:
            try:
                os.mkdir(arg)
                print(f"Folder '{arg}' berhasil dibuat.")
            except FileExistsError:
                print(f"Folder '{arg}' sudah ada!")
            except Exception as e:
                print(f"Gagal membuat folder: {e}")
                return
        else:
            print("Guna: mkdir <nama_folder>")

    elif cmd in ["rm", "hapus"]:
        if arg:
            if os.path.exists(arg):
                try:
                    if os.path.isdir(arg):
                        shutil.rmtree(arg)
                        print(f"Folder '{arg}' berhasil dihapus.")
                    else:
                        os.remove(arg)
                        print(f"File '{arg}' berhasil dihapus.")
                except Exception as e:
                    print(f"Gagal menghapus: {e}")
                    return
            else:
                print("File/Folder tidak ditemukan!")
                return
        else:
            print("Guna: rm <nama_file_atau_folder>")

    elif cmd == "touch":
        if arg:
            try:
                open(arg, "a").close()
                print(f"File '{arg}' berhasil dibuat/diperbarui.")
            except Exception as e:
                print(f"Gagal membuat file: {e}")
        else:
            print("Guna: touch <nama_file>")

    elif cmd == "cat":
        if arg:
            if os.path.exists(arg) and os.path.isfile(arg):
                if config.is_protected(arg):
                    print(
                        "Akses Ditolak: Gunakan 'sudo edit' untuk mengakses file terproteksi."
                    )
                else:
                    try:
                        with open(arg, "r") as f:
                            print(f.read())
                    except Exception as e:
                        print(f"Gagal membaca file: {e}")
            else:
                print(f"File '{arg}' tidak ditemukan!")
        else:
            print("Guna: cat <nama_file>")

    elif cmd == "nano":
        if arg:
            if config.is_protected(arg):
                print(
                    "Akses Ditolak: Gunakan 'sudo edit' untuk mengakses file terproteksi."
                )
            else:
                config.run_system_cmd(f'nano "{arg}"')
        else:
            print("Guna: nano <nama_file>")

    elif cmd == "history":
        print("Daftar Riwayat Perintah:")
        for i, h_cmd in enumerate(config.COMMAND_HISTORY, 1):
            print(f"  {i}  {h_cmd}")

    elif cmd == "echo":
        print(arg)

    elif cmd in ["python", "py", "PY"]:
        if arg:
            config.run_system_cmd(f'python3 "{arg}"')
        else:
            print("Guna: python <nama_file.py>")

    elif cmd in ["pip", "pip3"]:
        config.run_system_cmd(single_command)

    elif cmd == "node":
        if arg:
            config.run_system_cmd(f'node "{arg}"')
        else:
            print("Guna: node <nama_file.js>")

    # --- SHORTCUT GIT (dicek sebelum passthrough git) ---
    elif cmd in ["gs", "ga", "gl", "gb", "gd", "gp", "gpl", "gst", "gc", "gco", "gclone"]:
        if not commands.run_git_shortcut(cmd, arg):
            print(f"Command Not Found: {cmd}")

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
            print("Berhasil meng-update alias dari ~/.bashrc!")
        elif arg in ("~/.rydzzrc", config.RYDZZRC_PATH):
            config.load_rydzzrc()
            print("Berhasil meng-update konfigurasi dari ~/.rydzzrc!")
        else:
            print("Guna: source ~/.bashrc atau source ~/.rydzzrc")

    elif single_command.startswith("sudo"):
        handle_sudo(single_command)

    elif cmd in ["alias", "aliases"]:
        merged = {}
        merged.update(config.CONFIG.get("rydzz_aliases", {}))
        merged.update(config.USER_ALIASES)
        if merged:
            print("Daftar Alias:")
            for k, v in merged.items():
                print(f"  {k} -> '{v}'")
        else:
            print("Tidak ada alias ditemukan.")

    elif cmd in ["list", "help", "?"]:
        show_help()

    elif cmd == "clear":
        config.clear_screen()

    elif cmd == "htop":
        config.run_system_cmd("htop")

    elif cmd == "print":
        print("kocak")

    elif cmd == "TG":
        text_generator()

    elif cmd == "dl":
        handle_dl(arg)

    elif cmd == "qr":
        handle_qr(arg)

    elif cmd == "ascii":
        handle_ascii(arg)

    elif cmd == "exit":
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
            print(f"Command Not Found: {cmd}")


def main():
    # Setup environment
    os.chdir(config.CUSTOM_HOME)

    # Muat alias & konfigurasi
    config.USER_ALIASES = config.load_bashrc_aliases()
    config.load_rydzzrc()

    # Setup readline / tab completion
    completions.setup_readline()

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
            prompt = (
                f"{prompt_color}RydzzShell{level_str}:[{cwd}]{git_info}$ "
                f"{config.RESET}"
            )
            raw_input = input(prompt).strip()

            if not raw_input:
                continue

            config.COMMAND_HISTORY.append(raw_input)

            # --- FITUR DOUBLE COMMAND (&&) ---
            commands_seq = [c.strip() for c in raw_input.split("&&")]

            for single_command in commands_seq:
                if not single_command:
                    continue
                handle_command(single_command)

        except KeyboardInterrupt:
            print("\n^C")
            config.reset_terminal()
            continue
        except EOFError:
            print("\nGunakan perintah 'exit' untuk keluar.")
            continue
