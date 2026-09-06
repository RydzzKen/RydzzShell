import io

from rydzz import config, i18n, shell

_INITIAL_LANG = i18n.get_language()


def _run(cmd, inputs=None):
    old_in = None
    if inputs is not None:
        old_in = __import__("sys").stdin
        __import__("sys").stdin = io.StringIO("\n".join(inputs) + "\n")
    buf = io.StringIO()
    old_out = __import__("sys").stdout
    __import__("sys").stdout = buf
    try:
        shell.handle_command(cmd)
    finally:
        if old_in is not None:
            __import__("sys").stdin = old_in
        __import__("sys").stdout = old_out
    return buf.getvalue()


def test_code_default_language_is_en():
    assert _INITIAL_LANG == "en"
    assert config.CONFIG.get("lang") == "en"


def test_id_strings_are_used_under_baseline():
    # baseline test (conftest) memakai id, string id harus ada
    assert "DAFTAR PERINTAH" in i18n.t("help.title")
    assert "Guna: mv" in i18n.t("usage.mv")


def test_switch_to_en(monkeypatch):
    monkeypatch.setattr(i18n, "_current", "id")
    i18n.set_language("en")
    assert i18n.get_language() == "en"
    assert "COMMAND LIST" in i18n.t("help.title")
    assert "Usage:" in i18n.t("usage.mv")


def test_invalid_code_rejected(monkeypatch):
    monkeypatch.setattr(i18n, "_current", "id")
    assert i18n.set_language("xx") is None
    assert i18n.get_language() == "id"


def test_placeholder_formatting():
    out = i18n.t("ok.mkdir", arg="foo")
    assert "foo" in out


def test_missing_key_falls_back_to_id(monkeypatch):
    monkeypatch.setattr(i18n, "_current", "en")
    # cari kunci yang hanya ada di id (placeholder id fallback)
    out = i18n.t("ok.mkdir", arg="x")
    assert out  # tidak memunculkan placeholder raw


def test_list_languages():
    langs = i18n.list_languages()
    assert ("id", "Bahasa Indonesia") in langs
    assert ("en", "English") in langs


def test_error_sniffing_id(monkeypatch):
    monkeypatch.setattr(i18n, "_current", "id")
    assert i18n.is_error_output("Gagal membaca file")
    assert not i18n.is_error_output("success")


def test_error_sniffing_en(monkeypatch):
    monkeypatch.setattr(i18n, "_current", "en")
    assert i18n.is_error_output("Failed to read")
    assert i18n.is_error_output("Command Not Found: foo")
    assert not i18n.is_error_output("Gagal membaca file")


def test_lang_command_empty_shows_current(monkeypatch, capsys):
    monkeypatch.setattr(i18n, "_current", "id")
    output = _run("lang")
    assert "id" in output
    assert "lang list" in output


def test_lang_command_list(monkeypatch, capsys):
    monkeypatch.setattr(i18n, "_current", "id")
    output = _run("lang list")
    assert "id" in output
    assert "en" in output


def test_lang_change_and_save(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "RYDZZRC_PATH", str(tmp_path / ".rydzzrc"))
    monkeypatch.setattr(i18n, "_current", "id")
    assert config.apply_language("en") is True
    assert i18n.get_language() == "en"
    content = (tmp_path / ".rydzzrc").read_text()
    assert "lang=en" in content


def test_lang_change_invalid(monkeypatch):
    monkeypatch.setattr(i18n, "_current", "id")
    assert config.apply_language("zz") is False
    assert i18n.get_language() == "id"


def test_lang_change_via_command(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RYDZZRC_PATH", str(tmp_path / ".rydzzrc"))
    monkeypatch.setattr(i18n, "_current", "id")
    output = _run("lang -C en")
    assert "en" in output
    assert i18n.get_language() == "en"


def test_lang_command_unknown(monkeypatch, capsys):
    monkeypatch.setattr(i18n, "_current", "id")
    output = _run("lang -C zz")
    assert "tidak dikenal" in output or "unknown" in output.lower() or "zz" in output


def test_lang_picker(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "RYDZZRC_PATH", str(tmp_path / ".rydzzrc"))
    monkeypatch.setattr(i18n, "_current", "id")
    # pilihan 2 = English
    output = _run("lang -C", inputs=["2"])
    assert "en" in output
    assert i18n.get_language() == "en"


def test_help_changes_with_language(monkeypatch):
    monkeypatch.setattr(i18n, "_current", "id")
    id_help = _run("help")
    monkeypatch.setattr(i18n, "_current", "en")
    en_help = _run("help")
    assert "DAFTAR PERINTAH" in id_help
    assert "COMMAND LIST" in en_help