import os

from rydzz import commands


def test_fuzzy_substring(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "commands.py").write_text("x")
    (tmp_path / "README.md").write_text("x")
    os.makedirs(tmp_path / "sub" / "cmd")
    commands.fuzzy_find("cmd")
    out = capsys.readouterr().out
    assert "commands.py" in out
    assert "sub/cmd/" in out
    assert "README.md" not in out


def test_fuzzy_subsequence(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "server_config.py").write_text("x")
    commands.fuzzy_find("srcfg")
    out = capsys.readouterr().out
    assert "server_config.py" in out


def test_fuzzy_skips_hidden_and_node_modules(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".secret.py").write_text("x")
    os.makedirs(tmp_path / "node_modules")
    (tmp_path / "node_modules" / "dep.py").write_text("x")
    commands.fuzzy_find("py")
    out = capsys.readouterr().out
    assert ".secret.py" not in out
    assert "dep.py" not in out


def test_fuzzy_hidden_with_a(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".secret.py").write_text("x")
    commands.fuzzy_find(".secret", "-a")
    out = capsys.readouterr().out
    assert ".secret.py" in out


def test_fuzzy_respects_protected(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".sudo_pass").write_text("rahasia")
    commands.fuzzy_find("sudo", "-a")
    out = capsys.readouterr().out
    assert ".sudo_pass" not in out


def test_fuzzy_limit(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    for i in range(40):
        (tmp_path / f"f{i:02d}.txt").write_text("x")
    commands.fuzzy_find("txt", "--max", "10")
    out = capsys.readouterr().out
    assert out.count(".txt") == 10


def test_fuzzy_no_result(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    commands.fuzzy_find("zzzz")
    out = capsys.readouterr().out
    assert "zzzz" in out


def test_fuzzy_notdir(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    commands.fuzzy_find("x", tmp_path / "nope")
    out = capsys.readouterr().out
    assert "nope" in out


def test_fuzzy_usage_when_no_query(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    commands.fuzzy_find()
    out = capsys.readouterr().out
    assert "Usage" in out or "Pemakaian" in out