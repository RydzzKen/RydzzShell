from rydzz import tools


def test_record_and_load_index(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DL_ROOT", str(tmp_path))
    monkeypatch.setattr(tools, "INDEX_FILE", str(tmp_path / ".index.json"))
    tools._record_download("https://youtu.be/abc", "YouTube")
    tools._record_download("https://tiktok.com/x", "TikTok")
    entries = tools._load_index()
    assert len(entries) == 2
    assert entries[0]["url"] == "https://tiktok.com/x"
    assert entries[0]["platform"] == "TikTok"


def test_record_dedupe_same_url(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DL_ROOT", str(tmp_path))
    monkeypatch.setattr(tools, "INDEX_FILE", str(tmp_path / ".index.json"))
    tools._record_download("https://youtu.be/abc", "YouTube")
    tools._record_download("https://youtu.be/abc", "YouTube")
    assert len(tools._load_index()) == 1


def test_load_index_missing_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(tools, "INDEX_FILE", str(tmp_path / ".index.json"))
    assert tools._load_index() == []


def test_redownload_lists_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(tools, "DL_ROOT", str(tmp_path))
    monkeypatch.setattr(tools, "INDEX_FILE", str(tmp_path / ".index.json"))
    tools._record_download("https://youtu.be/abc", "YouTube")
    tools.redownload([])
    out = capsys.readouterr().out
    assert "youtu.be" in out
    assert "dl redo <nomor>" in out


def test_redownload_unknown_number(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(tools, "DL_ROOT", str(tmp_path))
    monkeypatch.setattr(tools, "INDEX_FILE", str(tmp_path / ".index.json"))
    tools._record_download("https://youtu.be/abc", "YouTube")
    tools.redownload(["9"])
    assert "tidak ada" in capsys.readouterr().out


def test_redownload_no_record(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(tools, "INDEX_FILE", str(tmp_path / ".index.json"))
    tools.redownload([])
    assert "--redo" in capsys.readouterr().out


def test_platform_dir_common():
    assert tools._platform_dir("https://www.youtube.com/watch?v=abc") == "YouTube"
    assert tools._platform_dir("https://youtu.be/abc") == "YouTube"
    assert tools._platform_dir("https://www.tiktok.com/@x/video/1") == "TikTok"
    assert tools._platform_dir("https://open.spotify.com/track/1") == "Spotify"


def test_platform_dir_unknown():
    assert tools._platform_dir("https://example.com/video") == "Lainnya"


def test_platform_label_has_icon():
    label = tools.platform_label("YouTube")
    assert tools.platform_icon("YouTube") in label
    assert "YouTube" in label
    assert tools.platform_icon("TakDikenal") == "🌐"


def test_spotify_detection():
    assert any(h in "https://open.spotify.com/track/1" for h in tools.SPOTIFY_HOSTS)
    assert not any(h in "https://youtube.com/watch?v=1" for h in tools.SPOTIFY_HOSTS)


def test_ascii_encode_bases():
    assert tools.ascii_encode("A", 10) == "65"
    assert tools.ascii_encode("A", 16) == "41"
    assert tools.ascii_encode("A", 2) == "01000001"


def test_ascii_decode():
    assert tools.ascii_decode("65 66 67") == "ABC"
    assert tools.ascii_decode("41 42", 16) == "AB"
    assert tools.ascii_decode("01000001", 2) == "A"


def test_ascii_decode_invalid():
    out = tools.ascii_decode("xyz", 10)
    assert out.startswith("Error:")


def test_parse_ascii_flags():
    base, label, remaining = tools._parse_ascii_flags(["-x", "kata"])
    assert base == 16
    assert remaining == ["kata"]


def test_human_size():
    assert tools._human_size(0) == "0 B"
    assert tools._human_size(1024) == "1.0 KB"
    assert tools._human_size(5 * 1024 * 1024) == "5.0 MB"
    assert tools._human_size("bukan_angka") == "?"


def test_url_display():
    short = tools._url_display("https://youtube.com/watch")
    assert "youtube.com" in short
    long_url = "https://example.com/" + "x" * 200
    assert tools._url_display(long_url, 55).endswith("...")