# -*- coding: utf-8 -*-
"""deploy — kirim project ke platform hosting lewat CLI (saat ini: Vercel).

Pola: output CLI deploy dilewatkan real-time (biar user lihat progres),
lalu setelah sukses `vercel ls` dijalankan & URL deployment terbaru
ditampilkan dalam kotak hijau.
"""

import os
import re
import shutil
import subprocess

from . import config
from .i18n import t

_VERCEL_BINS = ("vercel", "vercel.cmd", "vercel.exe")
_URL_RE = re.compile(r"https://[a-zA-Z0-9_-]+\.vercel\.app")


def vercel_available():
    """Cek apakah CLI vercel terpasang (lintas-platform)."""
    return any(shutil.which(bin) for bin in _VERCEL_BINS)


def vercel_executable():
    for bin in _VERCEL_BINS:
        exe = shutil.which(bin)
        if exe:
            return exe
    return None


def parse_vercel_args(tokens):
    """Urai argumen `vercel [path] [--prod] [--help]`.

    Mengembalikan dict: {path, prod, help}.
    """
    prod = False
    help_wanted = False
    positional = []
    for token in tokens:
        low = token.lower()
        if low in ("--prod", "-p", "--production"):
            prod = True
        elif low in ("--help", "-h"):
            help_wanted = True
        elif token.startswith("-"):
            continue
        else:
            positional.append(token)
    return {
        "path": positional[0] if positional else None,
        "prod": prod,
        "help": help_wanted,
    }


def resolve_target(path):
    """Path yang akan di-deploy: argumen (jika ada) atau cwd.

    Mengembalikan path absolut, atau None jika argumen bukan folder.
    """
    if path:
        target = os.path.abspath(os.path.expanduser(path))
        if not os.path.isdir(target):
            print(t("deploy.not_dir", path=path))
            return None
        return target
    return os.getcwd()


def build_vercel_command(target, prod):
    """Susun list argumen perintah vercel untuk dijalankan."""
    cmd = [vercel_executable(), "deploy", "--yes", target]
    if prod:
        cmd.append("--prod")
    return cmd


def _run_deploy(cmd):
    """Jalankan deploy dengan output real-time (HOME asli untuk auth)."""
    env = {**os.environ, "HOME": config.REAL_HOME}
    try:
        return subprocess.run(cmd, env=env).returncode
    except KeyboardInterrupt:
        print("\n^C")
        return None
    except OSError as e:
        print(t("deploy.failed", e=e))
        return None
    finally:
        config.reset_terminal()


def _is_authenticated():
    """Cek apakah Vercel CLI sudah login (vercel whoami sukses)."""
    exe = vercel_executable()
    if not exe:
        return False
    env = {**os.environ, "HOME": config.REAL_HOME}
    try:
        result = subprocess.run(
            [exe, "whoami"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _latest_urls():
    """Ambil daftar URL deployment terbaru via `vercel ls` (captured)."""
    env = {**os.environ, "HOME": config.REAL_HOME}
    try:
        result = subprocess.run(
            [vercel_executable(), "ls"],
            env=env, capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return _URL_RE.findall(result.stdout or "")


def _show_urls():
    """Tampilkan kotak hasil berisi URL deployment terbaru."""
    urls = _latest_urls()
    print()
    print(config.divider())
    print(t("deploy.done_title"))
    if urls:
        seen = set()
        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            print(f"  {config.GREEN_NEON}{url}{config.RESET}")
    else:
        print(t("deploy.no_url"))
    print(config.divider())


def vercel_deploy(argstr):
    """Entry point: `deploy vercel [path] [--prod] [--help]`."""
    opts = parse_vercel_args(argstr.split() if argstr else [])

    if opts["help"]:
        print(t("deploy.usage"))
        return 0

    if not vercel_available():
        print(t("deploy.vercel_missing"))
        print(t("deploy.install_hint"))
        return 1

    target = resolve_target(opts["path"])
    if not target:
        return 1

    # Guard: jangan biarkan 'deploy' tanpa tujuan men-deploy home sandbox
    home = os.path.abspath(config.CUSTOM_HOME)
    if target == home:
        print(t("deploy.home_warn_custom", home=target))
        print(config.wrap_text(t("deploy.usage")))
        return 1
    if target == os.path.abspath(config.REAL_HOME):
        print(t("deploy.home_warn_real", home=target))

    if not _is_authenticated():
        print(t("deploy.not_logged_in"))
        print(t("deploy.login_hint"))
        return 1

    mode = t("deploy.mode_prod") if opts["prod"] else t("deploy.mode_preview")
    print(t("deploy.starting", path=target, mode=mode))
    print()

    cmd = build_vercel_command(target, opts["prod"])
    code = _run_deploy(cmd)
    if code is None:
        return 1
    if code != 0:
        print(t("deploy.failed", e=t("deploy.exit_code", code=code)))
        return code

    _show_urls()
    return 0