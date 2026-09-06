import os
import re
import shutil
import subprocess
import sys
import textwrap
import time

from . import i18n
from .i18n import t

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

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

# --- Riwayat permanen antar-sesi ---
HISTORY_FILE = os.path.join(CUSTOM_HOME, ".rydzz_history")
HISTORY_LIMIT = 1000
HISTORY_PERSIST = True

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
    "history": True,
    "ai": True,
    "ai_key": "",
    "ai_model": "",
    "ai_base": "",
    "ai_nama": "RydzAgent",
    "weather_city": "jakarta",
    "lang": "en",
    "rydzz_aliases": {},
}

# Data untuk `ai error` — isi saat perintah gagal
LAST_CMD = ""
LAST_ERROR = ""


def wrap_ansi(text):
    """Bungkus kode ANSI dengan marker non-printing readline agar lebar
    prompt dihitung benar (mencegah teks wrap ke baris yang salah)."""
    return ANSI_RE.sub(lambda m: "\x01" + m.group(0) + "\x02", text)


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


def term_width():
    """Lebar terminal saat ini (fallback 80 kolom)."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def divider(char="=", cap=80):
    """Garis pemisah mengikuti lebar terminal, dibatasi maks `cap`."""
    return char * max(10, min(term_width(), cap))


def wrap_text(text, width=None, indent=2):
    """Bungkus baris panjang agar pas dengan lebar terminal.

    Baris yang sudah pendek dibiarkan utuh; newline eksisting dipertahankan
    dan kata panjang (URL/path) tidak dipecah.
    """
    if width is None:
        width = term_width()
    out = []
    for line in text.split("\n"):
        if len(ANSI_RE.sub("", line)) <= width:
            out.append(line)
            continue
        lead = len(line) - len(line.lstrip(" "))
        sub = " " * (lead + indent)
        wrapped = textwrap.wrap(
            line[lead:],
            width=max(10, width - lead),
            break_long_words=False,
            break_on_hyphens=False,
            replace_whitespace=False,
            subsequent_indent=sub,
        )
        wrapped[0] = " " * lead + wrapped[0].lstrip()
        out.append("\n".join(wrapped))
    return "\n".join(out)


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
        result = subprocess.run(command, shell=True, env=env)
        return result.returncode
    except KeyboardInterrupt:
        print("\n^C")
        return None
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
            print(t("cfg.bashrc_read_error", e=e))

    return aliases


def load_history():
    """Membaca riwayat perintah antar-sesi dari file ke COMMAND_HISTORY."""
    if not CONFIG.get("history", True):
        return
    if not os.path.exists(HISTORY_FILE):
        return
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8", errors="replace") as f:
            lines = [l.rstrip("\n") for l in f if l.strip()]
    except Exception:
        return
    merged = []
    for line in lines:
        if merged and merged[-1] == line:
            continue
        merged.append(line)
    COMMAND_HISTORY[:] = merged[-HISTORY_LIMIT:]


def _flush_history_buffer():
    """Menulis seluruh buffer COMMAND_HISTORY ke file riwayat."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            for line in COMMAND_HISTORY[-HISTORY_LIMIT:]:
                f.write(line + "\n")
    except Exception:
        pass


def append_history(cmd):
    """Menambahkan perintah ke buffer lalu menyimpannya (write-through)."""
    if not CONFIG.get("history", True):
        return
    cmd = (cmd or "").strip()
    if not cmd:
        return
    if COMMAND_HISTORY and COMMAND_HISTORY[-1] == cmd:
        return
    COMMAND_HISTORY.append(cmd)
    if len(COMMAND_HISTORY) > HISTORY_LIMIT:
        del COMMAND_HISTORY[:-HISTORY_LIMIT]
    _flush_history_buffer()


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
            elif key == "history":
                CONFIG["history"] = value.lower() in ("true", "1", "yes", "on")
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
            elif key == "ai":
                # ai=true/false -> matikan/aktifkan semua fitur AI
                CONFIG["ai"] = value.lower() in ("true", "1", "yes", "on")
            elif key == "ai key":
                CONFIG["ai_key"] = value
            elif key == "ai model":
                CONFIG["ai_model"] = value
            elif key == "ai base":
                CONFIG["ai_base"] = value
            elif key == "ai nama":
                CONFIG["ai_nama"] = value
            elif key == "weather city":
                CONFIG["weather_city"] = value.strip().lower()
            elif key == "lang":
                if i18n.set_language(value):
                    CONFIG["lang"] = i18n.get_language()
            elif key == "env":
                # env=KEY=VALUE -> set environment variable untuk shell & child
                k, _, v = value.partition("=")
                if k.strip():
                    os.environ[k.strip()] = v.strip()
    return


def _persist_language(code):
    """Tulis/update baris `lang=<kode>` di ~/.rydzz_home/.rydzzrc."""
    path = RYDZZRC_PATH
    lines = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError:
            lines = []
    found = False
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            cleaned.append(line)
            continue
        key, _, _ = stripped.partition("=")
        if key.strip().lower() == "lang":
            if not found:
                cleaned.append(f"lang={code}")
                found = True
            continue
        cleaned.append(line)
    if not found:
        cleaned.append(f"lang={code}")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned) + "\n")
    except OSError:
        pass


def apply_language(code):
    """Ganti bahasa saat runtime (lang -C / lang set) dan simpan ke .rydzzrc."""
    result = i18n.set_language(code)
    if not result:
        return False
    CONFIG["lang"] = result
    _persist_language(result)
    return True
