# -*- coding: utf-8 -*-
"""English language pack for the Rydzz shell."""

STRINGS = {
    # ---------- banner ----------
    "banner.hint": "Type 'help' or '?' for the command list.",

    # ---------- help ----------
    "help.title": "                  RYDZZ SHELL COMMAND LIST",
    "help.body": """• ls [path] [-a] [-l]      - List folder contents (-a hidden, -l detail)
• tree [path] [-L n]       - Show folder structure as a tree
• cd [folder]              - Change folder (plain cd = back to Home)
• pwd                      - Print the current directory path
• mkdir <folder>           - Create a new folder
• rm <file/folder>         - Delete a file or folder
• mv <src> <dst>           - Move or rename a file/folder
• cp <src> <dst>           - Copy a file or folder
• cat / nano <file>        - Read / edit a text file
• touch <file>             - Create/update a file timestamp
• echo <text>              - Print text
• history [-c]               - Command history (persistent across sessions; -c clears)
• python / py <file.py>    - Run a Python script
• pip / node               - Python & Node pipeline
• git / curl / wget        - Download & network tools
• ssh / sshd / ping        - Remote & connectivity
• whoami / passwd          - User info & change password
• df / free / ps / htop    - Memory & system info
• neofetch / fastfetch     - Aesthetic system display
• sudo edit <file>         - Protected access to edit secret files
• sudo newpass             - Permanently change the custom Sudo password
• source ~/.bashrc         - Reload aliases from ~/.bashrc
• alias / aliases          - Show aliases read from ~/.bashrc
• TG                       - Open the Text Generator
• dl <url>                 - Download video/music to download/rydzzMedia
    dl <url1> <url2> ...     -   batch-download several urls at once
    dl <url> -q              -   audio only (mp3)
    dl <url> --redo          -   re-download even if the file exists
    dl redo                  -   list downloads that can be repeated
    dl redo <number|url>     -   re-download an item from the list
    dl list                  -   view downloaded files
    dl list -n 5             -   5 most recent downloads
    dl list -s               -   sort by largest size
    dl update                -   update yt-dlp
• qr <text>                - Show a QR code in the terminal
    qr <text> -o file.png  -   save QR (png/svg)
• ascii enc|dec [-x|-b]     - ASCII conversion (decimal/hex/binary)
    ascii enc "word"          -   word → codes
    ascii dec "104 101 ..."   -   codes → word
• wclone <url> (alias wcode) - Clone a web page -> zip (HTML/CSS/JS)
• ai <question>            - Ask the RydzAgent AI guide
    ai tour                  -   interactive tour of shell features
    ai error                 -   explain the last command's error
• timer <sec|mm:ss>        - Countdown (cancel with Ctrl+C)
• stopwatch                - Stopwatch (stop with Ctrl+C)
• calc <expression>        - Calculator (2+2*3, sqrt(144), ...)
• weather [city]           - City weather (default: jakarta)
• lang                     - Set the shell language (lang list, lang -C)
• clear                    - Clear the screen
• restart                   - Restart the shell without exiting
• exit                     - Exit the shell
• <cmd1> && <cmd2>         - Run 2 commands at once
• cmd1 | cmd2              - Pipe cmd1 output to cmd2
    (can be piped into builtins: help | grep, history | grep, ...)
• trash / bk / hash         - Safe delete, backup, checksum
• todo / clip / freq        - Task list, clipboard, statistics
• serve [port] [folder]     - HTTP server for sharing files
• pick [query]              - Interactive fuzzy file finder
• task                      - Named snippets (task save <name> "<cmd>")

--- GIT SHORTCUTS ---
• gs=status ga=add gl=log gb=branch gd=diff
• gp=push gpl=pull gst=stash gc=<msg> gco=<branch> gclone=<url>

--- ADVANCED FEATURES ---
• Tab completion            - Auto-complete command/file (Tab)
• Auto-cd: type a folder name - Automatically jump into it
• ~/.rydzzrc                - Configure prompt, banner, hidden, init, lang""",

    # ---------- dl ----------
    "dl.usage_help": """Usage: dl <url1> <url2> ... [-q] | dl list [options] | dl update
  dl <url> --redo       - re-download even if the file exists
  dl list -n 5          - 5 most recent downloads
  dl list -s            - sort by largest size
  dl redo               - list downloads to re-download
  dl redo <number|url>  - re-download an item from the list""",
    "dl.usage_simple": "Usage: dl <url1> <url2> ... [-q]",
    "dl.updating": "Updating yt-dlp...",
    "dl.ytdlp_missing": "yt-dlp not found. Install it first: pip3 install -U yt-dlp",
    "dl.processing": "Processing video from {platform}...",
    "dl.failed": "Download failed (check the error above).",
    "dl.saved_to": "Result saved to: {outdir}",
    "dl.spotdl_missing": "spotdl not found. Install it first: pip3 install -U spotdl",
    "dl.spotify_drm": "Spotify is DRM-protected — processed via spotdl (found in an audio source).",
    "dl.dry_run": "[dry-run] spotdl → {url}",
    "dl.move_failed": "Failed to move {f}: {e}",
    "dl.spotify_ok": "Success: {n} songs saved to {outdir}",
    "dl.spotify_none": "No songs were downloaded (check the spotdl error above).",
    "dl.batch_title": "{bold}{cyan}Download Batch ({total} items){reset}",
    "dl.batch_cancel": "{red}  [FAILED]{reset} Cancelled on item {i}.",
    "dl.summary": "{red}[FAILED]{reset} {failed} items. {green}[OK]{reset} {ok} items.",
    "dl.all_success": "{green}[OK]{reset} All {total} items succeeded.",
    "dl.how_redo": "No downloads recorded yet. Use: dl <url> --redo",
    "dl.redo_list_title": "Downloads list (dl redo <number> to re-download):",
    "dl.redo_use_url": "  (or use a URL directly: dl redo <url>)",
    "dl.redo_num_missing": "Number {n} does not exist. Check: dl redo",
    "dl.list_usage": "Usage: dl list [-n <count>] [-s]",
    "dl.list_opt_n": "  -n <count>   only newest items (default: all)",
    "dl.list_opt_s": "  -s           sort by largest size",
    "dl.none_yet": "No downloads yet. Folder: {dir}",
    "dl.folder_empty": "Folder {dir} is empty.",
    "dl.summary_line": "{purple}rydzzMedia{reset} · {n} files · {size}",
    "dl.col_name": "Name",
    "dl.col_size": "Size",
    "dl.col_platform": "Platform",

    # ---------- ascii ----------
    "ascii.usage": "Usage: ascii enc|-x|-b \"text\"  |  ascii dec [-x|-b] \"numbers ...\"",
    "ascii.need_input": "ASCII mode needs input. Base: {base}",
    "ascii.decode_invalid": "Error: '{p}' is not a number in base {base}",
    "ascii.decode_range": "Error: '{p}' is out of range",

    # ---------- qr ----------
    "qr.segno_missing": "segno library not installed. Install it first: pip3 install segno",
    "qr.usage": "Usage: qr <text> [-o file.png|file.svg]",
    "qr.saved": "QR saved to: {path}",

    # ---------- ai ----------
    "ai.usage_help": """Usage: ai <question> | ai tour | ai error
  ai <ask>     - ask RydzAgent about anything
  ai tour      - interactive tour of shell features
  ai error     - explain the last command's error""",
    "ai.disabled": "AI feature is disabled (ai=false in .rydzzrc). Enable it first.",
    "ai.offline.hit": "{cyan}{name}{reset} (offline): the command '{word}' helps: {usage}",
    "ai.offline.tip": "  {dim}Tip: enable full AI by setting 'ai key' in ~/.rydzz_home/.rydzzrc.{reset}",
    "ai.offline.generic": "{cyan}{name}{reset} (offline): I'm offline (add an 'ai key' in .rydzzrc). Meanwhile, try asking about commands like: ls, tree, git, dl, wclone, qr, ascii. Type 'help' for the full list.",
    "ai.offline.error": "{cyan}{name}{reset} (offline): the command '{cmd}' errored:\n    {err}\n  {dim}(Enable 'ai key' for full AI analysis.){reset}",
    "ai.error": "{red}[AI Error]{reset} {msg}",
    "ai.key_hint": "Check 'ai key' in ~/.rydzz_home/.rydzzrc (get one at https://aistudio.google.com).",
    "ai.no_error": "No previous error has been recorded.",
    "ai.error_prompt": "The command I ran: `{cmd}`\nOutput/error that appeared:\n---\n{err}\n---\nWhy did this happen and how can I fix it? Answer briefly with concrete steps.",
    "ai.system.intro": "You are {name}, a friendly guide assistant inside a terminal/interactive shell called 'Rydzz'. You are called by a user named RydzzKen. Reply in casual but informative English, short and concise, with command examples when needed. You know these shell features:",
    "ai.system.closing": "If asked about something else, still help in a friendly way. Do not claim a shell command exists unless you know it from the list above — suggest a reasonable alternative.",
    "ai.tour.title": "=== Rydzz Tour with {name} ===",
    "ai.tour.example": "example: ",
    "ai.tour.prompt": "[Enter] continue, [q] quit: ",
    "ai.tour.stopped": "\nTour stopped.",
    "ai.tour.done": "\nTour finished. Feel free to ask via `ai`",

    # ---------- text generator (TG) ----------
    "tg.title": "         Text Generator",
    "tg.exit": "Type 'exit' in the text to leave!",
    "tg.input_text": "Enter a Word: ",
    "tg.input_count": "Enter a Number: ",
    "tg.press_enter": "\nPress Enter To Continue...",
    "tg.count_error": "The Number Must Be Digits!!",

    # ---------- sudo ----------
    "sudo.old_pass": "Enter Old Sudo Password: ",
    "sudo.new_pass": "Enter New Sudo Password: ",
    "sudo.confirm_pass": "Confirm New Password: ",
    "sudo.changed": "\n[SUCCESS] Sudo Password changed successfully!",
    "sudo.empty_pass": "\n[ERROR] Password cannot be empty!",
    "sudo.confirm_mismatch": "\n[ERROR] Passwords do not match!",
    "sudo.wrong_old": "\n[ERROR] Old password is wrong!",
    "sudo.edit_pass": "Enter Custom Sudo Password: ",
    "sudo.access_granted": "\nAccess Granted!",
    "sudo.access_denied": "\nAccess Denied: Wrong Password!",
    "sudo.usage_edit": "Usage: sudo edit <file_name>",
    "sudo.password_prompt": "Rydzz Password: ",
    "sudo.exec_fake": "Executing with fake-root: {cmd}",

    # ---------- file commands ----------
    "usage.mv": "Usage: mv <src> <dst>",
    "usage.cp": "Usage: cp <src> <dst>",
    "usage.mkdir": "Usage: mkdir <folder_name>",
    "usage.rm": "Usage: rm <file_or_folder_name>",
    "usage.touch": "Usage: touch <file_name>",
    "usage.cat": "Usage: cat <file_name>",
    "usage.nano": "Usage: nano <file_name>",
    "usage.python": "Usage: python <file.py>",
    "usage.node": "Usage: node <file.js>",
    "usage.source": "Usage: source ~/.bashrc or source ~/.rydzzrc",
    "ok.mv_dir": "'{src}' moved successfully into folder '{dst}'.",
    "ok.mv_rename": "'{src}' renamed successfully to '{dst}'.",
    "ok.cp": "'{src}' copied successfully to '{dst}'.",
    "ok.mkdir": "Folder '{arg}' created successfully.",
    "ok.rm_dir": "Folder '{arg}' deleted successfully.",
    "ok.rm_file": "File '{arg}' deleted successfully.",
    "ok.touch": "File '{arg}' created/updated successfully.",
    "err.mv_dest_dir": "Error: Destination folder '{dst}' not found!",
    "err.mv_fail": "Failed to move: {e}",
    "err.cp_fail": "Failed to copy: {e}",
    "err.cd_not_found": "Folder '{arg}' not found!",
    "err.cd_not_dir": "'{arg}' is not a folder!",
    "err.cd_fail": "Failed to change folder: {e}",
    "err.mkdir_exists": "Folder '{arg}' already exists!",
    "err.mkdir_fail": "Failed to create folder: {e}",
    "err.rm_fail": "Failed to delete: {e}",
    "err.touch_fail": "Failed to create file: {e}",
    "err.cat_not_found": "File '{arg}' not found!",
    "err.cat_read": "Failed to read file: {e}",
    "err.src_not_found": "Source file/folder '{src}' not found!",
    "err.not_found_generic": "File/Folder not found!",
    "err.protected_access": "Access Denied: Use 'sudo edit' to access protected files.",
    "err.cmd_not_found": "Command Not Found: {cmd}",
    "err.suggest": " — Did you mean: {list}?",

    # ---------- history ----------
    "history.cleared": "{green}[DONE]{reset} Command history cleared.",
    "history.empty": "No command history yet.",
    "history.title": "Command History ({total}):",
    "history.hint": "  (last command marked cyan — use history -c to clear)",

    # ---------- alias / source ----------
    "source.ok_bashrc": "Aliases updated from ~/.bashrc!",
    "source.ok_rydzzrc": "Configuration updated from ~/.rydzzrc!",
    "alias.title": "Aliases:",
    "alias.empty": "No aliases found.",

    # ---------- redirect ----------
    "redirect.failed": "Redirect failed: {e}",

    # ---------- EOF ----------
    "eof.exit_hint": "\nUse the 'exit' command to leave.",

    # ---------- lang command ----------
    "lang.current": "Active language: {name} ({code})",
    "lang.names.id": "Indonesian",
    "lang.names.en": "English",
    "lang.usage_help": "Usage: lang list | lang -C <code> | lang set <code>",
    "lang.usage_hint": """  lang list         - list available languages
  lang -C <code>    - change language (or no arg = pick manually)
  lang set <code>   - alias of lang -C""",
    "lang.list_title": "Available languages:",
    "lang.not_found": "Language '{code}' is unknown. Check: lang list",
    "lang.choose": "Choose a language number (0 to cancel): ",
    "lang.invalid_choice": "Invalid choice.",
    "lang.changed": "{green}[DONE]{reset} Language changed to {name} ({code}).",
    "lang.cancelled": "Cancelled.",

    # ---------- calc / timer / stopwatch / weather ----------
    "calc.usage": "Usage: calc <expression>  example: calc 2+2*3  |  calc sqrt(144)",
    "calc.unknown_name": "name '{name}' is not recognized/allowed",
    "calc.funcs_only": "only basic math functions are allowed",
    "calc.too_many_args": "too many function arguments",
    "calc.constants_only": "constants must be numbers",
    "calc.op_not_allowed": "operator '{op}' not allowed",
    "calc.unary_not_allowed": "unary operator '{op}' not allowed",
    "calc.expr_unsupported": "unsupported expression: {t}",
    "calc.divzero": "calc: division by zero!",
    "timer.usage": "Usage: timer <sec|mm:ss>  example: timer 90, timer 2:30",
    "timer.invalid": "Invalid duration. Example: timer 90 or timer 2:30",
    "timer.positive": "Duration must be greater than 0.",
    "timer.running": "Timer running — Ctrl+C to cancel.",
    "timer.remaining": "\r  Remaining {time}  ",
    "timer.cancelled": "\nTimer cancelled.",
    "timer.done": "\r  Done!                       ",
    "timer.timeup": "Time's up!",
    "stopwatch.running": "Stopwatch running — Ctrl+C to stop.",
    "stopwatch.elapsed": "\r  Elapsed {time}  ",
    "stopwatch.stopped": "\n  Stopped. Total: {time} ({total:.1f}s)",
    "weather.not_found": "Location '{city}' not found.",
    "weather.fetch_failed": "Failed to get weather (needs internet): {e}",
    "weather.fetch_failed_http": "Failed to get weather (needs internet): HTTP {code}",
    "weather.label": "{cyan}Weather:{reset} {data}",

    # ---------- webclone ----------
    "wc.usage": "Usage: wclone <url>  (e.g. wclone https://example.com)",
    "wc.invalid_url": "Invalid URL. Use the format https://domain.",
    "wc.cloning": "Cloning {cyan}{url}{reset} ...",
    "wc.fetch_failed": "Failed to download page: {e}",
    "wc.empty_page": "Empty page.",
    "wc.fetching_assets": "Downloading page assets...",
    "wc.fetching_css": "Downloading CSS assets...",
    "wc.zip_failed": "Failed to create zip: {e}",
    "wc.done": "\n{green}Clone successful!{reset}",
    "wc.assets_ok": "  Assets saved: {ok}   Failed: {failed}",
    "wc.zip_path": "  Zip: {cyan}{path}{reset} ({size} KB)",

    # ---------- config ----------
    "cfg.bashrc_read_error": "Failed to read ~/.bashrc: {e}",

    # ---------- ls / tree ----------
    "ls.bad_flag": "ls: unrecognized option '-{ch}'",
    "ls.no_access": "ls: cannot access '{target}': No such file or directory",
    "ls.empty": "(Empty folder)",
    "ls.capture_noaccess": "ls: cannot access '{target}'",
    "tree.not_dir": "tree: '{target}' is not a directory.",
    "tree.items_hidden": "{prefix}{n} items hidden...",

    # ---------- git shortcut ----------
    "git.gc_usage": "Usage: gc <commit_message>",
    "git.gco_usage": "Usage: gco <branch_name>",
    "git.gclone_usage": "Usage: gclone <repo_url>",

    # ---------- daily kits ----------
    "kits.trash.usage": "Usage: trash <path...> | trash list | trash restore <n|name> | trash empty",
    "kits.trash.not_found": "trash: '{path}' not found",
    "kits.trash.protected": "trash: '{path}' is protected — cannot delete",
    "kits.trash.moved": "trash: '{src}' → .trash/{dst}",
    "kits.trash.empty": "Trash is empty.",
    "kits.trash.restore_hint": "Restore with: trash restore <number>",
    "kits.trash.restore_usage": "Usage: trash restore <number|name>",
    "kits.trash.invalid_index": "trash: index '{n}' is invalid",
    "kits.trash.not_in_trash": "trash: '{name}' is not in the trash",
    "kits.trash.restored": "trash: '{name}' restored",
    "kits.trash.cleared": "Trash emptied.",
    "kits.bk.usage": "Usage: bk <path...> | bk list | bk restore <number>",
    "kits.bk.not_found": "bk: '{path}' not found",
    "kits.bk.backed": "bk: '{src}' → backup",
    "kits.bk.empty": "No backups yet.",
    "kits.bk.restore_hint": "Restore with: bk restore <number>",
    "kits.bk.restore_usage": "Usage: bk restore <number>",
    "kits.bk.invalid_index": "bk: index '{n}' is invalid",
    "kits.bk.restored": "bk: '{name}' restored to {dest}",
    "kits.hash.usage": "Usage: hash <file|text> [-a md5|sha1|sha256|sha512]",
    "kits.hash.unknown_algo": "hash: unknown algorithm '{algo}'",
    "kits.freq.invalid_n": "freq: '{n}' is not a number",
    "kits.freq.empty": "No history to count yet.",
    "kits.freq.title": "Top {n} most-used commands:",
    "kits.clip.usage": "Usage: clip set <text> | clip get | clip file <path>",
    "kits.clip.no_backend": "clip: no clipboard backend found (xclip/wl-copy/termux-clipboard)",
    "kits.clip.copied": "clip: text copied",
    "kits.clip.empty": "(clipboard is empty)",
    "kits.clip.not_found": "clip: '{path}' not found",
    "kits.todo.usage": "Usage: todo add <text> | todo list | todo done <n> | todo delete <n> | todo clear",
    "kits.todo.add_usage": "Usage: todo add <text>",
    "kits.todo.added": "todo: {n} task(s) saved",
    "kits.todo.empty": "No tasks yet.",
    "kits.todo.cleared": "All tasks cleared.",
    "kits.serve.not_dir": "serve: '{path}' is not a folder",
    "kits.serve.banner": "{green}  Rydzz server ready!{reset}",
    "kits.serve.hint_local": "  Local:   http://127.0.0.1:{port}",
    "kits.serve.hint_net": "  Network: http://{ip}:{port}",
    "kits.serve.background": "serve: running in background (kill via 'pkill -f http.server' if needed).",
    "kits.serve.stop_hint": "  Press Ctrl+C to stop.",
    "kits.pick.empty": "pick: no matching files",
    "kits.pick.prompt": "Choose a number: ",
    "kits.pick.invalid": "pick: invalid choice",

    # ---------- task runner ----------
    "kits.task.usage": "Usage: task | task save <name> \"<cmd $1>\" | task <name> <args...> | task delete <name>",
    "kits.task.save_usage": "Usage: task save <name> \"<command...>\"",
    "kits.task.saved": "task: '{name}' saved",
    "kits.task.deleted": "task: '{name}' deleted",
    "kits.task.not_found": "task: '{name}' not found",
    "kits.task.empty": "No snippets yet.",
    "kits.task.list_title": "Saved snippets:",
}

# `ai tour` steps (title, description, example)
TOUR_STEPS = [
    ("File Navigation", "list, move, create files", "ls -la"),
    ("Folder Tree", "view the structure directly", "tree -L 2"),
    ("Git Shortcut", "git in short commands", "gl (log), gs (status)"),
    ("Media Download", "yt-dlp & Spotify", "dl https://youtu.be/xxxx -q"),
    ("Web Clone", "copy one page into a zip", "wclone example.com"),
    ("QR & ASCII", "handy little tools", "qr 'hi' -o hi.png"),
    ("Tab Completion", "press Tab while typing", "type 'wcl' then Tab"),
    ("Pipeline", "chain & pipe commands", "history | grep dl"),
]

# Feature summary for the AI prompt
AI_OVERVIEW = """RYDZZ SHELL FEATURES:
- Navigation: ls [-a/-l], tree, cd, pwd, mkdir, rm, mv, cp, cat, nano, touch
- Git shortcut: gs, ga <add all>, gc <message>, gp, gpl, gl, gb, gd, gco <branch>, gst, gclone <url>
- Media download: dl <url> [-q audio] | dl list | dl update (yt-dlp, Spotify via spotdl)
- QR: qr <text> [-o file.png|svg]  |  ASCII: ascii enc|dec [-x|-b]
- Web clone: wclone <url> (alias wcode) -> zip html/css/js/images/fonts
- Utilities: clear, history, echo, whoami, sudo edit, sudo newpass, source ~/.bashrc, lang
- Pipeline: cmd1 | cmd2 , chaining && , redirect > or >>"""

# Offline AI topics (keyword -> explanation)
AI_TOPICS = {
    "ls": "list folder contents, add -a for hidden, -l for details",
    "tree": "folder structure as a tree, tree -L 2 for depth",
    "git": "gs=status, ga=add, gc=commit, gp=push, gl=log, gb=branch",
    "gs": "git status",
    "dl": "download video/music: dl <url>, -q for mp3 audio",
    "wclone": "clone one web page into a zip (HTML/CSS/JS/images)",
    "wcode": "alias of wclone",
    "qr": "make a QR: qr <text>, save with -o file.png",
    "ascii": "encode/decode ASCII: ascii enc|dec [-x hex] [-b binary]",
    "history": "view the commands you have typed",
    "clear": "clear the screen",
    "cd": "change folder",
    "mkdir": "create a new folder",
    "rm": "delete file/folder",
    "mv": "move/rename file",
    "cp": "copy file",
    "cat": "read a file's contents",
    "sudo": "sudo edit <file> for protected files",
    "lang": "set the shell language: lang list, lang -C <code>",
    "restart": "restart the shell without exiting (all state comes back fresh)",
    "exit": "exit the shell",
    "trash": "safe delete: trash <file>, trash list, trash restore <n>",
    "bk": "back up a file/folder: bk <path>, bk list, bk restore <n>",
    "hash": "checksums: hash <file|text> [-a md5|sha1|sha256|sha512]",
    "freq": "show the most-used commands from history",
    "clip": "clipboard copy/paste: clip set <text>, clip get, clip file <path>",
    "todo": "task list: todo add <text>, todo list, todo done <n>",
    "serve": "run an HTTP server: serve [port] [folder], for sharing files",
    "pick": "interactively find files with fuzzy match",
    "task": "named command snippets: task save <name> \"<cmd $1>\", task <name>",
}