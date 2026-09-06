# -*- coding: utf-8 -*-
"""Tes untuk kit harian: trash, backup, hash, freq, clip, todo, serve, pick,
dan task runner (snippets)."""
import os

from rydzz import config, kits, snippets


# ---------- trash ----------
def test_trash_move_list_restore(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(kits, "TRASH_DIR", str(tmp_path / ".trash"))
    victim = tmp_path / "data.txt"
    victim.write_text("isi")
    kits.trash(f"{victim.name}")
    assert not victim.exists()
    assert (tmp_path / ".trash" / "data.txt").exists()
    out, _ = capsys.readouterr()
    assert ".trash" in out
    kits.trash("restore 1")
    assert victim.exists()
    assert not (tmp_path / ".trash" / "data.txt").exists()


def test_trash_empty(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(kits, "TRASH_DIR", str(tmp_path / ".trash"))
    (tmp_path / "x.txt").write_text("x")
    kits.trash("x.txt")
    kits.trash("empty")
    assert not (tmp_path / ".trash").exists()


def test_trash_not_found(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(kits, "TRASH_DIR", str(tmp_path / ".trash"))
    kits.trash("ghost.txt")
    out, _ = capsys.readouterr()
    assert "tidak ditemukan" in out


# ---------- backup ----------
def test_bk_backup_restore(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(kits, "BACKUP_DIR", str(tmp_path / ".backups"))
    f = tmp_path / "rahasia.txt"
    f.write_text("penting")
    kits.backup(f.name)
    assert (tmp_path / ".backups").is_dir()
    assert os.listdir(tmp_path / ".backups")
    f.unlink()
    kits.backup("restore 1")
    assert f.exists()
    assert f.read_text() == "penting"


# ---------- hash ----------
def test_hash_text_sha256(capsys):
    kits.hashit("hello")
    out, _ = capsys.readouterr()
    assert "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824" in out


def test_hash_md5_flag(capsys):
    kits.hashit("-a md5 hello")
    out, _ = capsys.readouterr()
    assert "5d41402abc4b2a76b9719d911017c592" in out


def test_hash_unknown_algo(capsys):
    kits.hashit("-a sha3 hello")
    out, _ = capsys.readouterr()
    assert "tidak dikenal" in out


def test_hash_file(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    f = tmp_path / "halo.txt"
    f.write_text("hello")
    kits.hashit("halo.txt")
    out, _ = capsys.readouterr()
    assert "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824" in out


# ---------- freq ----------
def test_freq_top(monkeypatch, tmp_path, capsys):
    hfile = tmp_path / ".rydzz_history"
    hfile.write_text("gs\ngs\ngc halo\ngs\n")
    monkeypatch.setattr(config, "HISTORY_FILE", str(hfile))
    kits.freq("2")
    out, _ = capsys.readouterr()
    assert "Top 2" in out
    assert "gs" in out


def test_freq_invalid(monkeypatch, tmp_path, capsys):
    kits.freq("xyz")
    out, _ = capsys.readouterr()
    assert "bukan angka" in out


# ---------- clip ----------
def test_clip_set_calls_backend(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(kits.shutil, "which", lambda prog: "/bin/" + prog if prog == "termux-clipboard-set" else None)
    calls = []

    def fake_run(cmd, input="", text=False, **kw):
        calls.append((cmd, input))
        return None

    monkeypatch.setattr(kits.subprocess, "run", fake_run)
    kits.clip("set halo dunia")
    out, _ = capsys.readouterr()
    assert "tersalin" in out
    assert calls and calls[0][1] == "halo dunia"


def test_clip_no_backend(capsys):
    kits.clip("set xy")
    out, _ = capsys.readouterr()
    assert "tidak ada backend" in out or "tersalin" in out


def test_clip_file_missing(capsys):
    kits.clip("file nope.txt")
    out, _ = capsys.readouterr()
    assert "tidak ditemukan" in out


# ---------- todo ----------
def test_todo_add_list_done(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(kits, "TODO_FILE", str(tmp_path / ".rydzz_todo"))
    kits.todo("add belanja")
    kits.todo("add bersih-bersih")
    assert len((tmp_path / ".rydzz_todo").read_text().splitlines()) == 2
    kits.todo("done 1")
    content = (tmp_path / ".rydzz_todo").read_text().splitlines()
    assert content[0].startswith("[x] ")
    assert content[1].startswith("belanja") is False


def test_todo_clear(monkeypatch, tmp_path):
    monkeypatch.setattr(kits, "TODO_FILE", str(tmp_path / ".rydzz_todo"))
    kits.todo("add tugas A")
    kits.todo("clear")
    assert not (tmp_path / ".rydzz_todo").exists()


# ---------- serve ----------
def test_serve_not_dir(capsys):
    kits.serve("tidak-ada-folder")
    out, _ = capsys.readouterr()
    assert "bukan folder" in out


def test_serve_banner(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(config, "run_system_cmd", lambda cmd: None)
    kits.serve("8123")
    out, _ = capsys.readouterr()
    assert "http://127.0.0.1:8123" in out


def test_lan_ip():
    ip = kits._lan_ip()
    assert "." in ip


# ---------- pick ----------
def test_pick_selects(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(kits, "_collect_entries", lambda limit=500: ["a.txt", "b.txt"])
    monkeypatch.setattr("builtins.input", lambda _: "2")
    kits.pick("")
    out, _ = capsys.readouterr()
    assert "b.txt" in out


def test_pick_empty(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(kits, "_collect_entries", lambda limit=500: [])
    kits.pick("")
    out, _ = capsys.readouterr()
    assert "tidak ada file" in out


# ---------- task runner ----------
def test_task_save_run_delete(monkeypatch, tmp_path, capsys):
    sfile = tmp_path / ".rydzz_snippets"
    monkeypatch.setattr(snippets, "SNIPPETS_FILE", str(sfile))
    ran = []
    snippets.task("save halo echo $1", runner=lambda c: ran.append(c))
    assert os.path.exists(sfile)
    snippets.task("halo budi", runner=lambda c: ran.append(c))
    assert ran == ["echo budi"]
    snippets.task("list", runner=None)
    out, _ = capsys.readouterr()
    assert "halo" in out
    snippets.task("del halo", runner=None)
    assert "halo" not in snippets._load()


def test_task_usage_no_args(capsys):
    snippets.task("", runner=None)
    out, _ = capsys.readouterr()
    assert "Guna: task" in out