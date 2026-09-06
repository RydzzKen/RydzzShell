# -*- coding: utf-8 -*-
"""snippets — task runner: simpan & jalankan kumpulan perintah bernama.

Snippet disimpan di ~/.rydzz_home/.rydzz_snippets (JSON). Saat dijalankan,
placeholder $1..$n dan $@ disubstitusi lalu command dikirim ulang ke
handle_command shell, sehingga chaining/pipe/alias tetap berfungsi.
"""

import json
import os

from . import config
from .i18n import t

SNIPPETS_FILE = os.path.join(config.CUSTOM_HOME, ".rydzz_snippets")


def _load():
    if not os.path.exists(SNIPPETS_FILE):
        return {}
    try:
        with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(data):
    with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _expand(template, args):
    for i, a in enumerate(args, 1):
        template = template.replace(f"${i}", a)
    if args:
        template = template.replace("$@", " ".join(args))
    return template


def task(arg, runner=None):
    """runner adalah callback untuk menjalankan command hasil ekspansi."""
    parts = arg.split()
    data = _load()
    if not parts:
        print(t("kits.task.usage"))
        return

    op = parts[0]
    if op == "save":
        if len(parts) < 3:
            print(t("kits.task.save_usage"))
            return
        name = parts[1]
        tpl = " ".join(parts[2:]).strip()
        if len(tpl) >= 2 and tpl[0] == tpl[-1] and tpl[0] in "\"'":
            tpl = tpl[1:-1]
        data[name] = tpl
        _save(data)
        print(t("kits.task.saved", name=name))
    elif op == "del":
        name = parts[1] if len(parts) > 1 else ""
        if name in data:
            del data[name]
            _save(data)
            print(t("kits.task.deleted", name=name))
        else:
            print(t("kits.task.not_found", name=name))
    elif op in ("list", "ls"):
        if not data:
            print(t("kits.task.empty"))
            return
        print(t("kits.task.list_title"))
        for name, tpl in data.items():
            print(f"  {name:<14} {tpl}")
    elif op in data:
        expanded = _expand(data[op], parts[1:])
        print(f"$ {expanded}")
        if runner is not None:
            runner(expanded)
    else:
        print(t("kits.task.usage"))