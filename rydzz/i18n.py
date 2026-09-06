# -*- coding: utf-8 -*-
"""i18n — dukungan multi-bahasa untuk Rydzz shell (zero-dependency).

Bahasa default = 'id' agar perilaku lama & test yang mengandalkan teks
Bahasa Indonesia tetap tidak berubah. Setiap paket bahasa ada di
`rydzz/langs/<kode>.py` dan mengekspor `STRINGS` dict (plus opsional
`TOUR_STEPS`, `AI_OVERVIEW`, `AI_TOPICS`).
"""

from .langs import en as _en
from .langs import id as _id

# Registri bahasa: kode -> nama asli (untuk `lang list`)
LANGUAGES = {
    "id": "Bahasa Indonesia",
    "en": "English",
}

PACKS = {
    "id": _id,
    "en": _en,
}

_current = "en"

# Keyword deteksi error per bahasa (dipakai `ai error` & penangkap last-error).
ERROR_KEYWORDS = {
    "id": (
        "Command Not Found", "Perintah tidak ditemukan", "Gagal", "gagal",
        "tidak ditemukan", "Tidak ditemukan", "[ERROR]", "Error", "error:",
        "bukan folder", "Bukan folder", "Ditolak", "ditolak",
    ),
    "en": (
        "Command Not Found", "Failed", "failed", "not found", "Not found",
        "[ERROR]", "Error", "error:", "not a folder", "Not a folder",
        "Denied", "denied",
    ),
}


def _pack():
    return PACKS.get(_current) or _id


def t(key, **kwargs):
    """Terjemahkan kunci pesan ke bahasa aktif. Fallback ke id, lalu ke key."""
    msg = _pack().STRINGS.get(key)
    if msg is None:
        msg = _id.STRINGS.get(key, key)
    if kwargs:
        try:
            return msg.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return msg
    return msg


def set_language(code):
    """Ganti bahasa aktif. Mengembalikan kode bila valid, else None."""
    code = (code or "").strip().lower()
    if code not in LANGUAGES:
        return None
    global _current
    _current = code
    return code


def get_language():
    return _current


def language_name(code=None):
    code = code or _current
    return LANGUAGES.get(code, code)


def list_languages():
    return [(code, name) for code, name in LANGUAGES.items()]


def is_available(code):
    return (code or "").strip().lower() in LANGUAGES


def is_error_output(text):
    """Cek apakah output mengandung indikator error (sesuai bahasa aktif)."""
    kws = ERROR_KEYWORDS.get(_current) or ERROR_KEYWORDS["id"]
    return any(kw in text for kw in kws)


def tour_steps():
    return _pack().TOUR_STEPS or _id.TOUR_STEPS


def ai_overview():
    return _pack().AI_OVERVIEW or _id.AI_OVERVIEW


def ai_topics():
    return _pack().AI_TOPICS or _id.AI_TOPICS