from rydzz import commands


def _mock_ss(monkeypatch, out):
    monkeypatch.setattr(
        commands.shutil, "which", lambda name: "/usr/bin/ss" if name == "ss" else None
    )
    monkeypatch.setattr(commands, "_run_quiet", lambda cmd: out)


def test_port_info_finds_process(monkeypatch, capsys):
    fake = (
        "LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:* "
        'users:(("python3",pid=12345,fd=3))'
    )
    _mock_ss(monkeypatch, fake)
    commands.port_info(8080)
    out = capsys.readouterr().out
    assert "12345" in out
    assert "python3" in out


def test_port_info_free(monkeypatch, capsys):
    _mock_ss(monkeypatch, "")
    commands.port_info(9999)
    out = capsys.readouterr().out
    assert "9999" in out


def test_port_kill_confirms(monkeypatch, capsys):
    monkeypatch.setattr(
        commands, "_lookup_port", lambda port: [(12345, "python3", "127.0.0.1:8080")]
    )
    killed = []
    monkeypatch.setattr(commands.os, "kill", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    commands.port_kill(8080)
    assert killed == [12345]
    out = capsys.readouterr().out
    assert "12345" in out


def test_port_kill_cancel(monkeypatch, capsys):
    monkeypatch.setattr(
        commands, "_lookup_port", lambda port: [(12345, "python3", "127.0.0.1:8080")]
    )
    killed = []
    monkeypatch.setattr(commands.os, "kill", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
    commands.port_kill(8080)
    assert killed == []


def test_port_handler_list_subcommand(monkeypatch, capsys):
    fake = (
        "State Recv-Q Send-Q Local-Address Peer-Address Process\n"
        "LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:* "
        'users:(("python3",pid=12345,fd=3))'
    )
    _mock_ss(monkeypatch, fake)
    commands.port_handler("list")
    out = capsys.readouterr().out
    assert "Listening TCP" in out or "Port TCP" in out
    assert "8080" in out


def test_port_handler_kill_no_number(monkeypatch, capsys):
    commands.port_handler("kill")
    out = capsys.readouterr().out
    assert "Usage" in out or "Pemakaian" in out