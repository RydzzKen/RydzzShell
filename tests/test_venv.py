import os
import subprocess

from rydzz import shell


def _cleanup_env(extra=None):
    os.environ.pop("VIRTUAL_ENV", None)
    os.environ.pop("CUSTOM_VAR", None)
    os.environ.pop("_OLD_VIRTUAL_PATH", None)
    if extra:
        for key, value in extra.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_source_generic_syncs_env(monkeypatch, capsys, tmp_path):
    activate = tmp_path / "venv" / "bin" / "activate"
    activate.parent.mkdir(parents=True)
    activate.write_text("# venv\n")

    fake_env = (
        f"PATH=/some/venv/bin:/usr/bin\n"
        f"VIRTUAL_ENV={tmp_path}/venv\n"
        f"CUSTOM_VAR=hello123\n"
    )
    monkeypatch.setattr(
        shell.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(
            args=[], returncode=0, stdout=fake_env, stderr=""
        ),
    )

    baseline = {"PATH": os.environ.get("PATH"), "VIRTUAL_ENV": None, "CUSTOM_VAR": None}
    try:
        shell.handle_command(f"source {activate}")

        assert os.environ.get("VIRTUAL_ENV") == f"{tmp_path}/venv"
        assert os.environ.get("CUSTOM_VAR") == "hello123"
        assert os.environ.get("_OLD_VIRTUAL_PATH") == baseline["PATH"]
        out = capsys.readouterr().out
        assert "Berhasil source" in out
    finally:
        _cleanup_env(baseline)


def test_deactivate_restores_path(monkeypatch, capsys):
    old_path = os.environ.get("PATH", "")
    try:
        os.environ["_OLD_VIRTUAL_PATH"] = old_path
        os.environ["VIRTUAL_ENV"] = "/tmp/fake/venv"
        os.environ["PATH"] = "/tmp/fake/venv/bin:/usr/bin"

        shell.handle_command("deactivate")

        assert "VIRTUAL_ENV" not in os.environ
        assert os.environ.get("PATH") == old_path
        out = capsys.readouterr().out
        assert "dinonaktifkan" in out
    finally:
        _cleanup_env({"PATH": old_path})


def test_deactivate_not_active(monkeypatch, capsys):
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    monkeypatch.delenv("_OLD_VIRTUAL_PATH", raising=False)
    shell.handle_command("deactivate")
    out = capsys.readouterr().out
    assert "tidak ada virtual environment" in out.lower()


def test_source_missing_file(monkeypatch, capsys):
    shell.handle_command("source /no/such/file/activate")
    out = capsys.readouterr().out
    assert "tidak ditemukan" in out.lower()


def test_source_failed_on_error(monkeypatch, capsys, tmp_path):
    activate = tmp_path / "venv" / "bin" / "activate"
    activate.parent.mkdir(parents=True)
    activate.write_text("# venv\n")

    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd=["bash"], timeout=10)

    monkeypatch.setattr(shell.subprocess, "run", boom)
    try:
        shell.handle_command(f"source {activate}")
        out = capsys.readouterr().out
        assert "Gagal source" in out
    finally:
        _cleanup_env()