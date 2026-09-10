# -*- coding: utf-8 -*-
"""Tes untuk perintah rfr / resetfolder (hapus isi lalu buat ulang)."""
import io
import os
import sys

from rydzz import shell


def _run(cmd, inputs=None):
    old_in = None
    if inputs is not None:
        old_in = sys.stdin
        sys.stdin = io.StringIO("\n".join(inputs) + "\n")
    buf = io.StringIO()
    old_out = sys.stdout
    sys.stdout = buf
    try:
        shell.handle_command(cmd)
    finally:
        if old_in is not None:
            sys.stdin = old_in
        sys.stdout = old_out
    return buf.getvalue()


def test_rfr_folder_resets_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "kerja"
    target.mkdir()
    (target / "lama.txt").write_text("x")
    out = _run(f"rfr {target}", inputs=["y"])
    assert (target / "lama.txt").exists() is False
    assert target.is_dir()
    assert "berhasil di-reset" in out


def test_resetfolder_works_for_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    f = tmp_path / "data.txt"
    f.write_text("isi lama")
    out = _run(f"resetfolder {f}", inputs=["y"])
    assert f.exists()
    assert f.read_text() == ""
    assert "berhasil di-reset" in out


def test_rfr_canceled_keeps_content(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "proyek"
    target.mkdir()
    (target / "boleh.txt").write_text("jangan dihapus")
    out = _run(f"rfr {target}", inputs=["n"])
    assert (target / "boleh.txt").read_text() == "jangan dihapus"
    assert "dibatalkan" in out


def test_rfr_missing_target(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = _run("rfr tidak-ada")
    assert "tidak ditemukan" in out


def test_rfr_refuses_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "keep.txt").write_text("tetap ada")
    out = _run(f"rfr {tmp_path}", inputs=["y"])
    assert (tmp_path / "keep.txt").read_text() == "tetap ada"
    assert "Tidak bisa reset" in out