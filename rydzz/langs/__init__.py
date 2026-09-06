"""Kumpulan paket bahasa untuk Rydzz shell.

Tiap modul bahasa mengekspor:
- STRINGS     : dict {kunci: teks} (mendukung placeholder {format})
- TOUR_STEPS  : list[(judul, deskripsi, contoh)] untuk `ai tour` (opsional)
- AI_OVERVIEW : blok ringkasan fitur untuk prompt AI (opsional)
- AI_TOPICS   : dict {kata: penjelasan} untuk respon offline AI (opsional)

Untuk menambah bahasa baru: buat file baru di sini (mis. langs/ja.py),
daftarkan di rydzz/i18n.py (LANGUAGES + PACKS).
"""