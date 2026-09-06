import json
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin

from . import config

DEFAULT_MODEL = "gemini-3.6-flash"
DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"
TIMEOUT = 60

# Ringkasan fitur shell — jadi RydzAgent paham konteks.
OVERVIEW = """FEATUR RYDZZ SHELL:
- Navigasi: ls [-a/-l], tree, cd, pwd, mkdir, rm, mv, cp, cat, nano, touch
- Git shortcut: gs, ga <semua add>, gc <pesan>, gp, gpl, gl, gb, gd, gco <branch>, gst, gclone <url>
- Unduh media: dl <url> [-q audio] | dl list | dl update (yt-dlp, Spotify via spotdl)
- QR: qr <teks> [-o file.png|svg]  |  ASCII: ascii enc|dec [-x|-b]
- Klone web: wclone <url> (alias wcode) -> zip html/css/js/gambar/font
- Utilitas: clear, history, echo, whoami, sudo edit, sudo newpass, source ~/.bashrc
- Pipeline: cmd1 | cmd2 , chaining && , redirect > atau >>"""


def _cfg():
    return {
        "enabled": config.CONFIG.get("ai", True),
        "key": str(config.CONFIG.get("ai_key", "")).strip(),
        "model": str(config.CONFIG.get("ai_model", DEFAULT_MODEL)).strip()
        or DEFAULT_MODEL,
        "base": str(config.CONFIG.get("ai_base", DEFAULT_BASE)).strip()
        or DEFAULT_BASE,
        "name": str(config.CONFIG.get("ai_nama", "RydzAgent")).strip()
        or "RydzAgent",
    }


def _system_prompt(cfg):
    return (
        f"Kamu adalah {cfg['name']}, asisten pemandu yang ramah di dalam "
        f"terminal/interactive shell bernama 'Rydzz'. Kamu dipanggil oleh "
        f"pengguna bernama RydzzKen. Gunakan bahasa Indonesia kasual namun "
        f"informatif, jawab singkat-padat dengan contoh perintah bila perlu. "
        f"Kamu mengenal fitur shell ini:\n\n{OVERVIEW}\n\n"
        f"Jika ditanya di luar itu, tetap bantu dengan gaya ramah. "
        f"Jangan mengarang bahwa perintah shell tertentu ada jika tidak kamu "
        f"kenal dari daftar di atas — tawarkan alternatif yang masuk akal."
    )


def _build_url(cfg):
    base = cfg["base"].rstrip("/")
    return urljoin(base + "/", "chat/completions")


def _post(payload, cfg):
    """POST JSON ke endpoint OpenAI-compatible, kembalikan response terbuka."""
    req = urllib.request.Request(
        _build_url(cfg),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['key']}",
        },
    )
    try:
        return urllib.request.urlopen(req, timeout=TIMEOUT)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {detail[:300]}") from e
    except OSError as e:
        raise RuntimeError(f"Gagal terhubung: {e}") from e


def _clean_md(text):
    """Bersihkan markdown agar terbaca rapi di terminal (tanpa ** ` #)."""
    text = re.sub(r"(?m)^\s*```[^\n]*$", "", text)  # baris penanda code block
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)  # bold **x**
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)  # italic *x*
    text = re.sub(r"__([^_\n]+)__", r"\1", text)  # bold __x__
    text = re.sub(r"_([^_\n]+)_", r"\1", text)  # italic _x_
    text = re.sub(r"`([^`\n]+)`", r"\1", text)  # inline code `x`
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)  # heading #
    text = re.sub(r"(?m)^(\s*)\*+\s+", r"\1- ", text)  # bullet * / ** -> -
    return text


def _stream_answer(cfg, messages):
    payload = {"model": cfg["model"], "messages": messages, "stream": True}
    resp = _post(payload, cfg)
    pending = ""
    for raw in resp:
        line = raw.decode("utf-8", "replace").strip()
        if not line or not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
            delta = obj["choices"][0]["delta"].get("content", "") or ""
        except (json.JSONDecodeError, KeyError, IndexError):
            continue
        if not delta:
            continue
        pending += delta
        # Flush per baris agar tetap terasa streaming & markdown bisa dibersihkan
        while "\n" in pending:
            para, pending = pending.split("\n", 1)
            cleaned = _clean_md(para)
            if cleaned:
                sys.stdout.write(cleaned + "\n")
                sys.stdout.flush()
    if pending:
        cleaned = _clean_md(pending)
        if cleaned:
            sys.stdout.write(cleaned)
            sys.stdout.flush()
    sys.stdout.write("\n")


def _offline_respond(cfg, prompt):
    """Fallback tanpa key/internet: bantu dari daftar fitur lokal."""
    low = prompt.lower()
    known = {k.lower(): v for k, v in _topic_map().items()}
    for word, usage in known.items():
        if word in low:
            print(
                f"{config.CYAN}{cfg['name']}{config.RESET} (offline): "
                f"perintah '{word}' membantu: {usage}"
            )
            print(
                f"  {config.DIM}Tips: aktifkan AI penuh dengan set "
                f"'ai key' di ~/.rydzz_home/.rydzzrc.{config.RESET}"
            )
            return
    print(
        f"{config.CYAN}{cfg['name']}{config.RESET} (offline): "
        f"aku belum online (tambah 'ai key' di .rydzzrc). "
        f"Sementara ini, coba tanya tentang perintah seperti: "
        f"ls, tree, git, dl, wclone, qr, ascii. "
        f"Ketik 'help' untuk daftar lengkap."
    )


def _topic_map():
    return {
        "ls": "lihat isi folder, tambah -a untuk hidden, -l untuk detail",
        "tree": "struktur folder seperti pohon, tree -L 2 untuk kedalaman",
        "git": "gs=status, ga=add, gc=commit, gp=push, gl=log, gb=branch",
        "gs": "git status",
        "dl": "unduh video/lagu: dl <url>, -q untuk audio mp3",
        "wclone": "klone satu halaman web ke zip (HTML/CSS/JS/gambar)",
        "wcode": "alias dari wclone",
        "qr": "buat QR: qr <teks>, simpan dengan -o file.png",
        "ascii": "encode/decode ASCII: ascii enc|dec [-x hex] [-b biner]",
        "history": "lihat riwayat perintah yang pernah kamu ketik",
        "clear": "bersihkan layar",
        "cd": "pindah folder",
        "mkdir": "buat folder baru",
        "rm": "hapus file/folder",
        "mv": "pindah/rename file",
        "cp": "salin file",
        "cat": "baca isi file",
        "sudo": "sudo edit <file> untuk file terproteksi",
        "exit": "keluar dari shell",
    }


def is_online(cfg):
    return cfg["enabled"] and bool(cfg["key"])


def chat(user_prompt):
    """Jawab pertanyaan lewat RydzAgent."""
    cfg = _cfg()
    if not cfg["enabled"]:
        print("Fitur AI dimatikan (ai=false di .rydzzrc). Aktifkan dulu.")
        return
    if not cfg["key"]:
        _offline_respond(cfg, user_prompt)
        return
    messages = [
        {"role": "system", "content": _system_prompt(cfg)},
        {"role": "user", "content": user_prompt},
    ]
    print(f"{config.CYAN}{cfg['name']}{config.RESET}: ", end="")
    try:
        _stream_answer(cfg, messages)
    except RuntimeError as e:
        msg = str(e)
        print(f"\n{config.RED}[AI Error]{config.RESET} {msg}")
        if "401" in msg or "403" in msg or "API key" in msg:
            print("Cek 'ai key' di ~/.rydzz_home/.rydzzrc (dapat di https://aistudio.google.com).")


def explain_last_error():
    """Jelaskan error perintah terakhir (dipanggil manual via `ai error`)."""
    cfg = _cfg()
    cmd = config.LAST_CMD
    err = config.LAST_ERROR
    if not err:
        print("Belum ada error sebelumnya yang tercatat.")
        return
    if not cfg["key"]:
        print(
            f"{config.CYAN}{cfg['name']}{config.RESET} (offline): "
            f"error perintah '{cmd}':\n    {err}\n"
            f"  {config.DIM}(Aktifkan 'ai key' untuk analisis AI penuh.){config.RESET}"
        )
        return
    prompt = (
        f"Perintah yang saya jalankan: `{cmd}`\n"
        f"Output/error yang muncul:\n---\n{err[:2000]}\n---\n"
        f"Kenapa ini terjadi dan bagaimana cara memperbaikinya? "
        f"Jawab ringkas dengan langkah konkret."
    )
    messages = [
        {"role": "system", "content": _system_prompt(cfg)},
        {"role": "user", "content": prompt},
    ]
    print(f"{config.CYAN}{cfg['name']}{config.RESET}: ", end="")
    try:
        _stream_answer(cfg, messages)
    except RuntimeError as e:
        print(f"\n{config.RED}[AI Error]{config.RESET} {e}")


def tour():
    """Tur interaktif memperkenalkan fitur shell satu per satu."""
    cfg = _cfg()
    steps = [
        ("Navigasi File", "ls, cd, pwd, mkdir, rm, mv, cp", "ls -la"),
        ("Pohon Folder", "lihat struktur langsung", "tree -L 2"),
        ("Git Shortcut", "urusan git jadi singkat", "gl (log), gs (status)"),
        ("Unduh Media", "yt-dlp & Spotify", "dl https://youtu.be/xxxx -q"),
        ("Klone Web", "salin satu halaman jadi zip", "wclone example.com"),
        ("QR & ASCII", "tools kecil serba guna", "qr 'halo' -o halo.png"),
        ("Tab Completion", "tekan Tab saat mengetik", "ketik 'wcl' lalu Tab"),
        ("Pipeline", "rantai & pipa perintah", "history | grep dl"),
    ]
    print(f"{config.GREEN_NEON}=== Tur Rydzz bersama {cfg['name']} ==={config.RESET}")
    for i, (judul, desc, contoh) in enumerate(steps, 1):
        print(f"\n{config.CYAN}{i}. {judul}{config.RESET} — {desc}")
        print(f"   {config.DIM}contoh: {contoh}{config.RESET}", end=" ")
        if i < len(steps):
            try:
                jawab = input("[Enter] lanjut, [q] berhenti: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nTur dihentikan.")
                return
            if jawab == "q":
                print("Tur selesai. Tanya-tanya aja lewat `ai`")
                return
    print("\nTur selesai. Tanya-tanya aja lewat `ai`")