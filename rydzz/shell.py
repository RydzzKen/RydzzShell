import difflib
import getpass
import io
import os
import random
import shutil
import subprocess
import sys
import time

try:
    import readline
except ImportError:
    readline = None

from . import ai, commands, completions, config, deploy, gadgets, i18n, kits, pipe, snippets, tools, webclone
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


def handle_keystore(arg):
    args = arg.split() if arg else []
    if not args or args[0] != "create":
        print(t("keystore.usage"))
        return
    if len(args) < 3:
        print(t("keystore.usage"))
        return
    name = args[1]
    alias = args[2]
    path = args[3] if len(args) > 3 else None
    tools.create_keystore(name, alias, path)


def handle_deploy(arg):
    args = arg.split() if arg else []
    if not args:
        print(t("deploy.usage"))
        return
    platform = args[0].lower()
    rest = " ".join(args[1:])
    if platform == "vercel":
        deploy.vercel_deploy(rest)
    else:
        print(t("deploy.platform_unknown", plat=platform))
        print(t("deploy.usage"))


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


_FANCY_STYLES = {
    # style: (A-Z base, a-z base, 0-9 base or None)
    "bold": (0x1D400, 0x1D41A, 0x1D7CE),        # math bold
    "italic": (0x1D434, 0x1D44E, None),         # math italic (no digits)
    "script": (0x1D49C, 0x1D4B6, None),         # math script (no digits)
    "fraktur": (0x1D504, 0x1D51E, None),        # math fraktur (no digits)
    "double": (0x1D538, 0x1D552, 0x1D7D8),      # double-struck
    "sans": (0x1D5A0, 0x1D5BA, 0x1D7E2),        # sans-serif
    "mono": (0x1D670, 0x1D68A, 0x1D7F6),        # monospace
    "circled": (0x1F150, 0x24D0, None),         # circled A-Z/a-z (digits handled separately)
    "squared": (0x1F130, 0x24B6, None),         # squared (no digit mapping)
    "fullwidth": (0xFF21, 0xFF41, 0xFF10),      # full-width
}

_CIRCLED_DIGITS = ["0", "\u2460", "\u2461", "\u2462", "\u2463", "\u2464",
                   "\u2465", "\u2466", "\u2467", "\u2468"]


def _fancy_convert(text, style):
    """Konversi teks ke gaya Unicode. Karakter tanpa mapping dibiarkan asli."""
    if style not in _FANCY_STYLES or not text:
        return text
    ua, la, num = _FANCY_STYLES[style]
    out = []
    for ch in text:
        code = ord(ch)
        if "A" <= ch <= "Z":
            out.append(chr(ua + (code - 0x41)))
        elif "a" <= ch <= "z":
            out.append(chr(la + (code - 0x61)))
        elif "0" <= ch <= "9":
            if style == "circled":
                out.append(_CIRCLED_DIGITS[int(ch)])
            elif num is not None:
                out.append(chr(num + (code - 0x30)))
            else:
                out.append(ch)
        else:
            out.append(ch)
    return "".join(out)


_BLOCK_LETTERS = {
    "A": [" ### ", "#   #", "#####", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#### ", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#### ", "#    ", "#####"],
    "F": ["#####", "#    ", "#### ", "#    ", "#    "],
    "G": [" ####", "#    ", "#  ##", "#   #", " ####"],
    "H": ["#   #", "#   #", "#####", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["#####", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "###  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#### ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#### ", "#  # ", "#   #"],
    "S": [" ####", "#    ", " ### ", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "# # #", "## ##", "#   #"],
    "X": ["#   #", " # # ", "  #  ", " # # ", "#   #"],
    "Y": ["#   #", " # # ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "   # ", "  #  ", " #   ", "#####"],
    "0": [" ### ", "#   #", "#   #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "#####"],
    "2": [" ### ", "#   #", "   # ", "  #  ", "#####"],
    "3": ["#### ", "    #", " ### ", "    #", "#### "],
    "4": ["   # ", "  ## ", " # # ", "#####", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "#### "],
    "6": [" ####", "#    ", "#####", "#   #", " ####"],
    "7": ["#####", "    #", "   # ", "  #  ", "  #  "],
    "8": [" ### ", "#   #", " ### ", "#   #", " ### "],
    "9": [" ### ", "#   #", " ####", "    #", " ####"],
    " ": ["   ", "   ", "   ", "   ", "   "],
}


def _block_art(text):
    """Buat ASCII art block-style dari teks (huruf & angka kapital)."""
    lines = ["" for _ in range(5)]
    for ch in text.upper():
        glyph = _BLOCK_LETTERS.get(ch, _BLOCK_LETTERS[" "])
        for i in range(5):
            lines[i] += glyph[i] + " "
    return "\n".join(lines)


def tg_spam():
    """Mode spam text: ulang teks N kali, opsi nomor, pemisah, delay, simpan file."""
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
            jumlah = input(t("tg.input_count"))
            if jumlah.lower() == "exit":
                break
            try:
                jumlah = int(jumlah)
            except ValueError:
                print(t("tg.count_error"))
                input(t("tg.press_enter"))
                continue
            number = input(t("tg.input_number"))
            sep = input(t("tg.input_separator"))
            sep = {"n": "\n", "s": " ", "c": ",", "/": ","}.get(sep.strip().lower(), sep.replace("\\n", "\n"))
            delay = input(t("tg.input_delay"))
            try:
                delay = float(delay) if delay.strip() else 0.0
            except ValueError:
                delay = 0.0
            numbered = number.strip().lower() == "y"
            result = sep.join(f"{i}. {text}" if numbered else text for i in range(1, jumlah + 1))
            print("\n" + "-" * 40)
            if delay:
                for i in range(1, jumlah + 1):
                    print(f"{i}. {text}" if numbered else text, flush=True)
                    time.sleep(delay)
            else:
                print(result)
            print("-" * 40)
            if input(t("tg.input_save")).strip().lower() == "y":
                fname = input(t("tg.input_filename")).strip() or "tg_output.txt"
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(result + "\n")
                print(t("tg.saved").format(path=fname))
        except KeyboardInterrupt:
            print("\n^C")
            break
        input(t("tg.press_enter"))


_FIRST_NAMES = ["Andi", "Budi", "Citra", "Dewi", "Eko", "Fajar", "Gita", "Hadi", "Intan", "Joko",
                "Kartika", "Lukas", "Maya", "Nanda", "Putri", "Rizky", "Sari", "Tono", "Umi", "Vina"]
_LAST_NAMES = ["Pratama", "Saputra", "Wijaya", "Hidayat", "Santoso", "Kurniawan", "Nugroho",
               "Susanti", "Lestari", "Permata", "Rahayu", "Firmansyah", "Anggraini", "Maulana"]
_STREETS = ["Jl. Merdeka", "Jl. Sudirman", "Jl. Melati", "Jl. Kenanga", "Jl. Mawar", "Jl. Hasanuddin"]
_CITIES = ["Jakarta", "Bandung", "Surabaya", "Medan", "Yogyakarta", "Semarang", "Makassar", "Malang"]
_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "example.com"]
_PREFIXES = ["0812", "0813", "0852", "0856", "0895", "0821"]


def tg_random():
    """Mode random text generator: nama, email, alamat, telepon acak."""
    while True:
        config.clear_screen()
        print(config.divider())
        print(t("tg.title"))
        print(config.divider() + "\n")
        print(t("tg.random_menu") + "\n")
        mode = input(t("tg.input_choice"))
        if mode.lower() == "exit" or mode == "0":
            break
        try:
            mode = int(mode)
        except ValueError:
            continue
        try:
            count = int(input(t("tg.input_count")))
        except ValueError:
            print(t("tg.count_error"))
            input(t("tg.press_enter"))
            continue
        print()
        for _ in range(count):
            if mode == 1:
                print(f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}")
            elif mode == 2:
                name = f"{random.choice(_FIRST_NAMES).lower()}{random.choice(_LAST_NAMES).lower()}"
                print(f"{name}{random.randint(1, 99)}@{random.choice(_DOMAINS)}")
            elif mode == 3:
                num = random.randint(1, 999)
                print(f"{random.choice(_STREETS)} No. {num}, {random.choice(_CITIES)}")
            elif mode == 4:
                print(f"+62 {random.choice(_PREFIXES)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}")
            else:
                print(t("tg.bad_choice"))
                break
        input(t("tg.press_enter"))


_FANCY_NAMES = {
    "1": "bold", "2": "italic", "3": "script", "4": "fraktur",
    "5": "double", "6": "sans", "7": "mono", "8": "circled",
    "9": "squared", "10": "fullwidth",
}


def tg_fancy():
    """Mode fancy text: ubah teks ke berbagai gaya Unicode."""
    while True:
        config.clear_screen()
        print(config.divider())
        print(t("tg.title"))
        print(config.divider() + "\n")
        print(t("tg.fancy_menu") + "\n")
        style = input(t("tg.input_choice"))
        if style.lower() == "exit" or style == "0":
            break
        if style not in _FANCY_NAMES:
            print(t("tg.bad_choice"))
            input(t("tg.press_enter"))
            continue
        text = input(t("tg.input_text"))
        if text.lower() == "exit":
            break
        print("\n" + _fancy_convert(text, _FANCY_NAMES[style]) + "\n")
        input(t("tg.press_enter"))


def tg_ascii():
    """Mode ascii art: teks jadi banner block-style buatan sendiri."""
    while True:
        config.clear_screen()
        print(config.divider())
        print(t("tg.title"))
        print(config.divider() + "\n")
        print(t("tg.exit") + "\n")
        text = input(t("tg.input_text"))
        if text.lower() == "exit":
            break
        print("\n" + _block_art(text) + "\n")
        input(t("tg.press_enter"))


_CHARS_LOWER = "abcdefghijklmnopqrstuvwxyz"
_CHARS_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_CHARS_DIGIT = "0123456789"
_CHARS_SYMBOL = "!@#$%^&*()-_=+[]{};:,.<>?"


def tg_password():
    """Mode password generator."""
    while True:
        config.clear_screen()
        print(config.divider())
        print(t("tg.title"))
        print(config.divider() + "\n")
        print(t("tg.password_hint") + "\n")
        options = {
            "1": _CHARS_LOWER, "2": _CHARS_UPPER, "3": _CHARS_DIGIT,
            "4": _CHARS_SYMBOL, "5": _CHARS_LOWER + _CHARS_UPPER,
            "6": _CHARS_LOWER + _CHARS_UPPER + _CHARS_DIGIT,
            "7": _CHARS_LOWER + _CHARS_UPPER + _CHARS_DIGIT + _CHARS_SYMBOL,
        }
        mode = input(t("tg.input_choice"))
        if mode.lower() == "exit" or mode == "0":
            break
        if mode not in options:
            print(t("tg.bad_choice"))
            input(t("tg.press_enter"))
            continue
        try:
            length = int(input(t("tg.input_length")))
        except ValueError:
            print(t("tg.count_error"))
            input(t("tg.press_enter"))
            continue
        try:
            amount = int(input(t("tg.password_amount")))
        except ValueError:
            amount = 1
        charset = options[mode]
        print()
        for _ in range(amount):
            print("".join(random.choice(charset) for _ in range(max(length, 1))))
        input(t("tg.press_enter"))


def tg_key():
    """Mode key generator: license/product key atau token random."""
    while True:
        config.clear_screen()
        print(config.divider())
        print(t("tg.title"))
        print(config.divider() + "\n")
        print(t("tg.key_menu") + "\n")
        mode = input(t("tg.input_choice"))
        if mode.lower() == "exit" or mode == "0":
            break
        try:
            segments = int(input(t("tg.key_segments")))
        except ValueError:
            segments = 4
        try:
            seg_len = int(input(t("tg.key_seglen")))
        except ValueError:
            seg_len = 4
        if mode == "1":
            chars = "0123456789ABCDEF"
        elif mode == "2":
            chars = _CHARS_UPPER + _CHARS_DIGIT
        elif mode == "3":
            chars = _CHARS_LOWER + _CHARS_UPPER + _CHARS_DIGIT
        else:
            print(t("tg.bad_choice"))
            input(t("tg.press_enter"))
            continue
        parts = []
        for _ in range(segments):
            parts.append("".join(random.choice(chars) for _ in range(seg_len)))
        print("\n" + "-".join(parts) + "\n")
        input(t("tg.press_enter"))


def text_generator():
    """Menu utama Text Generator: pilih mode."""
    while True:
        config.clear_screen()
        print(config.divider())
        print(t("tg.title"))
        print(config.divider() + "\n")
        print(t("tg.menu") + "\n")
        choice = input(t("tg.input_choice"))
        if choice.lower() == "exit" or choice == "0":
            break
        if choice == "1":
            tg_spam()
        elif choice == "2":
            tg_random()
        elif choice == "3":
            tg_fancy()
        elif choice == "4":
            tg_ascii()
        elif choice == "5":
            tg_password()
        elif choice == "6":
            tg_key()
        else:
            print(t("tg.bad_choice"))
            input(t("tg.press_enter"))


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
    "keystore", "rn", "rename",
}

# Beritahu pipe.py nama-nama builtin ini agar pipeline murni perintah sistem
# (mis. curl | bash) bisa di-stream real-time, bukan di-capture.
pipe.register_builtin_names(PIPE_BUILTINS)


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
        pipe.execute_pipeline(
            single_command,
            builtin_runner=_run_builtin_capture,
            stream_system=True,
        )
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

    elif cmd in ["rn", "rename"]:
        args = arg.split(maxsplit=1)
        if len(args) == 2:
            src, dst = args[0], args[1]
            if os.path.exists(src):
                if os.path.isdir(src):
                    print(t("err.rn_dir", src=src))
                    return
                if os.path.exists(dst):
                    print(t("err.rn_exists", dst=dst))
                    return
                try:
                    os.rename(src, dst)
                    print(t("ok.rn", src=src, dst=dst))
                except Exception as e:
                    print(t("err.rn_fail", e=e))
                    return
            else:
                print(t("err.src_not_found", src=src))
                return
        else:
            print(t("usage.rn"))

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

    elif cmd == "keystore":
        handle_keystore(arg)

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

    elif cmd in ("deploy", "dp"):
        handle_deploy(arg)

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
