# Rydzz — Custom Interactive Shell

Sebuah shell interaktif kustom yang ditulis dalam Python murni (tanpa framework
eksternal). Dibangun sebagai proyek belajar sekaligus alat harian: navigasi
file, manajemen git, unduh video/lagu, QR code, konversi ASCII, hingga
pipeline perintah — semuanya dari satu terminal berwarna.

> Versi: **2.1** — modular ringan, plus `wclone`, AI pemandu **RydzAgent**, dan alat
> harian `timer`/`stopwatch`/`calc`/`weather`.

---

## Fitur Utama

### 🐚 Inti Shell
- Prompt berwarna kustom, banner startup, riwayat perintah (`history`)
- **Auto-cd**: ketik nama folder, langsung pindah
- **Tab completion** pintar (perintah, alias, path)
- **Pipe** (`cmd1 | cmd2`) dan **chaining** (`cmd1 && cmd2`)
- **Redirect** output (`>` dan `>>`)
- **Sandbox HOME**: perintah berjalan di `~/.rydzz_home`, terpisah dari home
  asli — kecuali `gh`/`git`/`yt-dlp` yang memakai kredensial asli Anda
- File `.rydzzrc` (lihat template) untuk: warna prompt, banner,
  hidden files, auto-cd, alias kustom, file terproteksi, perintah `init`
- `sudo newpass` & `sudo edit` untuk file rahasia terproteksi

### 📦 Manajemen Folder & File
| Perintah | Fungsi |
| --- | --- |
| `ls [path] [-a] [-l]` | Lihat isi folder, warna per jenis file |
| `tree [path] [-L n]` | Struktur pohon |
| `cd / pwd / mkdir / rm / mv / cp` | Navigasi & manipulasi |
| `cat / nano / touch / echo` | Baca & buat file |
| `python <file.py>` | Jalankan script Python |

### 🌿 Git Shortcut
`gs` (status) · `ga` (add -A) · `gc <msg>` (commit) · `gp` (push) ·
`gpl` (pull) · `gl` (log) · `gb` (branch) · `gd` (diff) ·
`gco <branch>` (checkout) · `gst` (stash) · `gclone <url>` (clone)

### 🌐 Unduh Media — `dl`
```
dl <url>                Unduh video ke ~/Downloads/rydzzMedia/<Platform>/
dl <url> -q             Audio saja (mp3)
dl list                 Lihat semua file ter-unduh
dl update               Update yt-dlp
dl <url> --dry          Simulasi tanpa unduh
```
- Ditenagai `yt-dlp`, otomatis dikelompokkan per platform:
  **YouTube, TikTok, Instagram, X/Twitter, Facebook, Reddit, Twitch,
  Bilibili, SoundCloud, Dailymotion, Vimeo, Pinterest, Rumble, Odysee,
  Likee, Snapchat, Telegram, Discord, Spotify, TwitCasting**, lainnya →
  `Lainnya/`
- Progress bar realtime (persen, kecepatan, ETA)
- **URL Spotify** (track/album/playlist) diproses lewat `spotdl`
  (Spotify ber-DRM sehingga dicari di sumber audio lain)
- Struktur folder otomatis menyesuaikan OS:
  `XDG_DOWNLOAD_DIR` → `user-dirs.dirs` → Termux/Android (`/sdcard/Download`)
  → `~/Downloads` (fallback universal)

### 🌼 Tools Kecil
- `qr <teks> [-o file.png|svg]` — QR code di terminal, bisa disimpan
- `ascii enc|dec [-x|-b]` — konversi ASCII desimal/hex/biner
- `wclone <url>` — klon halaman web (HTML/CSS/JS/gambar/font) jadi `.zip`
  di `~/Downloads/rydzzWeb/`

### 🧰 Alat Harian
- `timer <detik|mm:ss>` — countdown (contoh: `timer 90`, `timer 2:30`),
  bel saat habis, Ctrl+C untuk batalkan
- `stopwatch` — jam berjalan realtime, Ctrl+C untuk berhenti
- `calc <ekspresi>` — kalkulator aman: `calc 2+2*3`, `calc sqrt(144)`;
  dukung `+ - * / // % **` dan fungsi `math` (sqrt, sin, cos, tan, log,
  log10, exp, floor, ceil, abs, round, pow, pi, e)
- `weather [kota]` — cuaca dari wttr.in (tanpa API key); default kota dari
  `.rydzzrc` (`weather city=jakarta`), contoh: `weather bandung`

### 🤖 AI Pemandu — RydzAgent
- `ai <pertanyaan>` — tanya apa saja (Gemini free, Bahasa Indonesia)
- `ai tour` — tur interaktif mengenal fitur shell
- `ai error` — jelaskan error perintah terakhir (manual, privasi aman)
- `Command Not Found: xxx` → otomatis disarankan command terdekat (offline)
- Konfigurasi `.rydzzrc`: `ai=`, `ai key=`, `ai model=`, `ai base=`, `ai nama=`
  (key gratis di https://aistudio.google.com/apikey; tanpa key tetap jalan
  sebagai pemandu offline)

### 🔌 Integrasi Sistem
`git`, `curl`, `wget`, `ssh`/`sshd`, `ping`, `gh`, `pip`, `node`, `df`,
`free`, `ps`, `htop`, `neofetch`/`fastfetch`, `whoami`, `passwd`,
`source ~/.bashrc` untuk alias asli, plus perintah sistem lainnya.

---

## Instalasi

```bash
# Prasyarat: Python 3.10+ , lalu (opsional) tool download:
pip3 install -U yt-dlp segno spotdl

git clone https://github.com/RydzzKen/Rydzz.git
cd Rydzz
python3 CLI.py
```

> Library eksternal hanya dibutuhkan untuk fitur `dl`/`qr`; inti shell
> berjalan tanpa satu dependency pun.

## Konfigurasi `.rydzzrc`

Salin `rydzzrc.template` ke `~/.rydzz_home/.rydzzrc`. Direktif yang tersedia:

| Direktif | Contoh | Fungsi |
| --- | --- | --- |
| `prompt color=` | `prompt color=purple` | Warna prompt (green, cyan, ...) |
| `banner=` | `banner=false` | Tampilkan/abaikan banner startup |
| `hidden=` | `hidden=true` | `ls` menampilkan file hidden default |
| `auto_cd=` | `auto_cd=false` | Nonaktifkan auto-cd |
| `alias=` | `alias=cl=clear` | Alias kustom |
| `protected=add:` | `protected=add:rahasia.txt` | Proteksi file dari hapus/edit |
| `init=` | `init=clear` | Perintah otomatis saat startup |
| `weather city=` | `weather city=bandung` | Kota default untuk `weather` |

---

## Struktur Proyek

```
Rydzz/
├── CLI.py                # Entry point (python3 CLI.py)
├── rydzzrc.template      # Template konfigurasi ~/.rydzzrc
└── rydzz/
    ├── config.py         # State global: warna, protected files, loader rydzzrc
    ├── commands.py       # ls -a/-l, tree, git shortcut, capture_ls
    ├── completions.py    # Tab completion (readline)
    ├── pipe.py           # Pipeline & redirect
    ├── shell.py          # Loop utama REPL, dispatch, help
    ├── tools.py          # dl (yt-dlp/spotdl), qr (segno), ascii
    ├── webclone.py       # wclone — klon halaman web → zip
    ├── ai.py             # RydzAgent — AI pemandu (Gemini, opsional)
    └── gadgets.py        # timer, stopwatch, calc, weather
```

## Lisensi

Proyek belajar pribadi — silakan dipakai dan dimodifikasi.