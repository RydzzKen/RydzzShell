import os
import shutil
import subprocess
import sys
import time

# --- 1. SETUP ENVIRONMENT & HOME KHUSUS ---
try:
    import pwd

    REAL_HOME = pwd.getpwuid(os.getuid()).pw_dir
except Exception:
    REAL_HOME = os.path.expanduser("~")

CUSTOM_HOME = os.path.expanduser("~/.rydzz_home")
if not os.path.exists(CUSTOM_HOME):
    os.makedirs(CUSTOM_HOME)

os.environ["HOME"] = CUSTOM_HOME

# Set Shell Level (SHLVL)
SHELL_LEVEL = int(os.environ.get("RYDZZ_LEVEL", 1))
os.environ["RYDZZ_LEVEL"] = str(SHELL_LEVEL + 1)

# --- 2. MANAGEMENT SUDO PASSWORD PERMANEN ---
CUSTOM_SUDO_PASS = "SecretPass123"
PASS_FILE_PATH = os.path.join(CUSTOM_HOME, ".sudo_pass")

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
BLUE = "\033[94m"
MAGENTA = "\033[35m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
WHITE = "\033[97m"
RESET = "\033[0m"

COMMAND_HISTORY = []

# Alias yang dibaca dari ~/.bashrc (diisi saat shell start)
USER_ALIASES = {}

# Daftar file rahasia/proteksi yang disembunyikan dari 'ls' dan tidak bisa dibaca biasa
PROTECTED_FILES = [
    "CLI.py",
    ".CLI.py",
    "rydzz.py",
    ".rydzz.py",
    ".sudo_pass",
]

# --- Warna per tipe file untuk ls & tree ---
FILE_TYPE_COLORS = {
    ".py": CYAN,
    ".pyw": CYAN,
    ".js": YELLOW,
    ".mjs": YELLOW,
    ".ts": YELLOW,
    ".tsx": YELLOW,
    ".jsx": YELLOW,
    ".md": WHITE,
    ".markdown": WHITE,
    ".json": GREEN_NEON,
    ".yaml": GREEN_NEON,
    ".yml": GREEN_NEON,
    ".toml": GREEN_NEON,
    ".sh": MAGENTA,
    ".bash": MAGENTA,
    ".zsh": MAGENTA,
    ".html": BLUE,
    ".htm": BLUE,
    ".css": BLUE,
    ".scss": BLUE,
    ".txt": DIM + WHITE,
    ".log": DIM,
    ".ini": GREEN_NEON,
    ".cfg": GREEN_NEON,
    ".config": GREEN_NEON,
    ".zip": RED,
    ".tar": RED,
    ".gz": RED,
    ".rar": RED,
    ".7z": RED,
    ".jpg": MAGENTA,
    ".jpeg": MAGENTA,
    ".png": MAGENTA,
    ".gif": MAGENTA,
    ".svg": MAGENTA,
    ".webp": MAGENTA,
    ".mp3": BLUE,
    ".wav": BLUE,
    ".mp4": BLUE,
    ".mkv": BLUE,
}

# --- Konfigurasi dari .rydzzrc ---
RYDZZRC_PATH = os.path.join(CUSTOM_HOME, ".rydzzrc")
CONFIG = {
    "prompt_color": "green",
    "banner": True,
    "hidden": False,
    "auto_cd": True,
    "rydzz_aliases": {},
}


def get_prompt_color():
    cfg_color = CONFIG.get("prompt_color", "green")
    return {
        "green": GREEN_NEON,
        "purple": PURPLE,
        "cyan": CYAN,
        "yellow": YELLOW,
        "blue": BLUE,
        "magenta": MAGENTA,
        "red": RED,
        "white": WHITE,
    }.get(cfg_color, GREEN_NEON)


def get_file_color(path):
    """Mengembalikan kode warna berdasar ekstensi file."""
    name = os.path.basename(path)
    if os.path.isdir(path):
        return PURPLE
    # File executable (tanpa ekstensi) berwarna merah tebal
    if "." not in name and os.access(path, os.X_OK):
        return RED + BOLD
    _, ext = os.path.splitext(name)
    return FILE_TYPE_COLORS.get(ext.lower(), "")


def is_protected(path):
    return os.path.basename(os.path.abspath(path)) in PROTECTED_FILES


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


def run_system_cmd_real_home(command):
    """Menjalankan perintah dengan HOME asli (untuk gh/git/ssh).

    Kredensial (gh, .gitconfig, .git-credentials, ssh keys) hidup di
    HOME asli. Dengan memulihkan HOME hanya untuk command-command ini,
    auth di terminal utama terbawa ke dalam shell tanpa membocorkan
    sandbox untuk command lain.
    """
    env = {**os.environ, "HOME": REAL_HOME}
    try:
        subprocess.run(command, shell=True, env=env)
    except KeyboardInterrupt:
        print("\n^C")
    finally:
        reset_terminal()


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


def load_rydzzrc():
    """Membaca dan menerapkan konfigurasi dari ~/.rydzz_home/.rydzzrc"""
    if not os.path.exists(RYDZZRC_PATH):
        return

    with open(RYDZZRC_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip().lower()
            value = value.strip()

            if key.startswith("prompt"):
                # format: prompt color=green
                sub = key.replace("prompt", "").strip()
                if sub == "color":
                    CONFIG["prompt_color"] = value.strip().lower()
            elif key == "banner":
                CONFIG["banner"] = value.lower() in ("true", "1", "yes", "on")
            elif key == "hidden":
                CONFIG["hidden"] = value.lower() in ("true", "1", "yes", "on")
            elif key == "auto_cd":
                CONFIG["auto_cd"] = value.lower() in ("true", "1", "yes", "on")
            elif key == "alias":
                # format: alias=<name>=<command>
                if "=" in value:
                    name, _, command = value.partition("=")
                    CONFIG["rydzz_aliases"][name.strip()] = command.strip()
            elif key == "protected":
                # format: protected=add:file1,file2
                if value.lower().startswith("add:"):
                    to_add = value.split(":", 1)[1]
                    for item in to_add.split(","):
                        item = item.strip()
                        if item and item not in PROTECTED_FILES:
                            PROTECTED_FILES.append(item)
            elif key == "init":
                # init=command -> jalanin command saat startup (ditangani shell)
                CONFIG["init_command"] = value
    return
