# -*- coding: utf-8 -*-
"""Paket bahasa Indonesia (referensi utama)."""

STRINGS = {
    # ---------- banner ----------
    "banner.hint": "Ketik 'help' atau '?' untuk daftar perintah.",

    # ---------- help ----------
    "help.title": "                  DAFTAR PERINTAH RYDZZ SHELL",
    "help.body": """• ls [path] [-a] [-l]      - Lihat isi folder (-a hidden, -l detail)
• tree [path] [-L n]       - Tampilkan struktur folder dalam pohon
• cd [folder]              - Pindah folder (cd doang = balik ke Home)
• pwd                      - Menampilkan path lokasi direktori aktif
• mkdir <folder>           - Membuat folder baru
• rm <file/folder>         - Menghapus file atau folder
• mv <asal> <tujuan>       - Pindah atau rename file/folder
• cp <asal> <tujuan>       - Menyalin file atau folder
• cat / nano <file>        - Baca / edit file teks
• touch <file>             - Membuat/update timestamp file
• echo <teks>              - Mencetak teks
• history [-c]               - Riwayat perintah (permanen antar-sesi; -c hapus)
• python / py <file.py>    - Menjalankan script Python
• pip / node               - Pipeline Python & Node
• git / curl / wget        - Download & Network tools
• ssh / sshd / ping        - Remote & Connectivity
• whoami / passwd          - Informasi user & ubah password
• df / free / ps / htop    - Informasi memori & sistem
• neofetch / fastfetch     - Tampilan sistem aesthetic
• sudo edit <file>         - Akses terproteksi untuk edit file rahasia
• sudo newpass             - Mengubah password Sudo khusus secara permanen
• source ~/.bashrc         - Reload alias dari ~/.bashrc
• alias / aliases          - Menampilkan alias yang dibaca dari ~/.bashrc
• TG                       - Membuka Text Generator
• dl <url>                 - Unduh video/lagu ke download/rydzzMedia
    dl <url1> <url2> ...     -   unduh batch beberapa url sekaligus
    dl <url> -q              -   audio saja (mp3)
    dl <url> --redo          -   unduh ulang walau file sudah ada
    dl redo                  -   daftar unduhan yang bisa diulang
    dl redo <nomor|url>      -   unduh ulang dari daftar
    dl list                  -   lihat file ter-unduh
    dl list -n 5             -   5 unduhan terbaru
    dl list -s               -   urutkan dari ukuran terbesar
    dl update                -   update yt-dlp
• qr <teks>                - Tampilkan QR di terminal
    qr <teks> -o file.png  -   simpan QR (png/svg)
• ascii enc|dec [-x|-b]     - Konversi ASCII (desimal/hex/biner)
    ascii enc "kata"          -   kata → kode
    ascii dec "104 101 ..."   -   kode → kata
• wclone <url> (alias wcode) - Klon halaman web -> zip (HTML/CSS/JS)
• ai <tanya>                - Tanya AI Pemandu RydzAgent
    ai tour                  -   tur interaktif fitur shell
    ai error                 -   jelaskan error perintah terakhir
• timer <detik|mm:ss>      - Countdown (Ctrl+C batalkan)
• stopwatch                - Stopwatch (Ctrl+C berhenti)
• calc <ekspresi>          - Kalkulator (2+2*3, sqrt(144), ...)
• weather [kota]           - Cuaca kota (default: jakarta)
• lang                     - Atur bahasa shell (lang list, lang -C)
• clear                    - Membersihkan layar
• exit                     - Keluar dari shell
• <cmd1> && <cmd2>         - Menjalankan 2 perintah sekaligus
• cmd1 | cmd2              - Pipe output cmd1 ke cmd2
    (bisa dipipe ke builtin: help | grep, history | grep, ...)

--- SHORTCUT GIT ---
• gs=status ga=add gl=log gb=branch gd=diff
• gp=push gpl=pull gst=stash gc=<msg> gco=<branch> gclone=<url>

--- FITUR LANJUTAN ---
• Tab completion            - Lengkapi command/file otomatis (Tab)
• Auto-cd: ketik nama folder - Otomatis pindah ke folder itu
• ~/.rydzzrc                - Konfigurasi prompt, banner, hidden, init, lang""",

    # ---------- dl ----------
    "dl.usage_help": """Guna: dl <url1> <url2> ... [-q] | dl list [opsi] | dl update
  dl <url> --redo       - unduh ulang walau file sudah ada
  dl list -n 5          - 5 unduhan terbaru
  dl list -s            - urutkan dari ukuran terbesar
  dl redo               - daftar unduhan untuk diulang
  dl redo <nomor|url>   - unduh ulang item dari daftar""",
    "dl.usage_simple": "Guna: dl <url1> <url2> ... [-q]",
    "dl.updating": "Meng-update yt-dlp...",
    "dl.ytdlp_missing": "yt-dlp tidak ditemukan. Install dulu: pip3 install -U yt-dlp",
    "dl.processing": "Memproses video dari {platform}...",
    "dl.failed": "Download gagal (cek error di atas).",
    "dl.saved_to": "Hasil disimpan di: {outdir}",
    "dl.spotdl_missing": "spotdl tidak ditemukan. Install dulu: pip3 install -U spotdl",
    "dl.spotify_drm": "Spotify ber-DRM — diproses lewat spotdl (cari di sumber audio).",
    "dl.dry_run": "[dry-run] spotdl → {url}",
    "dl.move_failed": "Gagal memindahkan {f}: {e}",
    "dl.spotify_ok": "Berhasil: {n} lagu disimpan di {outdir}",
    "dl.spotify_none": "Tidak ada lagu yang terunduh (cek error spotdl di atas).",
    "dl.batch_title": "{bold}{cyan}Download Batch ({total} item){reset}",
    "dl.batch_cancel": "{red}  [GAGAL]{reset} Dibatalkan pada item {i}.",
    "dl.summary": "{red}[GAGAL]{reset} {failed} item. {green}[SUKSES]{reset} {ok} item.",
    "dl.all_success": "{green}[SUKSES]{reset} Semua {total} item berhasil.",
    "dl.how_redo": "Belum ada catatan unduhan. Gunakan: dl <url> --redo",
    "dl.redo_list_title": "Daftar unduhan (dl redo <nomor> untuk unduh ulang):",
    "dl.redo_use_url": "  (langsung pakai URL: dl redo <url>)",
    "dl.redo_num_missing": "Nomor {n} tidak ada. Cek: dl redo",
    "dl.list_usage": "Guna: dl list [-n <jumlah>] [-s]",
    "dl.list_opt_n": "  -n <jumlah>  hanya item terbaru (default: semua)",
    "dl.list_opt_s": "  -s           urutkan dari ukuran terbesar",
    "dl.none_yet": "Belum ada download. Folder: {dir}",
    "dl.folder_empty": "Folder {dir} kosong.",
    "dl.summary_line": "{purple}rydzzMedia{reset} · {n} file · {size}",
    "dl.col_name": "Nama",
    "dl.col_size": "Ukuran",
    "dl.col_platform": "Platform",

    # ---------- ascii ----------
    "ascii.usage": "Guna: ascii enc|-x|-b \"teks\"  |  ascii dec [-x|-b] \"angka ...\"",
    "ascii.need_input": "ASCII mode butuh input. Basis: {base}",
    "ascii.decode_invalid": "Error: '{p}' bukan angka basis {base}",
    "ascii.decode_range": "Error: '{p}' di luar rentang",

    # ---------- qr ----------
    "qr.segno_missing": "Library segno belum ada. Install dulu: pip3 install segno",
    "qr.usage": "Guna: qr <teks> [-o file.png|file.svg]",
    "qr.saved": "QR disimpan di: {path}",

    # ---------- ai ----------
    "ai.usage_help": """Guna: ai <pertanyaan> | ai tour | ai error
  ai <tanya>   - tanya RydzAgent tentang apa saja
  ai tour      - tur interaktif mengenal fitur shell
  ai error     - jelaskan error perintah terakhir""",
    "ai.disabled": "Fitur AI dimatikan (ai=false di .rydzzrc). Aktifkan dulu.",
    "ai.offline.hit": "{cyan}{name}{reset} (offline): perintah '{word}' membantu: {usage}",
    "ai.offline.tip": "  {dim}Tips: aktifkan AI penuh dengan set 'ai key' di ~/.rydzz_home/.rydzzrc.{reset}",
    "ai.offline.generic": "{cyan}{name}{reset} (offline): aku belum online (tambah 'ai key' di .rydzzrc). Sementara ini, coba tanya tentang perintah seperti: ls, tree, git, dl, wclone, qr, ascii. Ketik 'help' untuk daftar lengkap.",
    "ai.offline.error": "{cyan}{name}{reset} (offline): error perintah '{cmd}':\n    {err}\n  {dim}(Aktifkan 'ai key' untuk analisis AI penuh.){reset}",
    "ai.error": "{red}[AI Error]{reset} {msg}",
    "ai.key_hint": "Cek 'ai key' di ~/.rydzz_home/.rydzzrc (dapat di https://aistudio.google.com).",
    "ai.no_error": "Belum ada error sebelumnya yang tercatat.",
    "ai.error_prompt": "Perintah yang saya jalankan: `{cmd}`\nOutput/error yang muncul:\n---\n{err}\n---\nKenapa ini terjadi dan bagaimana cara memperbaikinya? Jawab ringkas dengan langkah konkret.",
    "ai.system.intro": "Kamu adalah {name}, asisten pemandu yang ramah di dalam terminal/interactive shell bernama 'Rydzz'. Kamu dipanggil oleh pengguna bernama RydzzKen. Gunakan bahasa Indonesia kasual namun informatif, jawab singkat-padat dengan contoh perintah bila perlu. Kamu mengenal fitur shell ini:",
    "ai.system.closing": "Jika ditanya di luar itu, tetap bantu dengan gaya ramah. Jangan mengarang bahwa perintah shell tertentu ada jika tidak kamu kenal dari daftar di atas — tawarkan alternatif yang masuk akal.",
    "ai.tour.title": "=== Tur Rydzz bersama {name} ===",
    "ai.tour.example": "contoh: ",
    "ai.tour.prompt": "[Enter] lanjut, [q] berhenti: ",
    "ai.tour.stopped": "\nTur dihentikan.",
    "ai.tour.done": "\nTur selesai. Tanya-tanya aja lewat `ai`",

    # ---------- text generator (TG) ----------
    "tg.title": "         Text Generator",
    "tg.exit": "Ketik 'exit' pada teks untuk keluar!",
    "tg.input_text": "Masukkan Kata: ",
    "tg.input_count": "Masukkan Jumlah: ",
    "tg.press_enter": "\nTekan Enter Untuk Lanjut...",
    "tg.count_error": "Jumlah Harus Berupa Angka!!",

    # ---------- sudo ----------
    "sudo.old_pass": "Masukkan Sudo Password Lama: ",
    "sudo.new_pass": "Masukkan Sudo Password Baru: ",
    "sudo.confirm_pass": "Konfirmasi Password Baru: ",
    "sudo.changed": "\n[SUCCESS] Sudo Password berhasil diubah!",
    "sudo.empty_pass": "\n[ERROR] Password tidak boleh kosong!",
    "sudo.confirm_mismatch": "\n[ERROR] Konfirmasi password tidak cocok!",
    "sudo.wrong_old": "\n[ERROR] Password lama salah!",
    "sudo.edit_pass": "Masukkan Custom Sudo Password: ",
    "sudo.access_granted": "\nAkses Diterima!",
    "sudo.access_denied": "\nAkses Ditolak: Password Salah!",
    "sudo.usage_edit": "Guna: sudo edit <nama_file>",
    "sudo.password_prompt": "Rydzz Password: ",
    "sudo.exec_fake": "Menjalankan dengan fake-root: {cmd}",

    # ---------- file commands ----------
    "usage.mv": "Guna: mv <asal> <tujuan>",
    "usage.cp": "Guna: cp <asal> <tujuan>",
    "usage.mkdir": "Guna: mkdir <nama_folder>",
    "usage.rm": "Guna: rm <nama_file_atau_folder>",
    "usage.touch": "Guna: touch <nama_file>",
    "usage.cat": "Guna: cat <nama_file>",
    "usage.nano": "Guna: nano <nama_file>",
    "usage.python": "Guna: python <nama_file.py>",
    "usage.node": "Guna: node <nama_file.js>",
    "usage.source": "Guna: source ~/.bashrc atau source ~/.rydzzrc",
    "ok.mv_dir": "'{src}' berhasil dipindahkan ke folder '{dst}'.",
    "ok.mv_rename": "'{src}' berhasil di-rename menjadi '{dst}'.",
    "ok.cp": "'{src}' berhasil disalin ke '{dst}'.",
    "ok.mkdir": "Folder '{arg}' berhasil dibuat.",
    "ok.rm_dir": "Folder '{arg}' berhasil dihapus.",
    "ok.rm_file": "File '{arg}' berhasil dihapus.",
    "ok.touch": "File '{arg}' berhasil dibuat/diperbarui.",
    "err.mv_dest_dir": "Error: Folder tujuan '{dst}' tidak ditemukan!",
    "err.mv_fail": "Gagal memindahkan: {e}",
    "err.cp_fail": "Gagal menyalin: {e}",
    "err.cd_not_found": "Folder '{arg}' tidak ditemukan!",
    "err.cd_not_dir": "'{arg}' bukan sebuah folder!",
    "err.cd_fail": "Gagal pindah folder: {e}",
    "err.mkdir_exists": "Folder '{arg}' sudah ada!",
    "err.mkdir_fail": "Gagal membuat folder: {e}",
    "err.rm_fail": "Gagal menghapus: {e}",
    "err.touch_fail": "Gagal membuat file: {e}",
    "err.cat_not_found": "File '{arg}' tidak ditemukan!",
    "err.cat_read": "Gagal membaca file: {e}",
    "err.src_not_found": "File/Folder asal '{src}' tidak ditemukan!",
    "err.not_found_generic": "File/Folder tidak ditemukan!",
    "err.protected_access": "Akses Ditolak: Gunakan 'sudo edit' untuk mengakses file terproteksi.",
    "err.cmd_not_found": "Command Not Found: {cmd}",
    "err.suggest": " — Maksudmu: {list}?",

    # ---------- history ----------
    "history.cleared": "{green}[SUKSES]{reset} Riwayat perintah dibersihkan.",
    "history.empty": "Belum ada riwayat perintah.",
    "history.title": "Daftar Riwayat Perintah ({total}):",
    "history.hint": "  (perintah terakhir ditandai cyan — untuk hapus: history -c)",

    # ---------- alias / source ----------
    "source.ok_bashrc": "Berhasil meng-update alias dari ~/.bashrc!",
    "source.ok_rydzzrc": "Berhasil meng-update konfigurasi dari ~/.rydzzrc!",
    "alias.title": "Daftar Alias:",
    "alias.empty": "Tidak ada alias ditemukan.",

    # ---------- redirect ----------
    "redirect.failed": "Redirect gagal: {e}",

    # ---------- EOF ----------
    "eof.exit_hint": "\nGunakan perintah 'exit' untuk keluar.",

    # ---------- lang command ----------
    "lang.current": "Bahasa aktif: {name} ({code})",
    "lang.usage_help": "Guna: lang list | lang -C <kode> | lang set <kode>",
    "lang.usage_hint": """  lang list         - daftar bahasa yang tersedia
  lang -C <kode>    - ganti bahasa (atau tanpa arg = pilih manual)
  lang set <kode>   - alias dari lang -C""",
    "lang.list_title": "Bahasa yang tersedia:",
    "lang.not_found": "Bahasa '{code}' tidak dikenal. Cek: lang list",
    "lang.choose": "Pilih nomor bahasa (0 untuk batal): ",
    "lang.invalid_choice": "Pilihan tidak valid.",
    "lang.changed": "{green}[SUKSES]{reset} Bahasa diganti ke {name} ({code}).",
    "lang.cancelled": "Dibatalkan.",

    # ---------- calc / timer / stopwatch / weather ----------
    "calc.usage": "Guna: calc <ekspresi>  contoh: calc 2+2*3  |  calc sqrt(144)",
    "calc.unknown_name": "nama '{name}' tidak dikenali/diizinkan",
    "calc.funcs_only": "hanya fungsi matematika dasar yang diizinkan",
    "calc.too_many_args": "terlalu banyak argumen fungsi",
    "calc.constants_only": "konstanta hanya angka",
    "calc.op_not_allowed": "operator '{op}' tak dizinkan",
    "calc.unary_not_allowed": "operator unary '{op}' tak dizinkan",
    "calc.expr_unsupported": "ekspresi tak didukung: {t}",
    "calc.divzero": "calc: pembagian dengan nol!",
    "timer.usage": "Guna: timer <detik|mm:ss>  contoh: timer 90, timer 2:30",
    "timer.invalid": "Durasi tidak valid. Contoh: timer 90 atau timer 2:30",
    "timer.positive": "Durasi harus lebih dari 0.",
    "timer.running": "Timer berjalan — Ctrl+C untuk batalkan.",
    "timer.remaining": "\r  Tersisa {time}  ",
    "timer.cancelled": "\nTimer dibatalkan.",
    "timer.done": "\r  Selesai!                       ",
    "timer.timeup": "Waktu habis!",
    "stopwatch.running": "Stopwatch jalan — Ctrl+C untuk berhenti.",
    "stopwatch.elapsed": "\r  Elapsed {time}  ",
    "stopwatch.stopped": "\n  Berhenti. Total: {time} ({total:.1f}s)",
    "weather.not_found": "Lokasi '{city}' tidak ditemukan.",
    "weather.fetch_failed": "Gagal mengambil cuaca (butuh internet): {e}",
    "weather.fetch_failed_http": "Gagal mengambil cuaca (butuh internet): HTTP {code}",
    "weather.label": "{cyan}Cuaca:{reset} {data}",

    # ---------- webclone ----------
    "wc.usage": "Guna: wclone <url>  (misal: wclone https://example.com)",
    "wc.invalid_url": "URL tidak valid. Gunakan format https://domain.",
    "wc.cloning": "Mengklone {cyan}{url}{reset} ...",
    "wc.fetch_failed": "Gagal mengunduh halaman: {e}",
    "wc.empty_page": "Halaman kosong.",
    "wc.fetching_assets": "Mengunduh aset halaman...",
    "wc.fetching_css": "Mengunduh aset CSS...",
    "wc.zip_failed": "Gagal membuat zip: {e}",
    "wc.done": "\n{green}Klon berhasil!{reset}",
    "wc.assets_ok": "  Aset berhasil: {ok}   Gagal: {failed}",
    "wc.zip_path": "  Zip: {cyan}{path}{reset} ({size} KB)",

    # ---------- config ----------
    "cfg.bashrc_read_error": "Gagal membaca ~/.bashrc: {e}",

    # ---------- ls / tree ----------
    "ls.bad_flag": "ls: tidak mengenali opsi '-{ch}'",
    "ls.no_access": "ls: tidak dapat mengakses '{target}': No such file or directory",
    "ls.empty": "(Folder kosong)",
    "ls.capture_noaccess": "ls: tidak dapat mengakses '{target}'",
    "tree.not_dir": "tree: '{target}' bukan direktori.",
    "tree.items_hidden": "{prefix}{n} item tersembunyi...",

    # ---------- git shortcut ----------
    "git.gc_usage": "Guna: gc <pesan_commit>",
    "git.gco_usage": "Guna: gco <nama_branch>",
    "git.gclone_usage": "Guna: gclone <url_repo>",
}

# Langkah `ai tour` (judul, deskripsi, contoh)
TOUR_STEPS = [
    ("Navigasi File", "ls, cd, pwd, mkdir, rm, mv, cp", "ls -la"),
    ("Pohon Folder", "lihat struktur langsung", "tree -L 2"),
    ("Git Shortcut", "urusan git jadi singkat", "gl (log), gs (status)"),
    ("Unduh Media", "yt-dlp & Spotify", "dl https://youtu.be/xxxx -q"),
    ("Klone Web", "salin satu halaman jadi zip", "wclone example.com"),
    ("QR & ASCII", "tools kecil serba guna", "qr 'halo' -o halo.png"),
    ("Tab Completion", "tekan Tab saat mengetik", "ketik 'wcl' lalu Tab"),
    ("Pipeline", "rantai & pipa perintah", "history | grep dl"),
]

# Ringkasan fitur untuk prompt AI
AI_OVERVIEW = """FEATUR RYDZZ SHELL:
- Navigasi: ls [-a/-l], tree, cd, pwd, mkdir, rm, mv, cp, cat, nano, touch
- Git shortcut: gs, ga <semua add>, gc <pesan>, gp, gpl, gl, gb, gd, gco <branch>, gst, gclone <url>
- Unduh media: dl <url> [-q audio] | dl list | dl update (yt-dlp, Spotify via spotdl)
- QR: qr <teks> [-o file.png|svg]  |  ASCII: ascii enc|dec [-x|-b]
- Klone web: wclone <url> (alias wcode) -> zip html/css/js/gambar/font
- Utilitas: clear, history, echo, whoami, sudo edit, sudo newpass, source ~/.bashrc, lang
- Pipeline: cmd1 | cmd2 , chaining && , redirect > atau >>"""

# Topik offline AI (kata -> penjelasan)
AI_TOPICS = {
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
    "lang": "atur bahasa shell: lang list, lang -C <kode>",
    "exit": "keluar dari shell",
}