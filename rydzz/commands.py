import os
import shutil
import stat
import time

from . import config

# Nama-nama flag yang didukung ls
VALID_LS_FLAGS = {
    "a": "sertakan hidden files",
    "l": "format panjang / detail",
}


def _font_color(name):
    return {
        "GREEN_NEON": config.GREEN_NEON,
        "PURPLE": config.PURPLE,
        "CYAN": config.CYAN,
        "YELLOW": config.YELLOW,
        "BLUE": config.BLUE,
        "MAGENTA": config.MAGENTA,
        "RED": config.RED,
        "DIM": config.DIM,
        "BOLD": config.BOLD,
        "WHITE": config.WHITE,
        "RESET": config.RESET,
    }.get(name, config.RESET)


def _permission_string(path):
    """Membuat string permission ala -rwxr-xr-x dari st_mode."""
    try:
        st = os.stat(path)
    except OSError:
        return "----------"

    mode = st.st_mode

    def _rwx(bits):
        return ("r" if bits & 0b100 else "-") + (
            "w" if bits & 0b010 else "-"
        ) + ("x" if bits & 0b001 else "-")

    is_dir = "d" if stat.S_ISDIR(mode) else ("l" if stat.S_ISLNK(mode) else "-")
    owner = _rwx((mode >> 6) & 0b111)
    group = _rwx((mode >> 3) & 0b111)
    other = _rwx(mode & 0b111)
    return f"{is_dir}{owner}{group}{other}"


def _owner_group(path):
    try:
        import grp
        import pwd

        st = os.stat(path)
        try:
            owner = pwd.getpwuid(st.st_uid).pw_name
        except Exception:
            owner = str(st.st_uid)
        try:
            group = grp.getgrgid(st.st_gid).gr_name
        except Exception:
            group = str(st.st_gid)
        return owner, group
    except Exception:
        return "n/a", "n/a"


def _collect_items(target_path, show_hidden):
    try:
        all_items = sorted(os.listdir(target_path))
    except OSError:
        return []

    items = []
    for item in all_items:
        if item in config.PROTECTED_FILES:
            continue
        if not show_hidden and item.startswith("."):
            continue
        items.append(item)
    return items


def _render_long_line(target_path, item):
    full_path = os.path.join(target_path, item)
    color = config.get_file_color(full_path)
    perms = _permission_string(full_path)
    try:
        st = os.stat(full_path)
        size = st.st_size
        mtime = time.strftime("%b %d %H:%M", time.localtime(st.st_mtime))
    except OSError:
        size = 0
        mtime = "?"
    owner, group = _owner_group(full_path)
    colored = f"{color}{item}{config.RESET}"
    return f"{perms} {owner:>8} {group:>8} {size:>8} {mtime} {colored}"


def _render_grid(items, target_path, show_hidden):
    if not items:
        return "(Folder kosong)"

    formatted_items = []
    raw_lengths = []
    for item in items:
        full_path = os.path.join(target_path, item)
        color = config.get_file_color(full_path)
        raw_lengths.append(len(item))
        if color:
            formatted_items.append(f"{color}{item}{config.RESET}")
        else:
            formatted_items.append(item)

    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80

    max_len = max(raw_lengths) + 3
    col_count = max(1, term_width // max_len)
    row_count = -(-len(items) // col_count)

    lines = []
    for r in range(row_count):
        line_str = ""
        for c in range(col_count):
            idx = r + c * row_count
            if idx < len(items):
                item_colored = formatted_items[idx]
                padding = max_len - raw_lengths[idx]
                line_str += item_colored + (" " * padding)
        lines.append(line_str)
    return "\n".join(lines)


def custom_ls(*args):
    """Tampilan 'ls' berkolom dengan penyaringan file proteksi & flag -a/-l."""
    show_hidden = config.CONFIG.get("hidden", False)
    long_mode = False
    target = "."

    for a in args:
        if a.startswith("-") and len(a) > 1 and not os.path.exists(a):
            for ch in a[1:]:
                if ch == "a":
                    show_hidden = True
                elif ch == "l":
                    long_mode = True
                elif ch == "h":
                    pass
                else:
                    print(f"ls: tidak mengenali opsi '-{ch}'")
                    return
        else:
            target = os.path.expanduser(a)

    if not os.path.exists(target):
        print(
            f"ls: tidak dapat mengakses '{target}': No such file or directory"
        )
        return

    if os.path.isfile(target):
        if os.path.basename(target) not in config.PROTECTED_FILES:
            print(target)
        return

    items = _collect_items(target, show_hidden)
    if long_mode:
        if not items:
            print("(Folder kosong)")
            return
        print(f"total {len(items)}")
        for item in items:
            print(_render_long_line(target, item))
    else:
        print(_render_grid(items, target, show_hidden))


def capture_ls(*args):
    """Versi ls yang mengembalikan output sebagai string (untuk pipe)."""
    show_hidden = config.CONFIG.get("hidden", False)
    long_mode = False
    target = "."

    for a in args:
        if a.startswith("-") and len(a) > 1 and not os.path.exists(a):
            for ch in a[1:]:
                if ch == "a":
                    show_hidden = True
                elif ch == "l":
                    long_mode = True
        else:
            target = os.path.expanduser(a)

    if not os.path.exists(target) or os.path.isfile(target):
        if os.path.isfile(target):
            return os.path.basename(target)
        return f"ls: tidak dapat mengakses '{target}'"

    items = _collect_items(target, show_hidden)
    if long_mode:
        lines = [f"total {len(items)}"]
        for item in items:
            lines.append(_render_long_line(target, item))
        return "\n".join(lines)
    return _render_grid(items, target, show_hidden)


def custom_tree(target=".", depth=0, prefix="", _level=0, _limit=50, _root=True):
    """Menampilkan struktur direktori dalam format pohon."""
    target = os.path.expanduser(target)
    if not os.path.isdir(target):
        print(f"tree: '{target}' bukan direktori.")
        return

    if _root:
        print(f"{config.BOLD}{target}{config.RESET}")

    if depth and _level >= depth:
        return

    try:
        raw_items = sorted(os.listdir(target))
    except OSError:
        return

    items = []
    for item in raw_items:
        if item in config.PROTECTED_FILES:
            continue
        if item.startswith("."):
            continue
        items.append(item)

    if _limit and len(items) > _limit:
        print(f"{prefix}{len(items) - _limit} item tersembunyi...")
        items = items[:_limit]

    for idx, item in enumerate(items):
        full_path = os.path.join(target, item)
        is_last = idx == len(items) - 1
        connector = "└── " if is_last else "├── "
        color = config.get_file_color(full_path)
        print(f"{prefix}{connector}{color}{item}{config.RESET}")
        if os.path.isdir(full_path):
            next_prefix = prefix + ("    " if is_last else "│   ")
            custom_tree(
                full_path, depth, next_prefix, _level + 1, _limit, _root=False
            )


# --- GIT WRAPPER SHORTCUTS ---
GIT_SHORTCUTS = {
    "gs": "git status",
    "ga": "git add -A",
    "gl": "git log --oneline",
    "gb": "git branch",
    "gd": "git diff",
    "gp": "git push",
    "gpl": "git pull",
    "gst": "git stash",
}


def run_git_shortcut(name, arg):
    """Menjalankan shortcut git. Mengembalikan True jika dikenali."""
    if name in GIT_SHORTCUTS:
        config.run_system_cmd_real_home(GIT_SHORTCUTS[name])
        return True
    elif name == "gc":
        if arg:
            config.run_system_cmd_real_home(f'git commit -m "{arg}"')
        else:
            print("Guna: gc <pesan_commit>")
        return True
    elif name == "gco":
        if arg:
            config.run_system_cmd_real_home(f'git checkout "{arg}"')
        else:
            print("Guna: gco <nama_branch>")
        return True
    elif name == "gclone":
        if arg:
            config.run_system_cmd_real_home(f'git clone "{arg}"')
        else:
            print("Guna: gclone <url_repo>")
        return True
    return False
