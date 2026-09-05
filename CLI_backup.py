import getpass
import math
import os
import shutil
import sys
import time

# Load modul readline untuk TAB completion & History panah atas/bawah
try:
    import readline

    readline.parse_and_bind("tab: complete")
except ImportError:
    pass

# --- 1. SETUP ENVIRONMENT & HOME KHUSUS ---
CUSTOM_HOME = os.path.expanduser("~/.rydzz_home")
if not os.path.exists(CUSTOM_HOME):
    os.makedirs(CUSTOM_HOME)

os.environ["HOME"] = CUSTOM_HOME

# Set Shell Level (SHLVL)
SHELL_LEVEL = int(os.environ.get("RYDZZ_LEVEL", 1))
os.environ["RYDZZ_LEVEL"] = str(SHELL_LEVEL + 1)

# --- 2. MANAGEMENT SUDO PASSWORD PERMANEN ---
CUSTOM_SUDO_PASS = "SecretPass123"  # Password default
PASS_FILE_PATH = os.path.join(CUSTOM_HOME, ".sudo_pass")

# Muat password dari file jika pernah diubah sebelumnya
if os.path.exists(PASS_FILE_PATH):
    try:
        with open(PASS_FILE_PATH, "r") as f:
            saved_pass = f.read().strip()
            if saved_pass:
                CUSTOM_SUDO_PASS = saved_pass
    except Exception:
        pass

# --- 3. KODE WARNA ANSI ---
GREEN_NEON = "\033[92m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

COMMAND_HISTORY = []

# Daftar file rahasia/proteksi yang disembunyikan dari 'ls' dan tidak bisa dibaca biasa
PROTECTED_FILES = [
    "CLI.py",
    ".CLI.py",
    "rydzz.py",
    ".rydzz.py",
    ".sudo_pass",
]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def reset_terminal():
    """Mereset mode input terminal agar tidak ngebug setelah CTRL+C"""
    if os.name != "nt":
        os.system("stty sane 2>/dev/null")


def run_system_cmd(command):
    """Menjalankan perintah terminal dengan penanganan CTRL+C yang aman"""
    try:
        os.system(command)
    except KeyboardInterrupt:
        print("\n^C")
    finally:
        reset_terminal()


def show_banner():
    """Menampilkan Tampilan Awal / ASCII Art"""
    clear_screen()
    banner = f"""{GREEN_NEON}
  _____ydzz   _____ _          _ 
 |  __ \     / ____| |        | |
 | |__) |   | (___ | |__   ___| |
 |  _  /     \___ \| '_ \ / _ \ |
 | | \ \ _   ____) | | | |  __/ |
 |_|  \_(_) |_____/|_| |_|\___|_|
{CYAN}    --- Custom Interactive Shell v2.0 ---{RESET}
{YELLOW}  Ketik 'help' atau '?' untuk daftar perintah.{RESET}
"""
    print(banner)


# Tampilkan Banner & Pindah ke Home Khusus hanya saat pertama kali dibuka
if "RYDZZ_INIT" not in os.environ:
    os.chdir(CUSTOM_HOME)
    os.environ["RYDZZ_INIT"] = "1"
    show_banner()


def load_bashrc_aliases():
    """Ngebaca dan ngambil daftar alias dari file ~/.bashrc"""
    aliases = {}
    bashrc_path = os.path.expanduser("~/.bashrc")

    if os.path.exists(bashrc_path):
        try:
            with open(bashrc_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("alias ") and not line.startswith("#"):
                        content = line.replace("alias ", "", 1)
                        if "=" in content:
                            name, command = content.split("=", 1)
                            name = name.strip()
                            command = command.strip().strip("'\"")
                            aliases[name] = command
        except Exception as e:
            print(f"Gagal membaca ~/.bashrc: {e}")

    return aliases


def get_git_branch():
    """Ngecek apakah folder aktif adalah Repo Git dan ngambil nama branch-nya"""
    if os.path.exists(".git"):
        try:
            with open(".git/HEAD", "r") as f:
                content = f.read().strip()
                if content.startswith("ref: refs/heads/"):
                    return (
                        f" ({CYAN}{content.replace('ref: refs/heads/', '')}{RESET})"
                    )
        except Exception:
            pass
    return ""


def custom_ls(target_dir="."):
    """Tampilan 'ls' berkolom dengan penyaringan file proteksi"""
    try:
        target_path = os.path.expanduser(target_dir)

        if not os.path.exists(target_path):
            print(
                f"ls: tidak dapat mengakses '{target_dir}': No such file or"
                " directory"
            )
            return

        if os.path.isfile(target_path):
            if os.path.basename(target_path) not in PROTECTED_FILES:
                print(target_dir)
            return

        all_items = sorted(os.listdir(target_path))
        items = [item for item in all_items if item not in PROTECTED_FILES]

        if not items:
            print("(Folder kosong)")
            return

        formatted_items = []
        raw_lengths = []

        for item in items:
            full_item_path = os.path.join(target_path, item)
            raw_lengths.append(len(item))
            if os.path.isdir(full_item_path):
                formatted_items.append(f"{PURPLE}{item}{RESET}")
            else:
                formatted_items.append(item)

        try:
            term_width = os.get_terminal_size().columns
        except OSError:
            term_width = 80

        max_len = max(raw_lengths) + 3
        col_count = max(1, term_width // max_len)
        row_count = math.ceil(len(items) / col_count)

        for r in range(row_count):
            line_str = ""
            for c in range(col_count):
                idx = r + c * row_count
                if idx < len(items):
                    item_colored = formatted_items[idx]
                    padding = max_len - raw_lengths[idx]
                    line_str += item_colored + (" " * padding)
            print(line_str)
    except Exception as e:
        print(f"Error ls: {e}")


def show_help():
    print("=" * 65)
    print("                  DAFTAR PERINTAH RYDZZ SHELL")
    print("=" * 65)
    print("• ls [path]                - Melihat isi folder (Ungu = Folder)")
    print(
        "• cd [folder]              - Pindah folder (cd doang = balik ke Home"
        " Khusus)"
    )
    print("• pwd                      - Menampilkan path lokasi direktori aktif")
    print("• mkdir <folder>           - Membuat folder baru")
    print("• rm <file/folder>         - Menghapus file atau folder")
    print("• mv <asal> <tujuan>       - Pindah atau rename file/folder")
    print("• cp <asal> <tujuan>       - Menyalin file atau folder")
    print("• cat / touch / grep       - Manipulasi file teks")
    print("• nano <file>              - Membuat/edit file teks")
    print("• python / py <file.py>    - Menjalankan script Python")
    print("• pip <command>            - Pengelola paket Python")
    print("• node <file.js>           - Menjalankan script Node.js")
    print("• git / curl / wget        - Download & Network tools")
    print("• ssh / sshd / ping        - Remote & Connectivity")
    print("• whoami / passwd          - Informasi user & ubah password")
    print("• df / free / ps / htop    - Informasi memori & sistem")
    print("• neofetch                 - Tampilan sistem aesthetic")
    print("• history                  - Melihat riwayat perintah")
    print(
        "• sudo edit <file>         - Akses terproteksi untuk edit file rahasia"
    )
    print(
        "• sudo newpass             - Mengubah password Sudo khusus secara"
        " permanen"
    )
    print("• source ~/.bashrc         - Reload alias dari ~/.bashrc")
    print(
        "• alias / aliases          - Menampilkan alias yang dibaca dari"
        " ~/.bashrc"
    )
    print("• TG                       - Membuka Text Generator")
    print("• clear                    - Membersihkan layar")
    print("• exit                     - Keluar dari shell")
    print("• <cmd1> && <cmd2>         - Menjalankan 2 perintah sekaligus")
    print("=" * 65)


USER_ALIASES = load_bashrc_aliases()

while True:
    cwd = os.path.basename(os.getcwd()) or os.getcwd()
    git_info = get_git_branch()

    level_str = f" L{SHELL_LEVEL}" if SHELL_LEVEL > 1 else ""

    try:
        prompt = f"{GREEN_NEON}RydzzShell{level_str}:[{cwd}]{git_info}$ {RESET}"
        raw_input = input(prompt).strip()

        if not raw_input:
            continue

        COMMAND_HISTORY.append(raw_input)

        # --- FITUR DOUBLE COMMAND (&&) ---
        commands = [c.strip() for c in raw_input.split("&&")]

        for single_command in commands:
            if not single_command:
                continue

            parts = single_command.split(maxsplit=1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""

            # --- CEK ALIAS DARI ~/.bashrc ---
            if cmd in USER_ALIASES:
                aliased_cmd = USER_ALIASES[cmd]
                full_cmd = f"{aliased_cmd} {arg}".strip()
                parts = full_cmd.split(maxsplit=1)
                cmd = parts[0]
                arg = parts[1] if len(parts) > 1 else ""
                single_command = full_cmd

            # --- TAMPILAN LS KHUSUS ---
            if cmd in ["ls", "dir"]:
                target_path = arg if arg else "."
                custom_ls(target_path)

            elif cmd == "pwd":
                print(os.getcwd())

            # --- PERINTAH MOVING & COPYING ---
            elif cmd == "mv":
                args = arg.split(maxsplit=1)
                if len(args) == 2:
                    src, dst = args[0], args[1]
                    if os.path.exists(src):
                        if dst.endswith("/") and not os.path.exists(dst):
                            print(
                                f"Error: Folder tujuan '{dst}' tidak ditemukan!"
                            )
                            break
                        else:
                            try:
                                shutil.move(src, dst)
                                if os.path.isdir(dst):
                                    print(
                                        f"'{src}' berhasil dipindahkan ke"
                                        f" folder '{dst}'."
                                    )
                                else:
                                    print(
                                        f"'{src}' berhasil di-rename menjadi"
                                        f" '{dst}'."
                                    )
                            except Exception as e:
                                print(f"Gagal memindahkan: {e}")
                                break
                    else:
                        print(f"File/Folder asal '{src}' tidak ditemukan!")
                        break
                else:
                    print("Guna: mv <asal> <tujuan>")
                    break

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
                            break
                    else:
                        print(f"File/Folder asal '{src}' tidak ditemukan!")
                        break
                else:
                    print("Guna: cp <asal> <tujuan>")
                    break

            # --- PERINTAH DIRECTORY & FILE ---
            elif cmd == "cd":
                if arg:
                    try:
                        os.chdir(arg)
                    except FileNotFoundError:
                        print(f"Folder '{arg}' tidak ditemukan!")
                        break
                    except NotADirectoryError:
                        print(f"'{arg}' bukan sebuah folder!")
                        break
                    except Exception as e:
                        print(f"Gagal pindah folder: {e}")
                        break
                else:
                    os.chdir(CUSTOM_HOME)

            elif cmd == "mkdir":
                if arg:
                    try:
                        os.mkdir(arg)
                        print(f"Folder '{arg}' berhasil dibuat.")
                    except FileExistsError:
                        print(f"Folder '{arg}' sudah ada!")
                    except Exception as e:
                        print(f"Gagal membuat folder: {e}")
                        break
                else:
                    print("Guna: mkdir <nama_folder>")
                    break

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
                            break
                    else:
                        print("File/Folder tidak ditemukan!")
                        break
                else:
                    print("Guna: rm <nama_file_atau_folder>")
                    break

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
                        if arg in PROTECTED_FILES:
                            print(
                                "Akses Ditolak: Gunakan 'sudo edit' untuk"
                                " mengakses file terproteksi."
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
                    if arg in PROTECTED_FILES:
                        print(
                            "Akses Ditolak: Gunakan 'sudo edit' untuk mengakses"
                            " file terproteksi."
                        )
                    else:
                        run_system_cmd(f'nano "{arg}"')
                else:
                    print("Guna: nano <nama_file>")
                    break

            # --- PERINTAH RIWAYAT & ECHO ---
            elif cmd == "history":
                print("Daftar Riwayat Perintah:")
                for i, h_cmd in enumerate(COMMAND_HISTORY, 1):
                    print(f"  {i}  {h_cmd}")

            elif cmd == "echo":
                print(arg)

            # --- PERINTAH EKSEKUSI PROGRAM & DEVELOPMENT ---
            elif cmd in ["python", "py", "PY"]:
                if arg:
                    run_system_cmd(f'python3 "{arg}"')
                else:
                    print("Guna: python <nama_file.py>")
                    break

            elif cmd in ["pip", "pip3"]:
                run_system_cmd(single_command)

            elif cmd == "node":
                if arg:
                    run_system_cmd(f'node "{arg}"')
                else:
                    print("Guna: node <nama_file.js>")
                    break

            # --- PERINTAH NETWORKING & SYSTEM TOOLS ---
            elif cmd in [
                "git",
                "curl",
                "wget",
                "ssh",
                "sshd",
                "ping",
                "zip",
                "unzip",
                "tar",
                "grep",
                "find",
                "df",
                "free",
                "ps",
                "neofetch",
                "fastfetch",
            ]:
                run_system_cmd(single_command)

            elif cmd == "whoami":
                run_system_cmd("whoami")

            elif cmd in ["passwd", "passw"]:
                run_system_cmd("passwd")

            # --- HANDLING COMMAND SOURCE ---
            elif cmd == "source":
                if arg == "~/.bashrc" or arg == os.path.expanduser("~/.bashrc"):
                    USER_ALIASES = load_bashrc_aliases()
                    print("Berhasil meng-update alias dari ~/.bashrc!")
                else:
                    print("Gunakan: source ~/.bashrc")

            # --- SUDO CUSTOM & UNIVERSAL ---
            elif single_command.startswith("sudo"):

                # 1. Ganti Password Sudo (sudo newpass)
                if single_command == "sudo newpass":
                    try:
                        old_pass = getpass.getpass(
                            "Masukkan Sudo Password Lama: "
                        )
                        if old_pass == CUSTOM_SUDO_PASS:
                            new_pass = getpass.getpass(
                                "Masukkan Sudo Password Baru: "
                            )
                            confirm_pass = getpass.getpass(
                                "Konfirmasi Password Baru: "
                            )

                            if new_pass == confirm_pass:
                                if new_pass.strip():
                                    CUSTOM_SUDO_PASS = new_pass.strip()
                                    with open(PASS_FILE_PATH, "w") as f:
                                        f.write(CUSTOM_SUDO_PASS)
                                    print(
                                        "\n[SUCCESS] Sudo Password berhasil"
                                        " diubah!"
                                    )
                                else:
                                    print(
                                        "\n[ERROR] Password tidak boleh kosong!"
                                    )
                            else:
                                print(
                                    "\n[ERROR] Konfirmasi password tidak cocok!"
                                )
                        else:
                            print("\n[ERROR] Password lama salah!")
                    except KeyboardInterrupt:
                        print("\n^C")
                        reset_terminal()
                    break

                # 2. Edit File Terproteksi (sudo edit <file>)
                elif single_command.startswith("sudo edit"):
                    target_file = single_command.replace(
                        "sudo edit ", "", 1
                    ).strip()
                    if target_file:
                        try:
                            pass_input = getpass.getpass(
                                "Masukkan Custom Sudo Password: "
                            )
                            if pass_input == CUSTOM_SUDO_PASS:
                                print("\nAkses Diterima!")
                                run_system_cmd(f'nano "{target_file}"')
                            else:
                                print("\nAkses Ditolak: Password Salah!")
                        except KeyboardInterrupt:
                            print("\n^C")
                            reset_terminal()
                    else:
                        print("Guna: sudo edit <nama_file>")
                    break

                # 3. Perilaku Sudo Biasa
                is_real_linux = shutil.which("sudo") and os.path.exists(
                    "/usr/bin/sudo"
                )

                if is_real_linux:
                    run_system_cmd(single_command)
                else:
                    try:
                        sudo_pass = getpass.getpass("Rydzz Password: ")
                        if sudo_pass == CUSTOM_SUDO_PASS:
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
                                cmd_tanpa_sudo = single_command.replace(
                                    "sudo ", "", 1
                                )
                                print(
                                    f"Executing with fake-root: {cmd_tanpa_sudo}"
                                )
                                run_system_cmd(cmd_tanpa_sudo)
                        else:
                            print("sudo: 1 incorrect password attempt")
                            break
                    except KeyboardInterrupt:
                        print("\n^C")
                        reset_terminal()
                        break

            # --- LIAT DAFTAR ALIAS ---
            elif cmd in ["alias", "aliases"]:
                if USER_ALIASES:
                    print("Daftar Alias dari ~/.bashrc:")
                    for k, v in USER_ALIASES.items():
                        print(f"  {k} -> '{v}'")
                else:
                    print("Tidak ada alias ditemukan di ~/.bashrc")

            # --- PERINTAH LAINNYA ---
            elif cmd in ["list", "help", "?"]:
                show_help()

            elif cmd == "clear":
                clear_screen()

            elif cmd == "htop":
                run_system_cmd("htop")

            elif cmd == "print":
                print("kocak")

            elif cmd == "TG":
                while True:
                    clear_screen()
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

            elif cmd == "exit":
                sys.exit()

            # --- FALLBACK SYSTEM ---
            else:
                if shutil.which(cmd):
                    run_system_cmd(single_command)
                else:
                    print(f"Command Not Found: {cmd}")
                    break

    except KeyboardInterrupt:
        print("\n^C")
        reset_terminal()
        continue
    except EOFError:
        print("\nGunakan perintah 'exit' untuk keluar.")
        continue
