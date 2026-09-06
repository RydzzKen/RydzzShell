from rydzz import completions, config


def test_build_command_list_has_builtin():
    cmds = completions.build_command_list()
    assert "help" in cmds
    assert "history" in cmds
    assert "dl" in cmds


def test_build_command_list_includes_aliases(monkeypatch):
    monkeypatch.setattr(config, "USER_ALIASES", {"cl": "clear"})
    cmds = completions.build_command_list()
    assert "cl" in cmds


def test_refresh_picks_new_alias(monkeypatch):
    monkeypatch.setattr(config, "USER_ALIASES", {"fz": "echo hi"})
    refreshed = completions.refresh()
    assert "fz" in refreshed


def test_refresh_picks_new_rydzz_alias(monkeypatch):
    monkeypatch.setitem(config.CONFIG, "rydzz_aliases", {"ll": "ls -la"})
    refreshed = completions.refresh()
    assert "ll" in refreshed


def test_refresh_includes_builtins_still():
    refreshed = completions.refresh()
    assert "exit" in refreshed