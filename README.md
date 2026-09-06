# Rydzz — Custom Interactive Shell

A custom interactive shell written in pure Python (no external framework).
Built as a learning project and a daily driver: file navigation, git
management, media downloads, QR codes, ASCII conversion, and command
pipelining — all from one colorful terminal.

> Version: **2.3** — multi-language (English/Indonesian), persistent history,
> pipes into builtins, batch/re-download in `dl`, adaptive `dl list` columns,
> and unit tests (pytest).

![Version](https://img.shields.io/badge/Version-v2.3-2ea44f)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Dependency](https://img.shields.io/badge/Core-Zero%20dependency-6f42c1)
![Platform](https://img.shields.io/badge/Platform-Linux%20%E2%80%A2%20Termux%20%E2%80%A2%20macOS%20%E2%80%A2%20Windows-brightgreen)
![Tests](https://img.shields.io/badge/Tests-pytest-green)

---

## Main Features

### 🐚 Shell Core
- Custom colored prompt, startup banner, **persistent history** (`history`,
  cross-session, stored at `~/.rydzz_home/.rydzz_history`)
- **Auto-cd**: type a folder name to jump right in
- Smart **tab completion** (commands, aliases, paths) — `.bashrc` aliases are
  refreshed automatically after `source ~/.bashrc`
- **Pipes** (`cmd1 | cmd2`) and **chaining** (`cmd1 && cmd2`) — pipes can now
  **enter builtins** (`help | grep`, `history | grep`, `echo | tr`, etc.)
- Output **redirection** (`>` and `>>`)
- **Sandbox HOME**: commands run in `~/.rydzz_home`, separate from your real
  home — except `gh`/`git`/`yt-dlp`, which use your real credentials
- `.rydzzrc` file (see template) for: prompt color, banner, hidden files,
  auto-cd, custom aliases, protected files, `init` commands
- `sudo newpass` & `sudo edit` for protected secret files

### 📦 File & Folder Management
| Command | Purpose |
| --- | --- |
| `ls [path] [-a] [-l]` | List folder contents, color per file type |
| `tree [path] [-L n]` | Tree structure |
| `cd / pwd / mkdir / rm / mv / cp` | Navigation & manipulation |
| `cat / nano / touch / echo` | Read & create files |
| `python <file.py>` | Run Python scripts |

### 🌿 Git Shortcuts
`gs` (status) · `ga` (add -A) · `gc <msg>` (commit) · `gp` (push) ·
`gpl` (pull) · `gl` (log) · `gb` (branch) · `gd` (diff) ·
`gco <branch>` (checkout) · `gst` (stash) · `gclone <url>` (clone)

### 🌐 Media Downloader — `dl`
```
dl <url>                Download video to ~/Downloads/rydzzMedia/<Platform>/
dl <url1> <url2> ...    Batch download multiple URLs ([i/N] header)
dl <url> -q             Audio only (mp3)
dl <url> --redo         Redownload even if the file already exists
dl redo                 List downloads that can be redone (no need to remember URLs)
dl redo <num|url>       Redownload item N from the list / directly by URL
dl <url> --dry          Simulate without downloading
dl list                 View downloaded files (adaptive columns)
dl list -n 5            Last 5 downloads
dl list -s              Sort by size (largest first)
dl update               Update yt-dlp
```
- Powered by `yt-dlp`, auto-grouped per platform (brand logos from
  Simple Icons):

| Platform | Domain | Content |
| --- | --- | --- |
| <img src="https://cdn.simpleicons.org/youtube/FF0000" width="16" /> **YouTube** | `youtube.com`, `youtu.be`, `music.youtube.com` | Video / Playlist (MP3 via `-q`) |
| <img src="https://cdn.simpleicons.org/instagram/E4405F" width="16" /> **Instagram** | `instagram.com` | Reels / Stories / Photos |
| <img src="https://cdn.simpleicons.org/tiktok/000000" width="16" /> **TikTok** | `tiktok.com`, `vt.tiktok.com` | Video |
| <img src="https://cdn.simpleicons.org/x/000000" width="16" /> **X (Twitter)** | `x.com`, `twitter.com` | Video / GIF |
| <img src="https://cdn.simpleicons.org/facebook/1877F2" width="16" /> **Facebook** | `facebook.com`, `fb.watch` | Reels / Video |
| <img src="https://cdn.simpleicons.org/spotify/1DB954" width="16" /> **Spotify** | `open.spotify.com`, `spotify.com` | Track / Album / Playlist (MP3 via spotdl) |
| <img src="https://cdn.simpleicons.org/reddit/FF4500" width="16" /> **Reddit** | `reddit.com`, `redd.it` | Video |
| <img src="https://cdn.simpleicons.org/twitch/9146FF" width="16" /> **Twitch** | `twitch.tv` | Clip / VOD |
| <img src="https://cdn.simpleicons.org/bilibili/00A1D6" width="16" /> **Bilibili** | `bilibili.com`, `b23.tv` | Video / Audio |
| <img src="https://cdn.simpleicons.org/soundcloud/FF3300" width="16" /> **SoundCloud** | `soundcloud.com` | Audio / MP3 |
| <img src="https://cdn.simpleicons.org/dailymotion/0066DC" width="16" /> **Dailymotion** | `dailymotion.com` | Video |
| <img src="https://cdn.simpleicons.org/vimeo/1AB7EA" width="16" /> **Vimeo** | `vimeo.com` | Video |
| <img src="https://cdn.simpleicons.org/pinterest/E60023" width="16" /> **Pinterest** | `*pinterest*`, `pinterest.com` | Video / Images |
| <img src="https://cdn.simpleicons.org/rumble/85C742" width="16" /> **Rumble** | `rumble.com` | Video |
| <img src="https://cdn.simpleicons.org/odysee/EF1970" width="16" /> **Odysee** | `odysee.com` | Video |
| **Likee** | `likee.com` | Video |
| <img src="https://cdn.simpleicons.org/snapchat/FFFC00" width="16" /> **Snapchat** | `snapchat.com` | Video |
| <img src="https://cdn.simpleicons.org/telegram/26A5E4" width="16" /> **Telegram** | `t.me`, `telegram.app` | Video |
| <img src="https://cdn.simpleicons.org/discord/5865F2" width="16" /> **Discord** | `discord` (incl. `cdn.discordapp.com`) | Clip |
| **TwitCasting** | `twitcasting.tv` | Live / VOD |
| **Others** | Any other URL | `Others/` folder |

  > **Likee** & **TwitCasting** show no logo — their icons aren't available
  > in Simple Icons yet. Logo source: `cdn.simpleicons.org`.
- Realtime progress bar (percent, speed, ETA)
- **Playlist/batch**: playlists are downloaded too (no `--no-playlist`) and you
  can download multiple URLs in a single command
- **Spotify URLs** (track/album/playlist) go through `spotdl`
  (Spotify is DRM-protected, so it searches other audio sources)
- Auto OS-aware folder structure:
  `XDG_DOWNLOAD_DIR` → `user-dirs.dirs` → Termux/Android (`/sdcard/Download`)
  → `~/Downloads` (universal fallback)

### 🌼 Small Tools
- `qr <text> [-o file.png|svg]` — QR code in terminal, saveable to file
- `ascii enc|dec [-x|-b]` — ASCII decimal/hex/binary conversion
- `wclone <url>` — clone a web page (HTML/CSS/JS/images/fonts) to a `.zip`
  in `~/Downloads/rydzzWeb/`

### 🌍 Multi-language
- `lang` — show active language + usage
- `lang list` — list available languages (`*` marks the active one)
- `lang -C <code>` / `lang set <code>` — switch language immediately
  (e.g. `lang -C id`)
- `lang -C` (no argument) — interactive language picker
- Available languages: `en` (English, default), `id` (Bahasa Indonesia)
- Can be set permanently via `.rydzzrc`: `lang=en`
- All output (help, banner, command feedback, AI, dl/qr/ascii, etc.) follows
  the selected language; add a new language pack in `rydzz/langs/`

### 🧰 Daily Tools
- `timer <seconds|mm:ss>` — countdown (e.g. `timer 90`, `timer 2:30`),
  rings when finished, Ctrl+C to cancel
- `stopwatch` — realtime elapsed time, Ctrl+C to stop
- `calc <expression>` — safe calculator: `calc 2+2*3`, `calc sqrt(144)`;
  supports `+ - * / // % **` and `math` functions (sqrt, sin, cos, tan, log,
  log10, exp, floor, ceil, abs, round, pow, pi, e)
- `weather [city]` — weather from wttr.in (no API key); default city from
  `.rydzzrc` (`weather city=jakarta`), e.g. `weather bandung`

### 🤖 AI Guide — RydzAgent
- `ai <question>` — ask anything (free Gemini, follows the shell language)
- `ai tour` — interactive tour of shell features
- `ai error` — explain the last command's error (manual, privacy-safe)
- `Command Not Found: xxx` → nearest command automatically suggested (offline)
- `.rydzzrc` config: `ai=`, `ai key=`, `ai model=`, `ai base=`, `ai nama=`
  (free key at https://aistudio.google.com/apikey; without a key it still
  works as an offline guide)

### 🔌 System Integration
`git`, `curl`, `wget`, `ssh`/`sshd`, `ping`, `gh`, `pip`, `node`, `df`,
`free`, `ps`, `htop`, `neofetch`/`fastfetch`, `whoami`, `passwd`,
`source ~/.bashrc` for real aliases, plus other system commands.

---

## Installation

```bash
# Prerequisites: Python 3.10+; optional download tools:
pip3 install -U yt-dlp segno spotdl

git clone https://github.com/RydzzKen/Rydzz.git
cd Rydzz
python3 CLI.py
```

> External libraries are only needed for the `dl`/`qr` features; the shell
> core runs with zero dependencies.

## `.rydzzrc` Configuration

Copy `rydzzrc.template` to `~/.rydzz_home/.rydzzrc`. Available directives:

| Directive | Example | Purpose |
| --- | --- | --- |
| `prompt color=` | `prompt color=purple` | Prompt color (green, cyan, ...) |
| `banner=` | `banner=false` | Show/ignore the startup banner |
| `history=` | `history=false` | Disable persistent cross-session history |
| `hidden=` | `hidden=true` | `ls` shows hidden files by default |
| `auto_cd=` | `auto_cd=false` | Disable auto-cd |
| `alias=` | `alias=cl=clear` | Custom aliases |
| `protected=add:` | `protected=add:secret.txt` | Protect files from delete/edit |
| `init=` | `init=clear` | Command(s) to run automatically at startup |
| `weather city=` | `weather city=bandung` | Default city for `weather` |
| `lang=` | `lang=id` | Shell UI language (`en` default, `id`, `en`) |

---

## Project Structure

```
Rydzz/
├── CLI.py                # Entry point (python3 CLI.py)
├── pytest.ini            # Test configuration (testpaths)
├── tests/                # Unit tests (pytest)
├── rydzzrc.template      # ~/.rydzzrc config template
└── rydzz/
    ├── config.py         # Global state: colors, protected files, rydzzrc loader, history
    ├── commands.py       # ls -a/-l, tree, git shortcuts, capture_ls
    ├── completions.py    # Tab completion (readline)
    ├── pipe.py           # Pipeline & redirection
    ├── shell.py          # Main REPL loop, dispatch, help
    ├── tools.py          # dl (yt-dlp/spotdl), qr (segno), ascii
    ├── webclone.py       # wclone — web page cloner → zip
    ├── ai.py             # RydzAgent — AI guide (Gemini, optional)
    ├── gadgets.py        # timer, stopwatch, calc, weather
    ├── i18n.py           # Multi-language support (translations, lang)
    └── langs/            # Language packs (id.py, en.py, ...)
```

## Testing

Unit tests are written with **pytest** (dev-only dependency — daily shell use
stays zero-dependency). To run:

```bash
pip3 install pytest
python3 -m pytest
```

## License

Personal learning project — feel free to use and modify.