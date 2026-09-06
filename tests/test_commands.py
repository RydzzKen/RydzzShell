import os

from rydzz import commands


def test_capture_ls_includes_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    out = commands.capture_ls(".")
    assert "a.txt" in out
    assert "b.txt" in out


def test_capture_ls_hides_hidden_by_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / ".secret").write_text("x")
    out = commands.capture_ls(".")
    assert "a.txt" in out
    assert ".secret" not in out


def test_capture_ls_show_hidden_with_flag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".secret").write_text("x")
    out = commands.capture_ls(".", "-a")
    assert ".secret" in out


def test_capture_ls_excludes_protected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".sudo_pass").write_text("rahasia")
    (tmp_path / "biasa.txt").write_text("b")
    out = commands.capture_ls(".", "-a")
    assert "biasa.txt" in out
    assert ".sudo_pass" not in out


def test_capture_ls_file_target(tmp_path):
    f = tmp_path / "satu.txt"
    f.write_text("x")
    assert commands.capture_ls(str(f)) == "satu.txt"
    assert "satu.txt" in commands.capture_ls("-l", str(f))


def test_capture_ls_long_has_total(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a")
    out = commands.capture_ls("-l", ".")
    assert out.startswith("total" )
    assert "a.txt" in out