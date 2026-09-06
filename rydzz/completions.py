import os

from . import config

BUILTIN_COMMANDS = [
    "ls", "dir", "cd", "pwd", "mkdir", "rm", "hapus", "mv", "cp",
    "touch", "cat", "nano", "echo", "history", "python", "py", "PY",
    "pip", "pip3", "node", "git", "curl", "wget", "ssh", "sshd",
    "ping", "zip", "unzip", "tar", "grep", "find", "df", "free",
    "ps", "neofetch", "fastfetch", "whoami", "passwd", "passw",
    "source", "sudo", "alias", "aliases", "list", "help", "?",
    "clear", "htop", "print", "TG", "exit",
    # git shortcuts
    "gs", "ga", "gl", "gb", "gd", "gp", "gpl", "gst", "gc", "gco",
    "gclone",
    # fitur baru
    "tree", "dl", "qr", "ascii", "wclone", "wcode",
    # AI pemandu
    "ai", "rydza",
    # alat harian
    "timer", "stopwatch", "calc", "weather",
]

_PATH_CACHE = {}


def _path_commands():
    """Mengumpulkan binary dari PATH yang bisa dieksekusi."""
    exts = {".exe", ".bat", ".cmd"} if os.name == "nt" else set()
    result = set()
    for d in os.environ.get("PATH", "").split(":"):
        if not d:
            continue
        try:
            for name in os.listdir(d):
                full = os.path.join(d, name)
                if os.access(full, os.X_OK) or name.lower().endswith(tuple(exts)):
                    result.add(name)
        except OSError:
            continue
    return result


def build_command_list():
    """Menggabungkan builtin + alias + binary PATH menjadi set perintah."""
    cmds = set(BUILTIN_COMMANDS)
    cmds.update(config.CONFIG.get("rydzz_aliases", {}).keys())
    cmds.update(getattr(config, "USER_ALIASES", {}).keys())
    cmds.update(_path_commands())
    return sorted(cmds)


def refresh():
    """Paksa pembacaan ulang daftar command (alias baru dll).

    Dipanggil setelah `source ~/.bashrc` / `source ~/.rydzzrc` agar tab
    completion langsung memakai alias yang baru saja dimuat.
    """
    _PATH_CACHE.clear()
    return build_command_list()


def _complete_path(text, cwd):
    """Lengkapi nama file/folder di cwd."""
    base = os.path.dirname(text)
    fragment = os.path.basename(text)
    if base:
        dir_path = os.path.join(cwd, base) if not os.path.isabs(base) else base
    else:
        dir_path = cwd

    try:
        entries = os.listdir(dir_path)
    except OSError:
        return []

    matches = []
    for name in entries:
        if name in config.PROTECTED_FILES:
            continue
        if not config.CONFIG.get("hidden", False) and name.startswith("."):
            continue
        if name.startswith(fragment):
            full = os.path.join(dir_path, name)
            display = os.path.join(base, name) if base else name
            if os.path.isdir(full):
                display += "/"
            matches.append(display)
    return matches


def completer(text, state):
    """Completer readline. Kata pertama = command, sisanya = path."""
    global readline
    if readline is None:
        return None

    line = readline.get_line_buffer()
    begin = readline.get_begidx()
    end = readline.get_endidx()

    # Kata pertama dalam buffer?
    if line[:begin].strip() == "" and text == line[:end].strip():
        prefix_cmd = text
        all_cmds = build_command_list()
        matches = [c for c in all_cmds if c.startswith(prefix_cmd)]
        matches.sort()
        # beri spasi di akhir biar bisa lanjut argumen
        matches = [m + "" for m in matches]
        try:
            return matches[state]
        except IndexError:
            return None

    # Bukan kata pertama -> complete path
    cwd = os.getcwd()
    matches = _complete_path(text, cwd)
    try:
        return matches[state]
    except IndexError:
        return None


def setup_readline():
    global readline
    try:
        import readline as _rl
    except ImportError:
        return
    readline = _rl
    _rl.set_completer(completer)
    _rl.set_completer_delims(" \t\n;")
    _rl.parse_and_bind("tab: menu-complete")


def setup_readline_history():
    """Muat riwayat readline dari file agar panah atas lintas-sesi jalan."""
    global readline
    if readline is None:
        return
    if not config.CONFIG.get("history", True):
        return
    try:
        if os.path.exists(config.HISTORY_FILE):
            readline.read_history_file(config.HISTORY_FILE)
        readline.set_history_length(config.HISTORY_LIMIT)
    except Exception:
        pass


# Simpan referensi readline untuk dipakai completer
try:
    import readline
except ImportError:
    readline = None
