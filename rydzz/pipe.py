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


def _is_custom_ls(cmd):
    return cmd in ("ls", "dir")


def execute_pipeline(cmd_str, builtin_runner=None):
    """Menjalankan pipeline: cmd1 | cmd2 | ...
    Custom 'ls' diproses secara internal (capture_ls). Segmen lain dicoba ke
    builtin_runner (callback ke builtin shell) dulu; jika None (bukan builtin)
    jatuh ke subprocess shell.
    """
    segments = split_pipes(cmd_str)
    if len(segments) == 1:
        # tidak benar-benar pipe, serahkan ke handler biasa
        return None

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
        print(output, end="" if output.endswith("\n") else "\n")
    return True
