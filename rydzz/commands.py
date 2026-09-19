import os
import re
import shutil
import signal
import stat
import subprocess
import time

from . import config
from .i18n import t

# Nama-nama flag yang didukung ls
VALID_LS_FLAGS = {
    "a": "sertakan hidden files",
    "A": "sertakan hidden files (tanpa . dan ..)",
    "l": "format panjang / detail",
    "F": "tambahkan indikator tipe (/ untuk direktori, dst.)",
    "C": "format kolom (default)",
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


def _classify_name(full_path, item):
    """Tambah indikator tipe ala GNU ls -F: / @ *."""
    try:
        if os.path.isdir(full_path):
            return item + "/"
        if os.path.islink(full_path):
            return item + "@"
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return item + "*"
    except OSError:
        pass
    return item


def _render_long_line(target_path, item, classify=False):
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
    display = _classify_name(full_path, item) if classify else item
    colored = f"{color}{display}{config.RESET}"
    return f"{perms} {owner:>8} {group:>8} {size:>8} {mtime} {colored}"


def _render_grid(items, target_path, show_hidden, classify=False):
    if not items:
        return t("ls.empty")

    formatted_items = []
    raw_lengths = []
    for item in items:
        full_path = os.path.join(target_path, item)
        color = config.get_file_color(full_path)
        display = _classify_name(full_path, item) if classify else item
        raw_lengths.append(len(display))
        if color:
            formatted_items.append(f"{color}{display}{config.RESET}")
        else:
            formatted_items.append(display)

    term_width = config.term_width()

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
    classify = False
    target = "."

    for a in args:
        if a.startswith("--color"):
            continue
        if a.startswith("-") and len(a) > 1 and not os.path.exists(a):
            for ch in a[1:]:
                if ch == "a" or ch == "A":
                    show_hidden = True
                elif ch == "l":
                    long_mode = True
                elif ch == "F":
                    classify = True
                elif ch == "C" or ch == "h" or ch == "G":
                    pass
                else:
                    print(t("ls.bad_flag", ch=ch))
                    return
        else:
            target = os.path.expanduser(a)

    if not os.path.exists(target):
        print(t("ls.no_access", target=target))
        return

    if os.path.isfile(target):
        if os.path.basename(target) not in config.PROTECTED_FILES:
            print(target)
        return

    items = _collect_items(target, show_hidden)
    if long_mode:
        if not items:
            print(t("ls.empty"))
            return
        print(f"total {len(items)}")
        for item in items:
            print(_render_long_line(target, item, classify))
    else:
        print(_render_grid(items, target, show_hidden, classify))


def capture_ls(*args):
    """Versi ls yang mengembalikan output sebagai string (untuk pipe)."""
    show_hidden = config.CONFIG.get("hidden", False)
    long_mode = False
    classify = False
    target = "."

    for a in args:
        if a.startswith("--color"):
            continue
        if a.startswith("-") and len(a) > 1 and not os.path.exists(a):
            for ch in a[1:]:
                if ch == "a" or ch == "A":
                    show_hidden = True
                elif ch == "l":
                    long_mode = True
                elif ch == "F":
                    classify = True
                elif ch == "C" or ch == "h" or ch == "G":
                    pass
        else:
            target = os.path.expanduser(a)

    if not os.path.exists(target) or os.path.isfile(target):
        if os.path.isfile(target):
            return os.path.basename(target)
        return t("ls.capture_noaccess", target=target)

    items = _collect_items(target, show_hidden)
    if long_mode:
        lines = [f"total {len(items)}"]
        for item in items:
            lines.append(_render_long_line(target, item, classify))
        return "\n".join(lines)
    return _render_grid(items, target, show_hidden, classify)


def custom_tree(target=".", depth=0, prefix="", _level=0, _limit=50, _root=True):
    """Menampilkan struktur direktori dalam format pohon."""
    target = os.path.expanduser(target)
    if not os.path.isdir(target):
        print(t("tree.not_dir", target=target))
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
        print(t("tree.items_hidden", prefix=prefix, n=len(items) - _limit))
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
            print(t("git.gc_usage"))
        return True
    elif name == "gco":
        if arg:
            config.run_system_cmd_real_home(f'git checkout "{arg}"')
        else:
            print(t("git.gco_usage"))
        return True
    elif name == "gclone":
        if arg:
            config.run_system_cmd_real_home(f'git clone "{arg}"')
        else:
            print(t("git.gclone_usage"))
        return True
    return False


# --- FF: FUZZY FIND ---
FF_SKIP_DIRS = {
    "node_modules", ".venv", "venv", ".idea", ".vscode", ".cache",
    ".tox", ".mypy_cache", ".ruff_cache", ".pytest_cache", "dist",
    "build", ".eggs", "site-packages",
}


def _fuzzy_score(text, query):
    """Skor pencocokan kasus-tidak-peduli: substring > subsequence."""
    text = text.lower()
    q = query.lower()
    if q in text:
        return 1000 - text.find(q)
    it = iter(text)
    if all(ch in it for ch in q):
        return 100
    return 0


def fuzzy_find(*args):
    """Cari file/folder secara fuzzy: ff <query> [-a] [path] [--max N]."""
    query = None
    start = "."
    limit = 30
    all_hidden = False
    rest = []
    i = 0
    while i < len(args):
        a = str(args[i])
        if a in ("-a", "--all"):
            all_hidden = True
        elif a.startswith("--max="):
            try:
                limit = int(a.split("=", 1)[1])
            except ValueError:
                pass
        elif a == "--max" and i + 1 < len(args):
            i += 1
            try:
                limit = int(args[i])
            except ValueError:
                pass
        else:
            rest.append(a)
        i += 1

    if not rest:
        print(t("ff.usage"))
        return
    query = rest[0]
    if len(rest) > 1:
        start = rest[1]
    if limit < 1:
        limit = 1

    start = os.path.expanduser(start or ".")
    if not os.path.isdir(start):
        print(t("ff.notdir", target=start))
        return

    results = []

    def walk(cur, rel):
        try:
            entries = sorted(os.listdir(cur))
        except OSError:
            return
        for name in entries:
            if name in config.PROTECTED_FILES:
                continue
            full = os.path.join(cur, name)
            is_dir = os.path.isdir(full)
            if is_dir and name in FF_SKIP_DIRS:
                continue
            if not all_hidden and name.startswith("."):
                continue
            score = _fuzzy_score(name, query)
            if score > 0:
                display = name if not rel else f"{rel}/{name}"
                results.append((score, display, full, is_dir))
            if is_dir:
                walk(full, name if not rel else f"{rel}/{name}")

    walk(start, "")
    if not results:
        print(t("ff.no_result", query=query))
        return

    results.sort(key=lambda r: r[0], reverse=True)
    for score, display, full, is_dir in results[:limit]:
        color = config.get_file_color(full)
        suffix = "/" if is_dir else ""
        print(f"{color}{display}{suffix}{config.RESET}")
    total = len(results)
    print(t("ff.summary", shown=min(total, limit), total=total, limit=limit))


# --- ALIAS DOCTOR ---
def alias_doctor():
    """Mendeteksi alias yang bisa rekursi tak hingga saat di-expand."""
    rydzz = dict(config.CONFIG.get("rydzz_aliases", {}))
    bashrc = dict(getattr(config, "USER_ALIASES", {}))
    merged = dict(rydzz)
    merged.update(bashrc)

    lines = [t("alias.doctor_title", total=len(merged), rydzz=len(rydzz), bashrc=len(bashrc))]

    def first_word(expansion):
        parts = expansion.split(maxsplit=1)
        return parts[0] if parts else ""

    healthy = []
    bad = []
    for name, value in sorted(merged.items()):
        seen = {name}
        steps = [value]
        word = first_word(value)
        while word in merged and word not in seen:
            seen.add(word)
            steps.append(merged[word])
            word = first_word(merged[word])
        if word in merged:
            bad.append((name, steps, word))
        else:
            healthy.append((name, value))

    lines.append(t("alias.doctor_sehat", n=len(healthy)))
    for name, value in healthy:
        lines.append(f"  ✓ {name} : '{value}'")

    lines.append(t("alias.doctor_bad", n=len(bad)))
    for name, steps, cycle_word in bad:
        arrow = " -> ".join(f"'{s}'" for s in steps)
        lines.append(f"  ⚠ {name}: {arrow}  {t('alias.doctor_loop', name=cycle_word)}")
    return lines


# --- PORT MANAGER ---
def _run_quiet(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL, text=True, errors="replace"
        )
    except Exception:
        return ""


def _parse_ss(out):
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if not parts or parts[0] == "State":
            continue
        m = re.search(r'"(.+?)",pid=(\d+)', line)
        proc = m.group(1) if m else "?"
        pid = int(m.group(2)) if m else 0
        local = parts[3] if len(parts) > 3 else "?"
        peer = parts[4] if len(parts) > 4 else ""
        rows.append((pid, proc, f"{local} {peer}".strip()))
    return rows


def _parse_lsof(out):
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if not parts or parts[0] == "COMMAND":
            continue
        if len(parts) < 3:
            continue
        proc = parts[0]
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        user = parts[2]
        detail = parts[-1]
        rows.append((pid, proc, f"{user} ({detail})"))
    return rows


def _lookup_port(port_s):
    try:
        port = int(port_s)
    except (TypeError, ValueError):
        print(t("port.usage"))
        return []
    if shutil.which("ss"):
        out = _run_quiet(f"ss -ltnp 'sport = :{port}'")
        return _parse_ss(out)
    if shutil.which("lsof"):
        out = _run_quiet(f"lsof -iTCP:{port} -sTCP:LISTEN -P -n")
        return _parse_lsof(out)
    print(t("port.no_tool"))
    return []


def port_list():
    """Daftar porta TCP yang sedang mendengarkan."""
    if shutil.which("ss"):
        out = _run_quiet("ss -ltnp")
        if not out.strip():
            return
        print(t("port.list_title"))
        for line in out.splitlines():
            parts = line.split()
            if not parts or parts[0] == "State" or len(parts) < 5:
                continue
            m = re.search(r'"(.+?)",pid=(\d+)', line)
            proc = f"  {m.group(1)} ({m.group(2)})" if m else ""
            print(f"  {parts[3]:<24} {parts[4]:<12}{proc}")
        return
    print(t("port.no_tool"))


def port_info(port_s):
    rows = _lookup_port(port_s)
    if not rows:
        print(t("port.free", port=port_s))
        return
    print(t("port.title", port=port_s))
    for pid, proc, detail in rows:
        pid_txt = str(pid) if pid else "?"
        print(f"  PID {pid_txt:<8} {proc:<12} {detail}")
    if len(rows) == 1 and rows[0][0]:
        print(t("port.hint", kill=f"port kill {port_s}"))


def port_kill(port_s):
    rows = _lookup_port(port_s)
    if not rows:
        print(t("port.free", port=port_s))
        return
    targets = [(pid, proc) for pid, proc, _ in rows if pid > 0]
    if not targets:
        print(t("port.no_pid", port=port_s))
        return
    for pid, proc in targets:
        try:
            ans = input(t("port.confirm", pid=pid, proc=proc)).strip().lower()
        except EOFError:
            ans = ""
        if ans not in ("y", "yes"):
            print(t("port.cancelled"))
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            print(f"kill {pid}: {e}")
            continue
        print(t("port.killed", pid=pid, proc=proc))


def port_handler(arg):
    """Gerbang perintah port: port | port list | port <no> | port kill <no>."""
    parts = arg.split()
    if not parts:
        port_list()
        return
    first = parts[0].lower()
    if first in ("list", "-l", "--list"):
        port_list()
        return
    if first == "kill":
        if len(parts) < 2:
            print(t("port.usage"))
            return
        port_kill(parts[1])
        return
    port_info(parts[0])
