import pytest

from rydzz import config


@pytest.fixture
def history_tmp(monkeypatch, tmp_path):
    hfile = tmp_path / ".rydzz_history"
    monkeypatch.setattr(config, "HISTORY_FILE", str(hfile))
    config.COMMAND_HISTORY.clear()
    return hfile


def test_append_persists(history_tmp):
    config.append_history("gs")
    config.append_history("gp origin main")
    assert history_tmp.read_text().splitlines() == ["gs", "gp origin main"]


def test_load_back(history_tmp):
    config.append_history("gs")
    config.append_history("gp")
    config.COMMAND_HISTORY.clear()
    config.load_history()
    assert config.COMMAND_HISTORY == ["gs", "gp"]


def test_consecutive_dedupe(history_tmp):
    config.append_history("gc pesan")
    config.append_history("gc pesan")
    assert config.COMMAND_HISTORY == ["gc pesan"]
    assert len(history_tmp.read_text().splitlines()) == 1


def test_respects_history_limit(history_tmp, monkeypatch):
    monkeypatch.setattr(config, "HISTORY_LIMIT", 3)
    for i in range(6):
        config.append_history(f"cmd{i}")
    assert config.COMMAND_HISTORY == ["cmd3", "cmd4", "cmd5"]


def test_flush_clear(history_tmp):
    config.append_history("gs")
    config.append_history("gp")
    config.COMMAND_HISTORY.clear()
    config._flush_history_buffer()
    assert config.COMMAND_HISTORY == []
    config.load_history()
    assert config.COMMAND_HISTORY == []


def test_append_disabled_by_config(history_tmp, monkeypatch):
    monkeypatch.setitem(config.CONFIG, "history", False)
    config.append_history("gs")
    assert config.COMMAND_HISTORY == []
    assert not history_tmp.exists()