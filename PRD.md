# PRD — Rydzz Custom Interactive Shell

| | |
| --- | --- |
| **Product** | Rydzz — Custom Interactive Shell |
| **PRD Version** | 1.4 |
| **Product Version** | 2.4 |
| **Author** | RydzzKen |
| **Status** | Launched (v2.4) |

---

## 1. Executive Summary

Rydzz is a custom interactive shell written in pure Python. It combines file
utilities, git management, social media downloads, QR codes, and data
conversion into a single colorful, user-friendly terminal interface. Built as
a learning project and a personal daily driver.

## 2. Goals

1. Provide a shell interface that is fun and easy to use (multi-language:
   English and Indonesian, colored prompt, custom banner).
2. Consolidate daily developer tasks in one place: file navigation, git,
   media downloads, QR, ASCII conversion, and daily kits (safe delete,
   backup, checksum, clipboard, task lists, file sharing).
3. Sandbox HOME so shell commands cannot damage the real home directory,
   while still using real credentials for `gh`/`git`/`yt-dlp`.
4. Run the core without any dependency — portable across devices
   (Linux, Termux/Android, macOS, Windows).

## 3. Non-Goals

- Not a replacement for bash/zsh for power users.
- Does not fully handle background processes/jobs (`&`, `nohup`).
- Not intended for multi-user production / high-security environments.
- Historically excluded piping into shell builtins (e.g. `help | grep`);
  now supported since v2.2 (F16).

## 4. Persona & Use Cases

**Persona: learning developer (student/hobbyist).**
- Wants a terminal that is comfortable and easy to use daily.
- Frequently downloads videos/songs from social media for content needs.
- Uses git to push personal projects.
- Runs the shell on a Linux laptop and a phone (Termux).

## 5. Main Features

### P0 — Core (Shipped)
| ID | Feature | Description |
| --- | --- | --- |
| F1 | File navigation | `ls -a/-l`, `tree -L`, `cd`, `pwd`, `mkdir`, `rm`, `mv`, `cp` |
| F2 | File manipulation | `cat`, `nano`, `touch`, `echo` |
| F3 | Git shortcuts | `gs/ga/gc/gp/gpl/gl/gb/gd/gco/gst/gclone` |
| F4 | Command chaining & pipe | `&&`, `\n`, `cmd1 \| cmd2` |
| F5 | Redirection | `>` and `>>` |
| F6 | Tab completion | Commands, aliases, paths |
| F7 | Auto-cd | Type a folder name to jump in |
| F8 | `.rydzzrc` configuration | Colors, banner, hidden, alias, protected, init |
| F9 | HOME sandbox | Isolation in `~/.rydzz_home` |

### P1 — Tools (Shipped)
| ID | Feature | Description |
| --- | --- | --- |
| F10 | `dl` media downloader | yt-dlp + autoclass platform module + per-OS folder |
| F11 | `dl` Spotify | Routes to spotdl (DRM workaround), supports playlists |
| F12 | `qr` | Terminal QR + save PNG/SVG (segno) |
| F13 | `ascii` | Decimal/hex/binary conversion |
| F14 | Git/gh real auth | Real credentials carried only for specific commands |
| F15 | `sudo newpass` / `sudo edit` | Protected secret files |
| F21 | `wclone` web cloner | Clone web page → zip (HTML/CSS/JS/images/fonts), zero-dependency |
| F22 | RydzAgent AI Guide | `ai` chat/tour/error (free Gemini, optional), offline command suggestions |
| F23 | Small daily tools | `timer` countdown, `stopwatch`, `calc` safe calculator (AST whitelist), `weather` (wttr.in, no key) |
| F16 | Pipe into builtins | `help \| grep`, `history \| grep`, `echo \| tr` — pipes enter builtins |
| F17 | Persistent history | Cross-session history to `~/.rydzz_home/.rydzz_history` (limit 1000, `history -c`) |
| F18 | Alias export | Tab completion loads `.bashrc` aliases; auto-refreshes after `source` |
| F19 | `dl` batch/playlist | Download many URLs `url1 url2 ...`, playlists without `--no-playlist`, `--redo`, `dl list` adaptive columns (-n/-s) |
| F20 | Unit tests | pytest for commands/tools/pipe/gadgets/history/completions |
| F24 | Multi-language (`lang`) | English default / Bahasa Indonesia; `lang list`, `lang -C <code>`, `lang -C` interactive picker, persistent via `lang=` in `.rydzzrc`; all user-facing output translated through `rydzz/i18n.py` + `rydzz/langs/` packs |
| F25 | Daily kits (safe ops) | `trash` (safe delete + `list`/`restore`/`empty`, refuses protected files), `bk`/`backup` (timestamped backups + `list`/`restore`), `hash` (`-a md5`/`sha1`/`sha256`/`sha512`), `freq [n]` (top commands from history), `clip set/get/file` (auto backend), `todo add/list/done/undone/del/clear` |
| F26 | `serve` & `pick` | `serve [port] [dir] [-b]` HTTP file sharing (foreground/background, LAN address hint); `pick [query]` interactive fuzzy file picker over the current tree |
| F27 | `task` runner | Named snippets (JSON at `~/.rydzz_home/.rydzz_snippets`), `$1..$n` / `$@` substitution, result re-dispatched through the shell (chaining/pipes/aliases work inside snippets) |
| F28 | Tee pipes & `env=` config | `cmd \| tee <file>` (with `-a` append) captures builtin output too; `env=KEY=VALUE` in `.rydzzrc` sets environment variables for the shell & children |
| F29 | `restart` | Reload the shell instantly without exiting (fresh state) |

### P2 — Next up
| ID | Feature | Description |
| --- | --- | --- |
| (open) | User plugins / script config | Extensible user plugins & script configuration as a future direction |

## 6. Technical Architecture

- **Language:** Python 3.10+; lightweight modular architecture (package
  `rydzz/`).
- **Entry point:** `CLI.py` → `rydzz.shell.main()`.
- **Modules:**
  - `config.py` — global state, colors, `.rydzzrc` loader, command runner
    (`run_system_cmd`, `run_system_cmd_real_home`).
  - `commands.py` — `ls`/`tree`/`capture_ls`, git shortcuts.
  - `completions.py` — tab completion (readline).
  - `pipe.py` — pipeline execution + real-home env for `gh`/`git`.
  - `shell.py` — REPL loop, dispatch, help, alias, TG (text generator),
    `lang` handler.
  - `tools.py` — downloader (`yt-dlp`/`spotdl`), QR (`segno`), ASCII.
  - `webclone.py` — `wclone`, web page cloner → zip (stdlib `urllib`/
    `html.parser`/`zipfile`).
  - `ai.py` — RydzAgent AI Guide: chat/tour/error via Gemini (OpenAI-compat,
    stdlib `urllib`), offline fallback without API key.
  - `gadgets.py` — daily tools: `timer`, `stopwatch`, `calc` (safe AST
    parser, stdlib `ast`), `weather` (wttr.in via stdlib `urllib`, no key).
  - `kits.py` — daily kits (F25/F26): `trash`, `backup`, `hash`, `freq`,
    `clip`, `todo`, `serve`, `pick` (all stdlib).
  - `snippets.py` — `task` runner (F27): named snippets in JSON, `$1..$n`/
    `$@` substitution, recursive re-dispatch into the shell.
  - `i18n.py` — translation engine (`t()`, set/get/list language, error
    sniffer per language).
  - `langs/` — language packs (`id.py`, `en.py`, ...).
- **Optional dependencies:** `yt-dlp` (F10), `segno` (F12), `spotdl` (F11),
  and a Gemini API key (F22, optional — without a key it runs the offline
  fallback). Shell core runs with zero dependencies.
- **HOME flow:** `REAL_HOME` is captured before override; the shell runs in
  `CUSTOM_HOME` (`~/.rydzz_home`); `gh`/`git`/`yt-dlp`/`spotdl` commands run
  with `HOME=REAL_HOME` via `run_system_cmd_real_home`.

## 7. Security & Privacy

- Credentials (`.gitconfig`, `.git-credentials`, gh, ssh) are only exposed to
  commands that actually need them (`gh`/`git`/`ssh`), never to other commands.
- `PROTECTED_FILES` prevents delete/write of sensitive files (`CLI.py`,
  `.sudo_pass`) both from the shell and from `.rydzzrc` review.
- Custom sudo password is stored inside the sandbox, not the real home.

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Spotify changes its web API | `spotdl` error (`KeyError: 'uri'`) | `pip3 install -U spotdl spotapi`; SoundCloud/YouTube fallback |
| yt-dlp hits rate-limit/DRM on a site | Download fails | Regular `dl update`; per-platform pptp |
| New platform missing from `PLATFORM_MAP` | Lands in `Others/` folder | Add mapping; contributions welcome |
| Sandbox vs real home mix-up | Auth leak/loss | Only `gh/git/yt-dlp/spotdl` commands use the real home |
| wttr.in changes format / gets blocked | `weather` fails / odd data | Friendly error messages; default city in `.rydzzrc`; generic User-Agent |

## 9. Success Metrics

- Ease of use: all core features used without reading documentation.
- Task completion: download a video (yt-dlp), download a Spotify song
  (spotdl), make a QR, convert ASCII, quick math (`calc`), cooking timer
  (`timer`), weather check (`weather`), git push, a safe delete via `trash`
  with a working `hash` checksum, and `serve` a folder from a phone — all
  from a single shell.
- Portability: runs on Linux, Termux/Android, macOS, Windows.

## 10. Roadmap

- **v2.0** — modular (package `rydzz/`), gh/git real auth,
  `dl` tools (6+ platforms, Spotify, per-OS folders), `qr`, `ascii`.
- **v2.1** — `wclone` web cloner (F21), RydzAgent AI Guide (F22),
  small daily tools (F23): `timer`, `stopwatch`, `calc`, `weather`.
- **v2.2** — P2 completion: pipe into builtins (F16), persistent history
  (F17), alias export / live refresh (F18), batch & playlist with
  re-download plus adaptive `dl list` in `dl` (F19), pytest unit tests (F20).
- **v2.3** — multi-language (F24): `lang` command, `rydzz/i18n.py` engine,
  language packs under `rydzz/langs/`, English default, `lang=` config key.
- **v2.4** — daily kits (F25): `trash`, `bk`/`backup`, `hash`, `freq`,
  `clip`, `todo`; `serve` & `pick` (F26); `task` snippet runner (F27);
  `| tee` pipes & `env=` config (F28); `restart` (F29); new 2.4 banner.

---

*This PRD tracks the live product; P2 may change based on user feedback.*