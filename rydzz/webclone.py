import gzip
import html.parser
import io
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from urllib.parse import urljoin, urlparse, urlsplit, unquote
from urllib.request import Request, urlopen

from . import config, tools
from .i18n import t

WEB_ROOT = os.path.join(tools.DOWNLOAD_DIR, "rydzzWeb")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

MAX_ASSETS = 200
TIMEOUT = 15

_CSS_URL_RE = re.compile(
    r"url\(\s*(?:'([^']*)'|\"([^\"]*)\"|([^)\s]*))\s*\)",
    re.IGNORECASE,
)

_SKIP_SCHEMES = ("data:", "javascript:", "mailto:", "tel:", "about:", "#")


class _AssetCollector(html.parser.HTMLParser):
    """Mengumpulkan daftar resource (CSS/JS/img/media) dari satu HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.resources = {}

    def _add(self, kind, location):
        self.resources.setdefault(kind, set()).add(location)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "link":
            rel = (attrs.get("rel", "") or "").lower()
            href = attrs.get("href")
            stylesheet = "stylesheet" in rel
            preload = "preload" in rel or "prefetch" in rel
            icon = (
                rel
                and any(
                    r in rel
                    for r in (
                        "icon",
                        "apple-touch-icon",
                        "mask-icon",
                        "manifest",
                    )
                )
            )
            if href and (stylesheet or preload or icon):
                kind = "css" if stylesheet else "other"
                self._add(kind, href)
        elif tag == "script":
            src = attrs.get("src")
            if src:
                self._add("js", src)
        elif tag == "img":
            src = attrs.get("src")
            if src:
                self._add("img", src)
        elif tag in ("audio", "video", "embed"):
            src = attrs.get("src")
            if src:
                self._add("media", src)
        elif tag == "source":
            src = attrs.get("src") or attrs.get("srcset")
            if src:
                for part in src.split(","):
                    piece = part.strip().split()[0]
                    if piece:
                        self._add("media", piece)
        elif tag == "iframe":
            src = attrs.get("src")
            if src:
                self._add("media", src)


def _fetch(url):
    """Mengambil konten URL sebagai bytes, menangani gzip sekaligus."""
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    with urlopen(req, timeout=TIMEOUT) as resp:
        data = resp.read()
        info = resp.headers
        encoding = info.get("Content-Encoding", "")
        charset = info.get_content_charset()
        if "gzip" in encoding:
            data = gzip.decompress(data)
        return data, charset


def _decode_html(data, charset):
    """Decode HTML bytes dengan deteksi BOM/charset/fallback."""
    if not charset:
        if data.startswith(b"\xef\xbb\xbf"):
            charset = "utf-8-sig"
        elif data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
            charset = "utf-16"
        else:
            match = re.search(
                rb"charset=[\"']?([\w-]+)", data[:2048], re.IGNORECASE
            )
            charset = match.group(1).decode("ascii", "replace") if match else None
    try:
        return data.decode(charset or "utf-8")
    except (LookupError, UnicodeDecodeError):
        return data.decode("utf-8", errors="replace")


def _normalize_url(raw, base_url):
    """Ubah relative/protocol-relative jadi URL absolut; None bila tak layak."""
    raw = raw.strip().strip('"').strip("'")
    if not raw or raw.lower().startswith(_SKIP_SCHEMES):
        return None
    url = urljoin(base_url, raw)
    if urlparse(url).scheme not in ("http", "https"):
        return None
    return url


def _safe_name(url, fallback="file"):
    """Nama file aman dari basename URL."""
    path = unquote(urlsplit(url).path)
    name = os.path.basename(path)
    if not name or name in (".", "/"):
        name = fallback
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if len(name) > 80:
        root, ext = os.path.splitext(name)
        name = root[:70] + ext
    return name


def _unique_path(directory, name):
    """Nama file unik di directory (suffix numerik saat bentrok)."""
    candidate = os.path.join(directory, name)
    base, ext = os.path.splitext(name)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(directory, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


class _Cloner:
    def __init__(self, base_url, stage_dir):
        self.base_url = base_url
        self.host = urlparse(base_url).netloc
        self.stage_dir = stage_dir
        self.dir_by_kind = {
            "css": os.path.join(stage_dir, "css"),
            "js": os.path.join(stage_dir, "js"),
            "img": os.path.join(stage_dir, "img"),
            "media": os.path.join(stage_dir, "media"),
            "other": os.path.join(stage_dir, "assets"),
        }
        self.url_to_local = {}
        self.raw_to_local = {}
        self.counts = {"css": 0, "js": 0, "img": 0, "media": 0, "other": 0}
        self.saved = 0
        self.failed = 0

    def _local_target(self, url, kind):
        """Tentukan path lokal (relatif stage) untuk sebuah resource URL."""
        if url in self.url_to_local:
            return self.url_to_local[url]
        host = urlparse(url).netloc
        directory = self.dir_by_kind[kind]
        if host and host != self.host:
            directory = os.path.join(
                self.dir_by_kind["other"], re.sub(r"[^A-Za-z0-9.-]", "_", host)
            )
        os.makedirs(directory, exist_ok=True)
        name = _safe_name(url, fallback=kind)
        rel = _unique_path(directory, name)
        self.url_to_local[url] = rel
        return rel

    def fetch_resource(self, url, kind, raw=None):
        if len(self.url_to_local) >= MAX_ASSETS:
            return None
        raw = raw if raw is not None else url
        existing = self.url_to_local.get(url)
        rel = existing or self._local_target(url, kind)
        self.raw_to_local[raw] = rel
        if existing:
            return rel
        try:
            data, _ = _fetch(url)
            with open(rel, "wb") as f:
                f.write(data)
        except Exception:
            self.failed += 1
            self.url_to_local.pop(url, None)
            self.raw_to_local.pop(raw, None)
            return None

        self.saved += 1
        self.counts[kind] = self.counts.get(kind, 0) + 1
        return rel

    def rewrite_refs(self, html):
        """Ganti referensi resource di HTML (bentuk raw aslinya) dengan path lokal."""
        ordered = sorted(self.raw_to_local.items(), key=lambda kv: len(kv[0]), reverse=True)
        for raw, rel in ordered:
            html = html.replace(raw, os.path.relpath(rel, self.stage_dir))
        return html

    def rewrite_css_files(self):
        """Rewrite url(...) dalam semua CSS agar menunjuk aset lokal."""
        for root, _dirs, files in os.walk(self.stage_dir):
            for fn in files:
                if not fn.lower().endswith(".css"):
                    continue
                path = os.path.join(root, fn)
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except OSError:
                    continue
                base = self.css_base_url(path)
                new_content = self._rewrite_css_content(content, base, root)
                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)

    def collect_css_asset_urls(self):
        """Kumpulkan semua URL aset yang dirujuk url(...) di CSS terunduh."""
        urls = []
        for root, _dirs, files in os.walk(self.stage_dir):
            for fn in files:
                if not fn.lower().endswith(".css"):
                    continue
                path = os.path.join(root, fn)
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except OSError:
                    continue
                base = self.css_base_url(path)
                for m in _CSS_URL_RE.finditer(content):
                    src = m.group(1) or m.group(2) or m.group(3)
                    url = _normalize_url(src, base)
                    if url:
                        urls.append(url)
        return urls

    def css_base_url(self, local_path):
        for url, rel in self.url_to_local.items():
            if os.path.abspath(rel) == os.path.abspath(local_path):
                return url
        return self.base_url

    def _rewrite_css_content(self, content, base_url, from_dir):
        def repl(m):
            if m.group(1) is not None:
                quote, src = "'", m.group(1)
            elif m.group(2) is not None:
                quote, src = '"', m.group(2)
            else:
                quote, src = "", m.group(3) or ""
            url = _normalize_url(src, base_url)
            if not url:
                return m.group(0)
            rel = self.fetch_resource(url, "img")
            if not rel:
                return m.group(0)
            rel_path = os.path.relpath(rel, from_dir)
            return f"url({quote}{rel_path}{quote})"

        return _CSS_URL_RE.sub(repl, content)


def _domain_slug(url):
    host = urlparse(url).netloc
    host = re.sub(r"^www\.", "", host)
    return re.sub(r"[^A-Za-z0-9.-]", "_", host) or "web"


def _progress(i, total, label=""):
    """Progress bar satu baris (di-update in-place)."""
    if total <= 0:
        return
    pct = min(int(i * 100 / total), 100)
    filled = pct // 5
    bar = "█" * filled + "░" * (20 - filled)
    suffix = f" {label} " if label else " "
    sys.stdout.write(f"\r  {suffix}[{bar}] {i}/{total} ({pct}%)")
    sys.stdout.flush()


def clone_site(url):
    """Mengklon satu halaman web (HTML/CSS/JS/gambar/font) menjadi .zip.

    Menghasilkan: ~/Downloads/rydzzWeb/<domain>_<timestamp>.zip
    """
    if not url:
        print(t("wc.usage"))
        return False, None

    raw = url.strip().strip('"').strip("'")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        print(t("wc.invalid_url"))
        return False, None

    print(t("wc.cloning", cyan=config.CYAN, reset=config.RESET, url=raw))
    try:
        data, charset = _fetch(raw)
    except Exception as e:
        print(t("wc.fetch_failed", e=e))
        return False, None

    html_text = _decode_html(data, charset)

    # Kumpulkan referensi resource
    collector = _AssetCollector()
    collector.feed(html_text)
    raw_resources = collector.resources

    if not html_text.strip():
        print(t("wc.empty_page"))
        return False, None

    stage = tempfile.mkdtemp(prefix="rydzz_wc_")
    os.makedirs(os.path.join(stage, "css"), exist_ok=True)
    os.makedirs(os.path.join(stage, "js"), exist_ok=True)
    os.makedirs(os.path.join(stage, "img"), exist_ok=True)
    os.makedirs(os.path.join(stage, "media"), exist_ok=True)
    os.makedirs(os.path.join(stage, "assets"), exist_ok=True)

    cloner = _Cloner(raw, stage)

    # Fase 1: unduh aset yang dirujuk HTML, dengan progress
    html_targets = []
    for kind in ("css", "js", "img", "media", "other"):
        for src in raw_resources.get(kind, ()):
            resolved = _normalize_url(src, raw)
            if resolved:
                html_targets.append((resolved, kind, src))
    # Dedupe agar jumlah target akurat
    seen = set()
    html_targets = [
        t for t in html_targets
        if not (t[0] in seen or seen.add(t[0]))
    ]

    total_html = len(html_targets)
    if total_html:
        print(t("wc.fetching_assets"))
        for i, (resolved, kind, src) in enumerate(html_targets, 1):
            cloner.fetch_resource(resolved, kind, raw=src)
            _progress(i, total_html, "HTML")
            if len(cloner.url_to_local) >= MAX_ASSETS:
                break
        print()

    # Tulis index.html dengan referensi yang sudah di-rewrite ke path lokal
    index_html = cloner.rewrite_refs(html_text)
    with open(os.path.join(stage, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # Fase 2: unduh aset yang dirujuk url(...) di CSS, dengan progress
    css_targets = list(dict.fromkeys(cloner.collect_css_asset_urls()))
    if css_targets:
        print(t("wc.fetching_css"))
        for i, resp_url in enumerate(css_targets, 1):
            cloner.fetch_resource(resp_url, "img", raw=resp_url)
            _progress(i, len(css_targets), "CSS")
            if len(cloner.url_to_local) >= MAX_ASSETS:
                break
        print()

    cloner.rewrite_css_files()

    # Buat zip
    os.makedirs(WEB_ROOT, exist_ok=True)
    slug = _domain_slug(raw)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(WEB_ROOT, f"{slug}_{stamp}.zip")
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(stage):
                for fn in files:
                    full = os.path.join(root, fn)
                    arc = os.path.relpath(full, stage)
                    zf.write(full, arc)
    except Exception as e:
        print(t("wc.zip_failed", e=e))
        shutil.rmtree(stage, ignore_errors=True)
        return False, None

    shutil.rmtree(stage, ignore_errors=True)
    size_kb = os.path.getsize(zip_path) / 1024

    print(t("wc.done", green=config.GREEN_NEON, reset=config.RESET))
    c = cloner.counts
    print(f"  HTML / CSS / JS / Media: "
          f"{1} / {c['css']} / {c['js']} / "
          f"{c['img'] + c['media'] + c['other']}")
    print(t("wc.assets_ok", ok=cloner.saved, failed=cloner.failed))
    print(
        t(
            "wc.zip_path",
            cyan=config.CYAN,
            reset=config.RESET,
            path=zip_path,
            size=f"{size_kb:.1f}",
        )
    )
    return True, zip_path