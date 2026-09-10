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
• rfr <file/folder>        - Reset file/folder (hapus isi lalu buat ulang)
• mv <asal> <tujuan>       - Pindah atau rename file/folder
• rn <lama> <baru>          - Rename file
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
• TG                       - Text Generator (spam, random, fancy, ASCII, password, key)
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
• restart                   - Restart shell tanpa keluar
• checkupdate [-y]            - Cek update di GitHub (-y = update tanpa tanya)
• exit                     - Keluar dari shell
• <cmd1> && <cmd2>         - Menjalankan 2 perintah sekaligus
• cmd1 | cmd2              - Pipe output cmd1 ke cmd2
    (bisa dipipe ke builtin: help | grep, history | grep, ...)
• trash / bk / hash         - Hapus aman, backup, checksum
• todo / clip / freq        - Daftar tugas, clipboard, statistik
• serve [port] [folder]     - HTTP server buat kirim file
• pick [query]              - Cari file interaktif (fuzzy)
• task                      - Snippet perintah bernama (task save <nama> "<cmd>")
• keystore <nama> <alias> - Buat Java keystore (.jks)
• deploy vercel [path] [--prod] - Deploy project ke Vercel (default: folder aktif)

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
    "tg.input_number": "Beri nomor tiap baris? (y/n): ",
    "tg.input_separator": "Pemisah (n=baris baru, s=spasi, c=koma, atau custom): ",
    "tg.input_delay": "Jeda antar baris dalam detik (kosongkan = tanpa jeda): ",
    "tg.input_save": "Simpan ke file? (y/n): ",
    "tg.input_filename": "Nama file (default tg_output.txt): ",
    "tg.saved": "Hasil disimpan di: {path}",
    "tg.press_enter": "\nTekan Enter Untuk Lanjut...",
    "tg.count_error": "Jumlah Harus Berupa Angka!!",
    "tg.bad_choice": "Pilihan tidak valid!",
    "tg.input_choice": "Pilih mode: ",
    "tg.input_length": "Panjang: ",
    "tg.password_amount": "Berapa banyak? (default 1): ",
    "tg.key_segments": "Segmen (default 4): ",
    "tg.key_seglen": "Karakter per segmen (default 4): ",
    "tg.menu": """[1] Spam Text (ulang)
[2] Random Text Generator
[3] Fancy Text / Unicode
[4] ASCII Art Text
[5] Password Generator
[6] Key Generator
[0] Keluar""",
    "tg.random_menu": """[1] Nama Acak
[2] Email Acak
[3] Alamat Acak
[4] Nomor Telepon Acak
[0] Kembali""",
    "tg.fancy_menu": """[1] Bold      [2] Italic
[3] Script    [4] Fraktur
[5] Double    [6] Sans
[7] Mono      [8] Circled
[9] Squared   [10] Full-width
[0] Kembali""",
    "tg.password_hint": """[1] Huruf Kecil
[2] Huruf Besar
[3] Angka
[4] Simbol
[5] Kecil + Besar
[6] Kecil + Besar + Angka
[7] Semua (Kecil + Besar + Angka + Simbol)
[0] Kembali""",
    "tg.key_menu": """[1] Key hex (0-9 A-F)
[2] Key alfanumerik besar
[3] Key alfanumerik campuran
[0] Kembali""",

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
    "usage.rn": "Guna: rn <nama_lama> <nama_baru>",
    "usage.cp": "Guna: cp <asal> <tujuan>",
    "usage.mkdir": "Guna: mkdir <nama_folder>",
    "usage.rm": "Guna: rm <nama_file_atau_folder>",
    "usage.rfr": "Guna: rfr <file_atau_folder>  (alias: resetfolder)",
    "usage.touch": "Guna: touch <nama_file>",
    "usage.cat": "Guna: cat <nama_file>",
    "usage.nano": "Guna: nano <nama_file>",
    "usage.python": "Guna: python <nama_file.py>",
    "usage.node": "Guna: node <nama_file.js>",
    "usage.source": "Guna: source ~/.bashrc atau source ~/.rydzzrc",
    "ok.mv_dir": "'{src}' berhasil dipindahkan ke folder '{dst}'.",
    "ok.mv_rename": "'{src}' berhasil di-rename menjadi '{dst}'.",
    "ok.rn": "'{src}' berhasil di-rename menjadi '{dst}'.",
    "ok.cp": "'{src}' berhasil disalin ke '{dst}'.",
    "ok.mkdir": "Folder '{arg}' berhasil dibuat.",
    "ok.rm_dir": "Folder '{arg}' berhasil dihapus.",
    "ok.rm_file": "File '{arg}' berhasil dihapus.",
    "ok.rfr_dir": "Folder '{arg}' berhasil di-reset.",
    "ok.rfr_file": "File '{arg}' berhasil di-reset.",
    "rfr.confirm": "Reset '{arg}'? Semua isi akan dihapus lalu dibuat ulang (y/N): ",
    "rfr.cancelled": "Reset dibatalkan.",
    "err.rfr_protected": "Error: Tidak bisa reset folder kerja/home saat ini.",
    "err.rfr_dir_fail": "Gagal mereset folder: {e}",
    "err.rfr_file_fail": "Gagal mereset file: {e}",
    "ok.touch": "File '{arg}' berhasil dibuat/diperbarui.",
    "err.mv_dest_dir": "Error: Folder tujuan '{dst}' tidak ditemukan!",
    "err.mv_fail": "Gagal memindahkan: {e}",
    "err.rn_dir": "Error: Folder tidak bisa di-rename dengan 'rn'. Gunakan 'mv' saja.",
    "err.rn_exists": "Error: '{dst}' sudah ada!",
    "err.rn_fail": "Gagal meng-rename: {e}",
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

    # ---------- cek update ----------
    "checkupdate.failed": "Gagal mengecek update (butuh internet): {e}",
    "checkupdate.no_remote_version": "Tidak bisa membaca versi terbaru dari repository.",
    "checkupdate.up_to_date": "{green}[SUKSES]{reset} RydzzShell sudah versi terbaru (v{local}). Versi terbaru: v{remote}",
    "checkupdate.available": "{cyan}Versi baru tersedia:{reset} sekarang v{local} -> terbaru v{remote}",
    "checkupdate.confirm": "Update sekarang? (y/N): ",
    "checkupdate.cancelled": "Update dibatalkan.",
    "checkupdate.done": "{green}[SUKSES]{reset} Ter-update ke v{version}. Jalankan 'restart' untuk menerapkan.",
    "checkupdate.error": "Update gagal, cek output git di atas.",

    # ---------- redirect ----------
    "redirect.failed": "Redirect gagal: {e}",

    # ---------- EOF ----------
    "eof.exit_hint": "\nGunakan perintah 'exit' untuk keluar.",

    # ---------- lang command ----------
    "lang.current": "Bahasa aktif: {name} ({code})",
    "lang.names.id": "Bahasa Indonesia",
    "lang.names.en": "Bahasa Inggris",
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

    # ---------- kit harian ----------
    "kits.trash.usage": "Guna: trash <path...> | trash list | trash restore <n|nama> | trash empty",
    "kits.trash.not_found": "trash: '{path}' tidak ditemukan",
    "kits.trash.protected": "trash: '{path}' terproteksi — tidak bisa dihapus",
    "kits.trash.moved": "trash: '{src}' → .trash/{dst}",
    "kits.trash.empty": "Trash kosong.",
    "kits.trash.restore_hint": "Pulihkan: trash restore <nomor>",
    "kits.trash.restore_usage": "Guna: trash restore <nomor|nama>",
    "kits.trash.invalid_index": "trash: nomor '{n}' tidak valid",
    "kits.trash.not_in_trash": "trash: '{name}' tidak ada di trash",
    "kits.trash.restored": "trash: '{name}' dipulihkan",
    "kits.trash.cleared": "Trash dikosongkan.",
    "kits.bk.usage": "Guna: bk <path...> | bk list | bk restore <nomor>",
    "kits.bk.not_found": "bk: '{path}' tidak ditemukan",
    "kits.bk.backed": "bk: '{src}' → backup",
    "kits.bk.empty": "Belum ada backup.",
    "kits.bk.restore_hint": "Pulihkan: bk restore <nomor>",
    "kits.bk.restore_usage": "Guna: bk restore <nomor>",
    "kits.bk.invalid_index": "bk: nomor '{n}' tidak valid",
    "kits.bk.restored": "bk: '{name}' dipulihkan ke {dest}",
    "kits.hash.usage": "Guna: hash <file|teks> [-a md5|sha1|sha256|sha512]",
    "kits.hash.unknown_algo": "hash: algoritma '{algo}' tidak dikenal",
    "kits.freq.invalid_n": "freq: '{n}' bukan angka",
    "kits.freq.empty": "Belum ada riwayat untuk dihitung.",
    "kits.freq.title": "Top {n} perintah terpopuler:",
    "kits.clip.usage": "Guna: clip set <teks> | clip get | clip file <path>",
    "kits.clip.no_backend": "clip: tidak ada backend clipboard (xclip/wl-copy/termux-clipboard)",
    "kits.clip.copied": "clip: teks tersalin",
    "kits.clip.empty": "(clipboard kosong)",
    "kits.clip.not_found": "clip: '{path}' tidak ditemukan",
    "kits.todo.usage": "Guna: todo add <teks> | todo list | todo done <n> | todo del <n> | todo clear",
    "kits.todo.add_usage": "Guna: todo add <teks>",
    "kits.todo.added": "todo: {n} tugas tersimpan",
    "kits.todo.empty": "Belum ada tugas.",
    "kits.todo.cleared": "Semua tugas dihapus.",
    "kits.serve.not_dir": "serve: '{path}' bukan folder",
    "kits.serve.banner": "{green}  Server Rydzz siap!{reset}",
    "kits.serve.hint_local": "  Local:   http://127.0.0.1:{port}",
    "kits.serve.hint_net": "  Network: http://{ip}:{port}",
    "kits.serve.background": "serve: berjalan di background (kill via 'pkill -f http.server' bila perlu).",
    "kits.serve.stop_hint": "  Tekan Ctrl+C untuk berhenti.",
    "kits.pick.empty": "pick: tidak ada file yang cocok",
    "kits.pick.prompt": "Pilih nomor: ",
    "kits.pick.invalid": "pick: pilihan tidak valid",

    # ---------- keystore ----------
    "keystore.usage": "Penggunaan: keystore create <nama> <alias> [path]",
    "keystore.keytool_missing": "keytool tidak ditemukan. Install Java JDK untuk menggunakan fitur ini.",
    "keystore.creating": "Membuat keystore di {path} dengan alias {alias}...",
    "keystore.success": "Keystore berhasil dibuat di {path} (alias: {alias})",
    "keystore.failed": "Gagal membuat keystore.",
    "keystore.exists": "Keystore sudah ada di {path}.",

    # ---------- task runner ----------
    "kits.task.usage": "Guna: task | task save <nama> \"<cmd $1>\" | task <nama> <args...> | task del <nama>",
    "kits.task.save_usage": "Guna: task save <nama> \"<perintah...>\"",
    "kits.task.saved": "task: '{name}' tersimpan",
    "kits.task.deleted": "task: '{name}' dihapus",
    "kits.task.not_found": "task: '{name}' tidak ditemukan",
    "kits.task.empty": "Belum ada snippet.",
    "kits.task.list_title": "Snippet tersimpan:",

    # ---------- deploy ----------
    "deploy.usage": "Penggunaan: deploy vercel [path] [--prod] [--help]\n    deploy vercel                    -> deploy folder aktif (preview)\n    deploy vercel /path/ke/project   -> deploy folder spesifik\n    deploy vercel --prod             -> deploy ke production\n    deploy dp <path> --prod          -> alias singkat",
    "deploy.platform_unknown": "deploy: platform '{plat}' tidak dikenal (saat ini hanya 'vercel').",
    "deploy.vercel_missing": "deploy: CLI 'vercel' tidak ditemukan.",
    "deploy.install_hint": "  Install dulu: npm install -g vercel",
    "deploy.not_dir": "deploy: '{path}' bukan folder",
    "deploy.starting": "  Deploying {path} ➜ Vercel ({mode})...",
    "deploy.mode_prod": "production",
    "deploy.mode_preview": "preview",
    "deploy.done_title": "  📦 Deployment selesai!",
    "deploy.no_url": "  URL tidak terbaca — cek dashboard: https://vercel.com/dashboard",
    "deploy.exit_code": "proses vercel keluar dengan kode {code}",
    "deploy.failed": "  ✖ Gagal: {e}",
    "deploy.home_warn_custom": "deploy: '{home}' adalah home sandbox RydzzShell — kemungkinan besar bukan folder project yang mau di-deploy.\n    cd dulu ke folder project, atau beri path: deploy vercel /path/ke/project",
    "deploy.home_warn_real": "deploy: perhatian — kamu men-deploy folder home asli: {home}",
    "deploy.not_logged_in": "deploy: Vercel CLI belum login.",
    "deploy.login_hint": "  Login dulu: vercel login\n  (atau deploy sementara tanpa login: vercel deploy --temporary)",
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
- Navigasi: ls [-a/-l], tree, cd, pwd, mkdir, rm, rfr, mv, rn, cp, cat, nano, touch
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
    "rfr": "reset file/folder: rfr <path> (alias resetfolder)",
    "resetfolder": "reset file/folder: rfr <path> (alias singkat rfr)",
    "mv": "pindah/rename file",
    "rn": "rename file",
    "cp": "salin file",
    "cat": "baca isi file",
    "sudo": "sudo edit <file> untuk file terproteksi",
    "lang": "atur bahasa shell: lang list, lang -C <kode>",
    "restart": "restart shell tanpa perlu keluar (semua state segar kembali)",
    "checkupdate": "cek versi terbaru di GitHub lalu update bila diminta: checkupdate",
    "exit": "keluar dari shell",
    "trash": "hapus aman: trash <file>, trash list, trash restore <n>",
    "bk": "backup file/folder: bk <path>, bk list, bk restore <n>",
    "hash": "cek checksum: hash <file|teks> [-a md5|sha1|sha256|sha512]",
    "freq": "lihat perintah paling sering dipakai dari riwayat",
    "clip": "copy/paste clipboard: clip set <teks>, clip get, clip file <path>",
    "todo": "daftar tugas: todo add <teks>, todo list, todo done <n>",
    "serve": "jalankan HTTP server: serve [port] [folder], buat kirim file",
    "pick": "cari file interaktif dengan fuzzy match",
    "task": "snippet perintah bernama: task save <nama> \"<cmd $1>\", task <nama>",
    "deploy": "deploy project ke Vercel: deploy vercel [path] [--prod], defaultnya folder aktif",
}