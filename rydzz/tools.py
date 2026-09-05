import os
import shutil
import sys
from urllib.parse import urlparse

from . import config


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


def download_video(url, audio_only=False, dry_run=False):
    """Mengunduh video/audio dari URL medsos ke rydzzMedia/<Platform>/.

    URL Spotify tidak didukung oleh yt-dlp (DRM) — ditangani lewat
    `spotdl`, yang menerjemahkan ke sumber audio lalu mengunduhnya.
    Track/album/playlist Spotify didukung.
    """
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        print("yt-dlp tidak ditemukan. Install dulu: pip3 install -U yt-dlp")
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
    cmd.append("--no-playlist")
    if audio_only:
        cmd += ["-x", "--audio-format", "mp3"]
    cmd.append(url)

    print(f"Memproses video dari {platform}...")
    config.run_system_cmd_real_home(" ".join(f'"{c}"' for c in cmd))
    if not dry_run:
        print(f"Hasil disimpan di: {outdir}")
    return True


def _download_spotify(url, outdir, dry_run, yt_dlp):
    """Mengunduh lagu/album/playlist Spotify lewat spotdl.

    spotdl menolak menyimpan langsung ke direktori, jadi unduh ke temp,
    lalu pindahkan hasil (.mp3) ke outdir.
    """
    spotdl = shutil.which("spotdl")
    if not spotdl:
        print(
            "spotdl tidak ditemukan. Install dulu: pip3 install -U spotdl"
        )
        return False

    print("Spotify ber-DRM — diproses lewat spotdl (cari di sumber audio).")
    if dry_run:
        print(f"[dry-run] spotdl → {url}")
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
                print(f"Gagal memindahkan {f}: {e}")
    _cleanup_tmp(tmpdir)

    if moved:
        print(f"Berhasil: {moved} lagu disimpan di {outdir}")
    else:
        print("Tidak ada lagu yang terunduh (cek error spotdl di atas).")
    return True


def _cleanup_tmp(tmpdir):
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass


def list_downloads():
    """Menampilkan seluruh file yang sudah terunduh, dikelompok per platform."""
    if not os.path.exists(DL_ROOT):
        print(f"Belum ada download. Folder: {DL_ROOT}")
        return

    platforms = sorted(
        p
        for p in os.listdir(DL_ROOT)
        if os.path.isdir(os.path.join(DL_ROOT, p))
    )

    if not platforms:
        print(f"Folder {DL_ROOT} kosong.")
        return

    print(f"{config.PURPLE}{DL_ROOT}{config.RESET}")
    total = 0
    for platform in platforms:
        pdir = os.path.join(DL_ROOT, platform)
        files = sorted(
            f
            for f in os.listdir(pdir)
            if os.path.isfile(os.path.join(pdir, f))
        )
        if not files:
            continue
        color = config.get_file_color(pdir)
        print(f"  {color}{platform}{config.RESET}/")
        for f in files:
            print(f"    {f}")
            total += 1
    if total:
        print(f"Total: {total} file")


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
        print(
            "Library segno belum ada. Install dulu: pip3 install segno"
        )
        return False

    if not text:
        print("Guna: qr <teks> [-o file.png|file.svg]")
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
        print(f"QR disimpan di: {save_path}")
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
            return f"Error: '{p}' bukan angka basis {base}"
        except OverflowError:
            return f"Error: '{p}' di luar rentang"
    return "".join(out)