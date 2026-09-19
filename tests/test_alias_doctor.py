from rydzz import commands, config


def test_alias_doctor_detects_self_loop(monkeypatch):
    monkeypatch.setattr(config, "USER_ALIASES", {"ls": "ls --color=auto"})
    monkeypatch.setitem(config.CONFIG, "rydzz_aliases", {})
    text = "\n".join(commands.alias_doctor())
    assert "ls --color=auto" in text
    assert "masih alias" in text


def test_alias_doctor_detects_cycle(monkeypatch):
    monkeypatch.setattr(config, "USER_ALIASES", {"a": "b", "b": "a"})
    monkeypatch.setitem(config.CONFIG, "rydzz_aliases", {})
    text = "\n".join(commands.alias_doctor())
    assert "'b'" in text
    assert "masih alias" in text


def test_alias_doctor_healthy(monkeypatch):
    monkeypatch.setattr(config, "USER_ALIASES", {"ll": "ls -alF"})
    monkeypatch.setitem(config.CONFIG, "rydzz_aliases", {})
    text = "\n".join(commands.alias_doctor())
    assert "ls -alF" in text
    assert "masih alias" not in text


def test_alias_doctor_chain_ends_at_real_command(monkeypatch):
    monkeypatch.setattr(config, "USER_ALIASES", {"ll": "clear", "cl": "clear"})
    monkeypatch.setitem(config.CONFIG, "rydzz_aliases", {"l": "ll"})
    text = "\n".join(commands.alias_doctor())
    # rantai l -> ll -> clear berakhir di perintah nyata (bukan loop)
    assert "l : 'll'" in text
    assert "masih alias" not in text