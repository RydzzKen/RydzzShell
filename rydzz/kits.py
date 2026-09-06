# -*- coding: utf-8 -*-
"""kits — alat bantu harian zero-dependency: trash, backup, hash, freq,
clip, todo, serve, pick. Semua output lewat i18n (t())."""

import hashlib
import os
import shutil
import subprocess
import sys
import time
from collections import Counter

from . import config
from .i18n import t

TRASH_DIR = os.path.join(config.CUSTOM_HOME, ".trash")
BACKUP_DIR = os.path.join(config.CUSTOM_HOME, ".backups")
TODO_FILE = os.path.join(config.CUSTOM_HOME, ".rydzz_todo")

HASH_ALGOS = ("md5", "sha1", "sha256", "sha512")


# ---------- helper kecil ----------
def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def _human_size(n):
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"


def _unique_dest(dest_dir, name):
    dest = os.path.join(dest_dir, name)
    if not os.path.exists(dest):
        return dest
    stem, ext = os.path.splitext(name)
    i = 2
    while True:
        cand = os.path.join(dest_dir, f"{stem}_{i}{ext}")
        if not os.path.exists(cand):
            return cand
        i += 1


# ---------- trash ----------
def trash(arg):
    args = arg.split()
    if not args:
        print(t("kits.trash.usage"))
        return
    op = args[0]
    if op == "list":
        trash_list()
    elif op == "restore":
        trash_restore(args[1:])
    elif op == "empty":
        trash_empty()
    else:
        trash_items(args)


def trash_items(paths):
    _ensure_dir(TRASH_DIR)
    for p in paths:
        src = os.path.abspath(os.path.expanduser(p))
        if not os.path.exists(src):
            print(t("kits.trash.not_found", path=p))
            continue
        if config.is_protected(src):
            print(t("kits.trash.protected", path=p))
            continue
        dest = _unique_dest(TRASH_DIR, os.path.basename(src))
        shutil.move(src, dest)
        print(t("kits.trash.moved", src=p, dst=os.path.basename(dest)))


def _trash_items():
    if not os.path.isdir(TRASH_DIR):
        return []
    return sorted(os.listdir(TRASH_DIR))


def trash_list():
    items = _trash_items()
    if not items:
        print(t("kits.trash.empty"))
        return
    for i, name in enumerate(items, 1):
        print(f"  {i}. {name}")
    print(t("kits.trash.restore_hint"))


def trash_restore(sel):
    items = _trash_items()
    if not sel:
        print(t("kits.trash.restore_usage"))
        return
    for s in sel:
        if s.isdigit():
            n = int(s)
            if not (1 <= n <= len(items)):
                print(t("kits.trash.invalid_index", n=s))
                continue
            name = items[n - 1]
        else:
            name = os.path.basename(s)
        src = os.path.join(TRASH_DIR, name)
        if not os.path.exists(src):
            print(t("kits.trash.not_in_trash", name=s))
            continue
        dest = os.path.join(os.getcwd(), name)
        if os.path.exists(dest):
            dest = _unique_dest(os.getcwd(), name)
        shutil.move(src, dest)
        print(t("kits.trash.restored", name=name))


def trash_empty():
    shutil.rmtree(TRASH_DIR, ignore_errors=True)
    print(t("kits.trash.cleared"))


# ---------- backup (bk) ----------
def backup(arg):
    args = arg.split()
    if not args:
        print(t("kits.bk.usage"))
        return
    op = args[0]
    if op == "list":
        bk_list()
    elif op == "restore":
        bk_restore(args[1:])
    else:
        bk_items(args)


def _ts():
    return time.strftime("%Y%m%d_%H%M%S")


def bk_items(paths):
    _ensure_dir(BACKUP_DIR)
    stamp = _ts()
    for p in paths:
        src = os.path.abspath(os.path.expanduser(p))
        if not os.path.exists(src):
            print(t("kits.bk.not_found", path=p))
            continue
        base = os.path.basename(src)
        dest_dir = os.path.join(BACKUP_DIR, f"{base}_{stamp}")
        if os.path.isdir(src):
            shutil.copytree(src, dest_dir)
        else:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(src, os.path.join(dest_dir, base))
        with open(os.path.join(dest_dir, ".bak_name"), "w", encoding="utf-8") as f:
            f.write(base)
        print(t("kits.bk.backed", src=p, dest=dest_dir))


def _bk_items():
    if not os.path.isdir(BACKUP_DIR):
        return []
    return sorted(os.listdir(BACKUP_DIR))


def _item_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def bk_list():
    items = _bk_items()
    if not items:
        print(t("kits.bk.empty"))
        return
    for i, name in enumerate(items, 1):
        size = _item_size(os.path.join(BACKUP_DIR, name))
        print(f"  {i}. {name}  ({_human_size(size)})")
    print(t("kits.bk.restore_hint"))


def _bak_orig_name(src_dir, fallback):
    meta = os.path.join(src_dir, ".bak_name")
    if os.path.isfile(meta):
        try:
            with open(meta, "r", encoding="utf-8") as f:
                name = f.read().strip()
            if name:
                return name
        except OSError:
            pass
    return fallback


def bk_restore(sel):
    items = _bk_items()
    if not sel:
        print(t("kits.bk.restore_usage"))
        return
    for s in sel:
        if not s.isdigit():
            print(t("kits.bk.invalid_index", n=s))
            continue
        n = int(s)
        if not (1 <= n <= len(items)):
            print(t("kits.bk.invalid_index", n=s))
            continue
        name = items[n - 1]
        src = os.path.join(BACKUP_DIR, name)
        orig_name = _bak_orig_name(src, name.rsplit("_", 1)[0])
        dest = os.path.join(os.getcwd(), orig_name)
        if os.path.exists(dest):
            dest = _unique_dest(os.getcwd(), orig_name)
        inner = os.path.join(src, orig_name)
        if os.path.isfile(inner):
            shutil.copy2(inner, dest)
        elif os.path.isdir(src):
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".bak_name"))
        else:
            shutil.copy2(src, dest)
        print(t("kits.bk.restored", name=name, dest=dest))


# ---------- hash ----------
def hashit(arg):
    algo = "sha256"
    target = arg.strip().strip("'\"")
    rest = arg.split()
    if rest and rest[0] == "-a":
        if len(rest) < 3:
            print(t("kits.hash.usage"))
            return
        algo = rest[1].lower()
        target = " ".join(rest[2:]).strip("\"'")
    if algo not in HASH_ALGOS:
        print(t("kits.hash.unknown_algo", algo=algo))
        return
    h = hashlib.new(algo)
    if target and os.path.isfile(os.path.expanduser(target)):
        with open(os.path.expanduser(target), "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        print(f"{algo:<8}: {h.hexdigest()}  {target}")
    else:
        h.update(target.encode("utf-8"))
        print(f"{algo:<8}: {h.hexdigest()}  \"{target}\"")


# ---------- freq ----------
def freq(arg):
    n = 10
    args = arg.split()
    if args:
        try:
            n = int(args[0])
        except ValueError:
            print(t("kits.freq.invalid_n", n=args[0]))
            return
    if not os.path.exists(config.HISTORY_FILE):
        print(t("kits.freq.empty"))
        return
    with open(config.HISTORY_FILE, "r", encoding="utf-8", errors="replace") as f:
        commands = [ln.strip() for ln in f if ln.strip()]
    if not commands:
        print(t("kits.freq.empty"))
        return
    counts = Counter(cmd.split()[0] if cmd.split() else cmd for cmd in commands)
    items = counts.most_common(n)
    maxc = max(c for _, c in items) or 1
    print(t("kits.freq.title", n=len(items)))
    for name, cnt in items:
        bar = "█" * max(1, round(cnt / maxc * 20))
        print(f"  {name:<14} {cnt:>4}  {bar}")


# ---------- clip ----------
def _copy(text):
    if os.name == "nt":
        print(t("kits.clip.no_backend"))
        return False
    if shutil.which("termux-clipboard-set"):
        subprocess.run(["termux-clipboard-set"], input=text, text=True)
    elif shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text, text=True)
    elif shutil.which("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True)
    elif shutil.which("xsel"):
        subprocess.run(["xsel", "-b", "-i"], input=text, text=True)
    elif shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input=text, text=True)
    else:
        print(t("kits.clip.no_backend"))
        return False
    print(t("kits.clip.copied"))
    return True


def _paste():
    if os.name == "nt":
        print(t("kits.clip.no_backend"))
        return
    for prog in (
        ("termux-clipboard-get",),
        ("wl-paste",),
        ("xclip", "-selection", "clipboard", "-o"),
        ("xsel", "-b", "-o"),
        ("pbpaste",),
    ):
        if shutil.which(prog[0]):
            try:
                out = subprocess.run(
                    list(prog), capture_output=True, text=True, timeout=3
                ).stdout
            except Exception:
                out = ""
            print(out.rstrip("\n") or t("kits.clip.empty"))
            return
    print(t("kits.clip.no_backend"))


def clip(arg):
    parts = arg.split(maxsplit=1)
    op = parts[0] if parts else "get"
    payload = parts[1] if len(parts) > 1 else ""
    if op == "set":
        if not payload:
            print(t("kits.clip.usage"))
            return
        _copy(payload)
    elif op == "file":
        p = os.path.expanduser(payload)
        if not (payload and os.path.isfile(p)):
            print(t("kits.clip.not_found", path=payload))
            return
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                _copy(f.read())
        except OSError:
            print(t("kits.clip.not_found", path=payload))
    elif op == "get":
        _paste()
    else:
        print(t("kits.clip.usage"))


# ---------- todo ----------
def _read_todo():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def _write_todo(items):
    if items:
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(items) + "\n")
    elif os.path.exists(TODO_FILE):
        os.remove(TODO_FILE)


def _parse_indexes(payload, size):
    out = []
    for s in payload.split():
        if s.isdigit():
            n = int(s)
            if 1 <= n <= size:
                out.append(n)
    return out


def todo(arg):
    args = arg.split(maxsplit=1)
    op = args[0] if args else "list"
    payload = args[1] if len(args) > 1 else ""
    items = _read_todo()
    if op == "add":
        if not payload:
            print(t("kits.todo.add_usage"))
            return
        items.append(payload)
        _write_todo(items)
        print(t("kits.todo.added", n=len(items)))
    elif op == "list":
        if not items:
            print(t("kits.todo.empty"))
            return
        for i, item in enumerate(items, 1):
            done = item.startswith("[x] ")
            text = item[4:] if done else item
            mark = "✓" if done else " "
            print(f"  {mark} {i}. {text}")
    elif op == "done":
        for n in _parse_indexes(payload, len(items)):
            if not items[n - 1].startswith("[x] "):
                items[n - 1] = "[x] " + items[n - 1]
        _write_todo(items)
        todo("list")
    elif op == "undone":
        for n in _parse_indexes(payload, len(items)):
            items[n - 1] = items[n - 1][4:] if items[n - 1].startswith("[x] ") else items[n - 1]
        _write_todo(items)
    elif op == "del":
        idxs = _parse_indexes(payload, len(items))
        for n in sorted(idxs, reverse=True):
            del items[n - 1]
        _write_todo(items)
        todo("list")
    elif op == "clear":
        _write_todo([])
        print(t("kits.todo.cleared"))
    else:
        print(t("kits.todo.usage"))


# ---------- serve ----------
def _lan_ip():
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def serve(arg):
    args = arg.split()
    port = 8000
    target = "."
    background = False
    for a in args:
        if a in ("-b", "--background"):
            background = True
        elif a.isdigit():
            port = int(a)
        else:
            target = a
    if not os.path.isdir(target):
        print(t("kits.serve.not_dir", path=target))
        return
    ip = _lan_ip()
    print(t("kits.serve.banner", ip=ip, port=port, green=config.GREEN_NEON, reset=config.RESET))
    print(t("kits.serve.hint_local", port=port))
    print(t("kits.serve.hint_net", ip=ip, port=port))
    cmd = [sys.executable, "-m", "http.server", str(port), "--directory", target]
    if background:
        DEVNULL = getattr(subprocess, "DEVNULL", None) or open(os.devnull, "w")
        subprocess.Popen(
            cmd, stdout=DEVNULL, stderr=DEVNULL,
            start_new_session=True,
        )
        print(t("kits.serve.background"))
    else:
        print(t("kits.serve.stop_hint"))
        config.run_system_cmd(" ".join(f'"{c}"' for c in cmd))


# ---------- pick ----------
def _fuzzy_score(text, query):
    if not query:
        return 1
    text = text.lower()
    q = query.lower()
    pos = 0
    last = -2
    bonus = 0
    for ch in q:
        idx = text.find(ch, pos)
        if idx == -1:
            return 0
        if idx == last + 1:
            bonus += 2
        elif idx == last:
            bonus += 1
        last = idx
        pos = idx + 1
    if text.startswith(q):
        bonus += 10
    return bonus * 3 - len(text) * 0.01


def _collect_entries(limit=500):
    hidden = config.CONFIG.get("hidden", False)
    entries = []
    base = os.getcwd()
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if hidden or not d.startswith(".")]
        for name in files:
            if not hidden and name.startswith("."):
                continue
            rel = os.path.relpath(os.path.join(root, name), base)
            entries.append(rel)
            if len(entries) >= limit:
                return entries
    return entries


def pick(arg):
    query = arg.strip()
    entries = _collect_entries()
    if query:
        scored = [( _fuzzy_score(e, query), e) for e in entries]
        scored.sort(key=lambda x: (-x[0], len(x[1])))
        cands = [e for s, e in scored if s > 0][:20] or entries[:20]
    else:
        cands = entries[:20]
    if not cands:
        print(t("kits.pick.empty"))
        return
    for i, e in enumerate(cands, 1):
        print(f"  {i}. {e}")
    try:
        choice = int(input(t("kits.pick.prompt")).strip())
    except (ValueError, KeyboardInterrupt):
        print()
        return
    if 1 <= choice <= len(cands):
        print(cands[choice - 1])
    else:
        print(t("kits.pick.invalid"))