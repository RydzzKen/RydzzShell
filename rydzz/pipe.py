import os
import subprocess

from . import commands, config


def has_pipe(cmd_str):
    """Cek apakah string command mengandung pipe (|) yang aktif."""
    if "|" not in cmd_str:
        return False
    return True


def _split_quoted(s, delim):
    """Split string dengan menghormati kutipan ' dan \"."""
    parts = []
    current = ""
    in_single = False
    in_double = False
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "'" and not in_double:
            in_single = not in_single
            current += ch
        elif ch == '"' and not in_single:
            in_double = not in_double
            current += ch
        elif ch == delim and not in_single and not in_double:
            parts.append(current)
            current = ""
        else:
            current += ch
        i += 1
    if current.strip():
        parts.append(current)
    return parts


def split_pipes(cmd_str):
    """Memecah command menjadi list segmen berdasarkan pipe."""
    return [seg.strip() for seg in _split_quoted(cmd_str, "|") if seg.strip()]


def _run_segment(shell_command, input_data=None):
    """Menjalankan segmen shell (system passthrough) ambil stdout string."""
    env = None
    first_word = shell_command.split()[0] if shell_command.split() else ""
    if first_word in ("gh", "git"):
        env = {**os.environ, "HOME": config.REAL_HOME}
    try:
        result = subprocess.run(
            shell_command,
            shell=True,
            capture_output=True,
            text=True,
            errors="replace",
            input=input_data,
            env=env,
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


# Nama-nama builtin yang boleh dipipe (didaftarkan shell.py).
# Dipakai untuk memutuskan apakah sebuah pipeline bisa di-stream langsung
# (semua segmen perintah sistem) tanpa lewat capture Python.
PIPE_BUILTIN_NAMES = set()


def register_builtin_names(names):
    """Daflarkan nama builtin yang bisa dipipe (dipanggil dari shell.py)."""
    PIPE_BUILTIN_NAMES.update(names)


def is_builtin_segment(seg):
    """True bila segmen ditangani builtin/custom-ls (bukan perintah sistem)."""
    parts = seg.split(maxsplit=1)
    cmd = parts[0] if parts else ""
    if _is_custom_ls(cmd):
        return True
    return cmd in PIPE_BUILTIN_NAMES


def _run_pipeline_stream(cmd_str):
    """Jalankan pipeline penuh lewat OS shell, output streaming real-time.

    Dipakai saat semua segmen adalah perintah sistem (mis. curl | bash):
    tidak ada kebutuhan menangkap output di Python, jadi biarkan OS shell
    yang menyambungkan antar-proses supaya progress instalasi langsung
    terlihat di layar.
    """
    first_word = cmd_str.split()[0] if cmd_str.split() else ""
    env = None
    if first_word in ("gh", "git"):
        env = {**os.environ, "HOME": config.REAL_HOME}
    try:
        subprocess.run(cmd_str, shell=True, env=env)
    except KeyboardInterrupt:
        print("\n^C")
    finally:
        config.reset_terminal()


def _is_custom_ls(cmd):
    return cmd in ("ls", "dir")


def execute_pipeline(cmd_str, builtin_runner=None, stream_system=False):
    """Menjalankan pipeline: cmd1 | cmd2 | ...
    Custom 'ls' diproses secara internal (capture_ls). Segmen lain dicoba ke
    builtin_runner (callback ke builtin shell) dulu; jika None (bukan builtin)
    jatuh ke subprocess shell.
    `... | tee <file>` di akhir menulis output ke file sekaligus ke layar.

    `stream_system=True`: bila SEMUA segmen adalah perintah sistem (bukan
    builtin, mis. curl | bash), pipeline langsung dilimpahkan ke OS shell
    dengan output streaming real-time — tidak ditangkap ke string Python.
    """
    segments = split_pipes(cmd_str)
    if len(segments) == 1:
        # tidak benar-benar pipe, serahkan ke handler biasa
        return None

    # Fast-path streaming: pipeline murni perintah sistem (curl | bash, dst.)
    if stream_system and all(not is_builtin_segment(s) for s in segments):
        _run_pipeline_stream(cmd_str)
        return True

    tee_file = None
    tee_append = False
    last_parts = segments[-1].split()
    if last_parts and last_parts[0] == "tee":
        tee_args = last_parts[1:]
        if "-a" in tee_args:
            tee_append = True
            tee_args = [a for a in tee_args if a != "-a"]
        if tee_args:
            tee_file = tee_args[0]
        segments = segments[:-1]

    output = None
    for seg in segments:
        parts = seg.split(maxsplit=1)
        cmd = parts[0] if parts else ""
        arg = parts[1] if len(parts) > 1 else ""

        if _is_custom_ls(cmd):
            # ls diproses internal, output jadi string
            args = arg.split() if arg else []
            output = commands.capture_ls(*args)
        elif builtin_runner is not None:
            captured = builtin_runner(seg)
            if captured is not None:
                output = captured
            else:
                output = _run_segment(seg, input_data=output)
        else:
            output = _run_segment(seg, input_data=output)

    if output is not None:
        if tee_file:
            try:
                with open(tee_file, "a" if tee_append else "w") as f:
                    f.write(output)
            except Exception as e:
                print(f"tee: {e}")
        print(output, end="" if output.endswith("\n") else "\n")
    return True
