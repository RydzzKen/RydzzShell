# PRD — Rydzz Custom Interactive Shell

| | |
| --- | --- |
| **Produk** | Rydzz — Custom Interactive Shell |
| **Versi PRD** | 1.1 |
| **Versi Produk** | 2.1 |
| **Penulis** | RydzzKen |
| **Status** | Diluncurkan (v2.1) |

---

## 1. Ringkasan Eksekutif

Rydzz adalah shell interaktif kustom berbahasa Indonesia yang ditulis dalam
Python murni. Shell ini menggabungkan utilitas file, manajemen git,
pengunduh media sosial, QR code, dan konversi data ke dalam satu antarmuka
terminal berwarna yang ramah digunakan. Dibuat sebagai proyek belajar
sekaligus alat harian personal.

## 2. Tujuan (Goals)

1. Menyediakan antarmuka shell yang fun dan mudah dipakai (berbahasa
   Indonesia, prompt berwarna, banner kustom).
2. Merangkum tugas sehari-hari developer dalam satu pintu: navigasi file,
   git, unduh media, QR, konversi ASCII.
3. Sandbox HOME agar perintah shell tidak merusak home asli, sambil tetap
   memakai kredensial asli untuk `gh`/`git`/`yt-dlp`.
4. Berjalan tanpa dependency untuk inti shell — portable lintas perangkat
   (Linux, Termux/Android, macOS, Windows).

## 3. Non-Tujuan (Non-Goals)

- Bukan pengganti bash/zsh untuk power user.
- Tidak menangani proses background/pekerjaan (`&`, `nohup`) secara penuh.
- Tidak dimaksudkan untuk produksi multi-user / keamanan tingkat tinggi.
- Tidak mendukung pipe ke builtin shell (mis. `help | grep`).

## 4. Persona & Use Case

**Persona: developer belajar (mahasiswa/hobi).**
- Ingin terminal yang mudah dan nyaman dipakai sehari-hari.
- Sering mengunduh video/lagu dari media sosial untuk kebutuhan konten.
- Memakai git untuk mengunggah proyek pribadi.
- Menjalankan shell di laptop Linux dan ponsel (Termux).

## 5. Fitur Utama

### P0 — Inti (Sudah ada)
| ID | Fitur | Keterangan |
| --- | --- | --- |
| F1 | Navigasi file | `ls -a/-l`, `tree -L`, `cd`, `pwd`, `mkdir`, `rm`, `mv`, `cp` |
| F2 | Manipulasi file | `cat`, `nano`, `touch`, `echo` |
| F3 | Git shortcut | `gs/ga/gc/gp/gpl/gl/gb/gd/gco/gst/gclone` |
| F4 | Command chaining & pipe | `&&`, `\n`, `cmd1 \| cmd2` |
| F5 | Redirect | `>` dan `>>` |
| F6 | Tab completion | Perintah, alias, path |
| F7 | Auto-cd | Ketik nama folder langsung pindah |
| F8 | Konfigurasi `.rydzzrc` | Warna, banner, hidden, alias, protected, init |
| F9 | Sandbox HOME | Isolasi di `~/.rydzz_home` |

### P1 — Tools (Sudah ada)
| ID | Fitur | Keterangan |
| --- | --- | --- |
| F10 | `dl` media downloader | yt-dlp + autoclass module platform + folder per OS |
| F11 | `dl` Spotify | Route ke spotdl (DRM workaround), dukung playlist |
| F12 | `qr` | QR di terminal + simpan PNG/SVG (segno) |
| F13 | `ascii` | Konversi desimal/hex/biner |
| F14 | Git/gh real auth | Kredensial asli dibawa hanya untuk perintah tertentu |
| F15 | `sudo newpass` / `sudo edit` | File rahasia terproteksi |
| F21 | `wclone` web cloner | Klon halaman web → zip (HTML/CSS/JS/gambar/font), zero-dependency |
| F22 | AI Pemandu RydzAgent | `ai` chat/tour/error (Gemini free, fakultatif), saran command offline |
| F23 | Alat harian kecil | `timer` countdown, `stopwatch`, `calc` kalkulator aman (AST whitelist), `weather` (wttr.in tanpa key) |

### P2 — Rencana
| ID | Fitur | Keterangan |
| --- | --- | --- |
| F16 | Pipe ke builtin | `help \| grep`, `history \| grep` |
| F17 | History permanen | Simpan riwayat antar-sesi ke file |
| F18 | Alias export | Sinkronisasi alias dari `.bashrc` ke penyelesaian tab |
| F19 | Download batch/playlist UI | Kemajuan per item di `dl list` |
| F20 | Unit test | Pytest untuk commands/tools/pipe |

## 6. Arsitektur Teknis

- **Bahasa:** Python 3.10+; arsitektur modular ringan (package `rydzz/`).
- **Entry point:** `CLI.py` → `rydzz.shell.main()`.
- **Modul:**
  - `config.py` — state global, warna, loader `.rydzzrc`, runner command
    (`run_system_cmd`, `run_system_cmd_real_home`).
  - `commands.py` — `ls`/`tree`/`capture_ls`, git shortcut.
  - `completions.py` — tab completion (readline).
  - `pipe.py` — pipeline execution + env real-home untuk `gh`/`git`.
  - `shell.py` — REPL loop, dispatch, help, alias, TG (text generator).
  - `tools.py` — downloader (`yt-dlp`/`spotdl`), QR (`segno`), ASCII.
  - `webclone.py` — `wclone`, klon halaman web → zip (stdlib `urllib`/
    `html.parser`/`zipfile`).
  - `ai.py` — AI Pemandu RydzAgent: chat/tour/error via Gemini (OpenAI-compat,
    stdlib `urllib`), fallback offline tanpa API key.
  - `gadgets.py` — alat harian: `timer`, `stopwatch`, `calc` (parser AST
    aman, stdlib `ast`), `weather` (wttr.in via stdlib `urllib`, tanpa key).
- **Dependency opsional:** `yt-dlp` (F10), `segno` (F12), `spotdl` (F11),
  dan API key Gemini (F22, opsional — tanpa key memakai fallback offline).
  Inti shell tanpa dependency.
- **Alur HOME:** `REAL_HOME` ditangkap sebelum override; shell berjalan di
  `CUSTOM_HOME` (`~/.rydzz_home`); perintah `gh`/`git`/`yt-dlp`/`spotdl`
  dijalankan dengan `HOME=REAL_HOME` via `run_system_cmd_real_home`.

## 7. Keamanan & Privasi

- Kredensial (`.gitconfig`, `.git-credentials`, gh, ssh) hanya terekspos ke
  command yang memang butuh (`gh`/`git`/`ssh`), tidak ke command lain.
- `PROTECTED_FILES` mencegah hapus/tulis file sensitif (`CLI.py`,
  `.sudo_pass`) baik dari shell maupun ulasan `.rydzzrc`.
- Password sudo kustom disimpan di dalam sandbox, bukan home asli.

## 8. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Spotify mengubah API web | `spotdl` error (`KeyError: 'uri'`) | `pip3 install -U spotdl spotapi`; fallback SoundCloud/YouTube |
| yt-dlp kena rate-limit/DRM situs | Download gagal | `dl update` rutin; platform pptp |
| Platform baru belum ada di `PLATFORM_MAP` | Masuk folder `Lainnya/` | Tambah mapping, harap kontribusi |
| Home sandbox vs real home keliru | Auth bocor/hilang | Hanya command `gh/git/yt-dlp/spotdl` yang pakai real home |
| wttr.in berubah format / keblokir | `weather` gagal / data aneh | Pesan error ramah; dukung kota default `.rydzzrc`; pakai User-Agent umum |

## 9. Metrik Keberhasilan

- Kemudahan: seluruh fitur inti dipakai tanpa baca dokumentasi.
- Kelengkapan tugas: unduh video (yt-dlp), unduh lagu Spotify (spotdl),
  buat QR, konversi ASCII, hitung cepat (`calc`), timer masak (`timer`),
  cek cuaca (`weather`), dan push git dari satu shell.
- Portabilitas: berjalan di Linux, Termux/Android, macOS, Windows.

## 10. Roadmap

- **v2.0** — modular (paket `rydzz/`), gh/git real auth,
  tools `dl` (6+ platform, Spotify, folder per-OS), `qr`, `ascii`.
- **v2.1** — `wclone` web cloner (F21), AI Pemandu RydzAgent (F22),
  alat harian kecil (F23): `timer`, `stopwatch`, `calc`, `weather`.
- **v2.2 (rencana)** — sisa P2: pipe ke builtin (F16), history permanen
  (F17), alias export (F18), UI batch/playlist di `dl` (F19), unit test (F20).

---

*Dokumen PRD ini mengikuti produk yang sedang berjalan; P2 dapat berubah
sesuai masukan pengguna.*