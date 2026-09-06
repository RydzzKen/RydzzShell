import json
import os
import shutil
import sys
import time
from urllib.parse import urlparse

from . import config
from .i18n import t


def _default_download_dir():
    """Cari folder download bawaan yang berlaku di platform ini.

    Prioritas:
    1. Env var XDG_DOWNLOAD_DIR (Linux desktop)
    2. File user-dirs.dirs (kustomisasi per-user)
    3. Termux/Android shared storage (jika tersedia)
    4. Termux HOME/storage/downloads
    5. Fallback universal: ~/Downloads
    """
    # 1. Env var langsung
    env_dir = os.environ.get("XDG_DOWNLOAD_DIR")
    if env_dir:
        return env_dir.replace("$HOME", config.REAL_HOME)

    # 2. File user-dirs.dirs (Linux desktop)
    xdg = os.path.join(config.REAL_HOME, ".config", "user-dirs.dirs")
    if os.path.exists(xdg):
        try:
            with open(xdg) as f:
                for line in f:
                    if line.startswith("XDG_DOWNLOAD_DIR="):
                        val = line.split("=", 1)[1].strip().strip('"')
                        if val:
                            return val.replace("$HOME", config.REAL_HOME)
        except Exception:
            pass

    # 3. Termux / Android
    if os.environ.get("PREFIX"):  # Termux selalu set $PREFIX
        for candidate in (
            "/sdcard/Download",
            "/storage/emulated/0/Download",
        ):
            if os.path.isdir(candidate) and os.access(
                candidate, os.W_OK
            ):
                return candidate
        termux_storage = os.path.join(
            config.REAL_HOME, "storage", "downloads"
        )
        if os.path.isdir(termux_storage):
            return termux_storage
        # Fallback di dalam home Termux (dibuat otomatis)
        return os.path.join(config.REAL_HOME, "Downloads")

    # 4. Windows / macOS / Linux umum
    return os.path.join(config.REAL_HOME, "Downloads")


DOWNLOAD_DIR = _default_download_dir()

# --- DOWNLOADER ---
DL_ROOT = os.path.join(DOWNLOAD_DIR, "rydzzMedia")

# Indeks unduhan (URL sumber) agar bisa re-download dari daftar tanpa hafal URL
INDEX_FILE = os.path.join(DL_ROOT, ".rydzz_index.json")
_INDEX_LIMIT = 500


def _load_index():
    """Membaca indeks unduhan (list {url, platform, time})."""
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            entries = json.load(f)
        return entries if isinstance(entries, list) else []
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return []


def _save_index(entries):
    try:
        os.makedirs(DL_ROOT, exist_ok=True)
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(entries[-_INDEX_LIMIT:], f, ensure_ascii=False, indent=1)
    except OSError:
        pass


def _record_download(url, platform):
    """Catat keberhasilan unduhan untuk dipakai `dl redo`."""
    entries = [e for e in _load_index() if e.get("url") != url]
    entries.insert(0, {
        "url": url,
        "platform": platform,
        "time": time.strftime("%Y-%m-%d %H:%M"),
    })
    _save_index(entries)

PLATFORM_MAP = [
    ("youtube.com", "YouTube"),
    ("youtu.be", "YouTube"),
    ("youtube-nocookie.com", "YouTube"),
    ("music.youtube.com", "YouTube"),
    ("tiktok.com", "TikTok"),
    ("vm.tiktok", "TikTok"),
    ("instagram.com", "Instagram"),
    ("twitter.com", "X"),
    ("x.com", "X"),
    ("facebook.com", "Facebook"),
    ("fb.watch", "Facebook"),
    ("reddit.com", "Reddit"),
    ("redd.it", "Reddit"),
    ("twitch.tv", "Twitch"),
    ("bilibili.com", "Bilibili"),
    ("b23.tv", "Bilibili"),
    ("soundcloud.com", "SoundCloud"),
    ("dailymotion.com", "Dailymotion"),
    ("vimeo.com", "Vimeo"),
    ("pinterest", "Pinterest"),
    ("rumble.com", "Rumble"),
    ("odysee.com", "Odysee"),
    ("likee.com", "Likee"),
    ("snapchat.com", "Snapchat"),
    ("telegram.app", "Telegram"),
    ("t.me", "Telegram"),
    ("discord", "Discord"),
    ("spotify.com", "Spotify"),
    ("open.spotify", "Spotify"),
    ("twitcasting.tv", "TwitCasting"),
    ("streamable.com", "Streamable"),
]

# Host Spotify → diselesaikan lewat pencarian YouTube
SPOTIFY_HOSTS = ("spotify.com", "open.spotify", "spotify.link")

# Logo tiap platform untuk header unduhan / daftar
PLATFORM_ICONS = {
    "YouTube": "📺",
    "TikTok": "🎵",
    "Instagram": "📸",
    "X": "🐦",
    "Facebook": "👍",
    "Reddit": "🤖",
    "Twitch": "🎮",
    "Bilibili": "🦊",
    "SoundCloud": "🎧",
    "Dailymotion": "▶",
    "Vimeo": "🎬",
    "Pinterest": "📌",
    "Rumble": "🥊",
    "Odysee": "📼",
    "Likee": "✨",
    "Snapchat": "👻",
    "Telegram": "📨",
    "Discord": "💬",
    "Spotify": "🎵",
    "TwitCasting": "🎥",
    "Lainnya": "📁",
}


def platform_icon(platform):
    return PLATFORM_ICONS.get(platform, "🌐")


def platform_label(platform):
    """Nama platform dengan logo (ikon) di depannya."""
    return f"{platform_icon(platform)} {platform}"


def _platform_dir(url):
    host = urlparse(url).netloc.lower()
    for fragment, name in PLATFORM_MAP:
        if fragment in host:
            return name
    return "Lainnya"


def _ensure_dl_dirs(platform):
    outdir = os.path.join(DL_ROOT, platform)
    os.makedirs(outdir, exist_ok=True)
    return outdir


def _human_size(num):
    """Format ukuran bytes jadi B/KB/MB/GB/TB."""
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(num)} {unit}"
            return f"{num:.1f} {unit}"
        num /= 1024
    return "?"


def _url_display(url, width=55):
    """Url pendek untuk ditampilkan di header batch."""
    try:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        host = parsed.netloc or url.split("/")[0]
        compact = f"{host}/{path}" if path else host
    except Exception:
        compact = url
    if len(compact) <= width:
        return compact
    return compact[: width - 3] + "..."


def download_video(url, audio_only=False, dry_run=False, force=False):
    """Mengunduh video/audio dari URL medsos ke rydzzMedia/<Platform>/.

    URL Spotify tidak didukung oleh yt-dlp (DRM) — ditangani lewat
    `spotdl`, yang menerjemahkan ke sumber audio lalu mengunduhnya.
    Track/album/playlist Spotify didukung.
    `force=True` mengunduh ulang walau file sudah ada (--force-overwrites).
    """
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        print(t("dl.ytdlp_missing"))
        return False

    platform = _platform_dir(url)
    is_spotify = any(h in url for h in SPOTIFY_HOSTS)
    outdir = _ensure_dl_dirs(platform)

    if is_spotify:
        return _download_spotify(url, outdir, dry_run, yt_dlp)

    cmd = [
        yt_dlp,
        "-o",
        os.path.join(outdir, "%(title)s.%(ext)s"),
        "--restrict-filenames",
    ]
    if dry_run:
        cmd.append("--simulate")
    if force:
        cmd.append("--force-overwrites")
    if audio_only:
        cmd += ["-x", "--audio-format", "mp3"]
    cmd.append(url)

    print(t("dl.processing", platform=platform_label(platform)))
    rc = config.run_system_cmd_real_home(" ".join(f'"{c}"' for c in cmd))
    if rc != 0:
        print(t("dl.failed"))
        return False
    if not dry_run:
        _record_download(url, platform)
        print(t("dl.saved_to", outdir=outdir))
    return True


def _download_spotify(url, outdir, dry_run, yt_dlp):
    """Mengunduh lagu/album/playlist Spotify lewat spotdl.

    spotdl menolak menyimpan langsung ke direktori, jadi unduh ke temp,
    lalu pindahkan hasil (.mp3) ke outdir.
    """
    spotdl = shutil.which("spotdl")
    if not spotdl:
        print(t("dl.spotdl_missing"))
        return False

    print(t("dl.spotify_drm"))
    if dry_run:
        print(t("dl.dry_run", url=url))
        return True

    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="rydzz_spot_")
    cmd = [
        spotdl,
        "--output",
        os.path.join(tmpdir, "{artist} - {title}.{output-ext}"),
        url,
    ]
    config.run_system_cmd_real_home(" ".join(f'"{c}"' for c in cmd))

    # Pindahkan hasil .mp3 dari temp ke outdir
    moved = 0
    for f in os.listdir(tmpdir):
        src = os.path.join(tmpdir, f)
        if os.path.isfile(src) and f.lower().endswith(".mp3"):
            dst = os.path.join(outdir, f)
            try:
                import shutil as _sh

                _sh.move(src, dst)
                moved += 1
            except Exception as e:
                print(t("dl.move_failed", f=f, e=e))
    _cleanup_tmp(tmpdir)

    if moved:
        _record_download(url, "Spotify")
        print(t("dl.spotify_ok", n=moved, outdir=outdir))
    else:
        print(t("dl.spotify_none"))
    return True


def _cleanup_tmp(tmpdir):
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass


def download_batch(urls, audio_only=False, dry_run=False, force=False):
    """Mengunduh beberapa URL sekaligus dengan header [i/N] per item.

    Jika hanya satu URL, langsung diteruskan ke download_video (agar
    tampilan tetap konsisten dengan unduhan tunggal).
    """
    urls = [u.strip() for u in urls if u.strip()]
    if not urls:
        return False

    if len(urls) == 1:
        return download_video(
            urls[0], audio_only=audio_only, dry_run=dry_run, force=force
        )

    total = len(urls)
    ok = failed = 0
    print(
        t(
            "dl.batch_title",
            bold=config.BOLD,
            cyan=config.CYAN,
            reset=config.RESET,
            total=total,
        )
    )
    for i, url in enumerate(urls, 1):
        platform = _platform_dir(url)
        header = (
            f"  [{i}/{total}] {config.MAGENTA}{platform_label(platform)}{config.RESET} "
            f"→ {_url_display(url)}"
        )
        print(header)
        try:
            result = download_video(url, audio_only, dry_run, force)
        except KeyboardInterrupt:
            print(
                t(
                    "dl.batch_cancel",
                    red=config.RED,
                    reset=config.RESET,
                    i=i,
                )
            )
            break
        if result:
            ok += 1
        else:
            failed += 1

    total_sukses = ok
    total_gagal = failed
    if total_gagal:
        print(
            t(
                "dl.summary",
                red=config.RED,
                green=config.GREEN_NEON,
                reset=config.RESET,
                failed=total_gagal,
                ok=total_sukses,
            )
        )
    else:
        print(
            t(
                "dl.all_success",
                green=config.GREEN_NEON,
                reset=config.RESET,
                total=total_sukses,
            )
        )
    return total_gagal == 0


def redownload(args):
    """Unduh ulang dari indeks: `dl redo` (daftar) | `dl redo <nomor|url>`."""
    entries = _load_index()

    if not args:
        if not entries:
            print(t("dl.how_redo"))
            return False
        print(t("dl.redo_list_title"))
        for i, e in enumerate(entries, 1):
            print(
                f"  {i:>3}. {config.MAGENTA}{platform_label(e.get('platform', '?'))}{config.RESET}"
                f"  {_url_display(e.get('url', ''), 60)}  "
                f"{config.DIM}{e.get('time', '')}{config.RESET}"
            )
        print(t("dl.redo_use_url"))
        return True

    targets = []
    for a in args:
        if a.isdigit():
            i = int(a)
            if 1 <= i <= len(entries):
                targets.append(entries[i - 1]["url"])
            else:
                print(t("dl.redo_num_missing", n=a))
                return False
        else:
            targets.append(a)
    return download_batch(targets, force=True)


def list_downloads(opts=None):
    """Menampilkan seluruh file ter-unduh dengan kolom adaptif.

    Opsi:
      -n <N> / -n<N>  hanya tampilkan N file terbaru
      -s / --sort-size  urutkan dari ukuran terbesar
    """
    opts = opts or []
    limit = None
    sort_size = False
    i = 0
    while i < len(opts):
        o = opts[i]
        if o in ("-n", "--newest"):
            if i + 1 < len(opts) and opts[i + 1].isdigit():
                limit = int(opts[i + 1])
                i += 2
                continue
        elif o.startswith("-n") and o[2:].isdigit():
            limit = int(o[2:])
        elif o in ("-s", "--sort-size"):
            sort_size = True
        elif o in ("-h", "--help"):
            print(t("dl.list_usage"))
            print(t("dl.list_opt_n"))
            print(t("dl.list_opt_s"))
            return
        i += 1

    if not os.path.exists(DL_ROOT):
        print(t("dl.none_yet", dir=DL_ROOT))
        return

    platforms = sorted(
        p
        for p in os.listdir(DL_ROOT)
        if os.path.isdir(os.path.join(DL_ROOT, p))
    )

    entries = []
    for platform in platforms:
        pdir = os.path.join(DL_ROOT, platform)
        for f in os.listdir(pdir):
            full = os.path.join(pdir, f)
            if not os.path.isfile(full):
                continue
            try:
                size = os.path.getsize(full)
                mtime = os.path.getmtime(full)
            except OSError:
                size, mtime = 0, 0
            entries.append((platform, f, size, mtime))

    if not entries:
        print(t("dl.folder_empty", dir=DL_ROOT))
        return

    if sort_size:
        entries.sort(key=lambda e: (-e[2], e[1]))
    else:
        entries.sort(key=lambda e: (-e[3], e[1]))
    if limit:
        entries = entries[:limit]

    total_size = sum(e[2] for e in entries)
    print(
        t(
            "dl.summary_line",
            purple=config.PURPLE,
            reset=config.RESET,
            n=len(entries),
            size=_human_size(total_size),
        )
    )

    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80
    name_width = max(len(e[1]) for e in entries)
    name_width = min(name_width, max(12, term_width - 26))
    fmt = f"  {{:<{name_width}}}  {{:>9}}  {{}}"

    print(fmt.format(t("dl.col_name"), t("dl.col_size"), t("dl.col_platform")))
    print("  " + "-" * max(12, term_width - 2))

    for platform, fname, size, _mtime in entries:
        full = os.path.join(DL_ROOT, platform, fname)
        color = config.get_file_color(full)
        shown = fname if len(fname) <= name_width else fname[: name_width - 3] + "..."
        print(
            fmt.format(
                f"{color}{shown}{config.RESET}",
                _human_size(size),
                platform_label(platform),
            )
        )


def update_ytdlp():
    """Memperbarui yt-dlp."""

    config.run_system_cmd_real_home("pip3 install -U yt-dlp")


# --- QR GENERATOR ---
QR_DIR = DOWNLOAD_DIR


def _qr_terminal_render(qr):
    """Render matrix QR ke terminal memakai block character."""
    modules = qr.matrix

    rows = []
    dark = "██"
    light = "  "
    for row in modules:
        rows.append("".join(dark if cell else light for cell in row))
    return "\n".join(rows)


def gen_qr(text, out_file=None):
    """Menampilkan QR ke terminal atau menyimpannya sebagai file."""
    try:
        import segno
    except ImportError:
        print(t("qr.segno_missing"))
        return False

    if not text:
        print(t("qr.usage"))
        return False

    qr = segno.make_qr(text)

    # Selalu tampilkan QR di layar
    print(f"{config.BLUE}{text}{config.RESET}")
    print(_qr_terminal_render(qr))

    if out_file:
        # Simpan ke folder ~/download (real home); path absolut dipakai apa adanya
        if os.path.isabs(out_file):
            save_path = out_file
        else:
            os.makedirs(QR_DIR, exist_ok=True)
            save_path = os.path.join(QR_DIR, os.path.basename(out_file))
        ext = os.path.splitext(save_path)[1].lower()
        if ext == ".svg":
            qr.save(save_path, kind="svg")
        else:
            qr.save(save_path, kind="png")
        print(t("qr.saved", path=save_path))
    return True


# --- ASCII ENCODE / DECODE ---
def _parse_ascii_flags(args):
    base = 10
    label = "desimal"
    remaining = []
    for a in args:
        if a == "-x" or a == "--hex":
            base, label = 16, "hex"
        elif a == "-b" or a == "--bin":
            base, label = 2, "biner"
        elif a == "-d" or a == "--dec":
            base, label = 10, "desimal"
        else:
            remaining.append(a)
    return base, label, remaining


def ascii_encode(text, base=10):
    if base == 2:
        return " ".join(format(ord(c), "08b") for c in text)
    if base == 16:
        return " ".join(format(ord(c), "02x") for c in text)
    return " ".join(str(ord(c)) for c in text)


def ascii_decode(codes, base=10):
    parts = codes.replace(",", " ").split()
    out = []
    for p in parts:
        try:
            out.append(chr(int(p, base)))
        except ValueError:
            return t("ascii.decode_invalid", p=p, base=base)
        except OverflowError:
            return t("ascii.decode_range", p=p)
    return "".join(out)