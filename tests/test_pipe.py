from rydzz import pipe


def test_has_pipe():
    assert pipe.has_pipe("a | b")
    assert not pipe.has_pipe("ab")


def test_split_pipes_plain():
    assert pipe.split_pipes("a | b | c") == ["a", "b", "c"]


def test_split_pipes_respect_quotes():
    parts = pipe.split_pipes('echo "a|b" | grep a')
    assert parts == ['echo "a|b"', "grep a"]


def test_single_segment_returns_none(capsys):
    assert pipe.execute_pipeline("ls") is None


def test_execute_pipeline_ls_pipe_cat(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a")
    pipe.execute_pipeline("ls | cat")
    out = capsys.readouterr().out
    assert "a.txt" in out


def test_execute_pipeline_builtin_runner_last(capsys):
    runner = lambda seg: "bravo\n" if seg == "hello" else None
    pipe.execute_pipeline("x | hello", builtin_runner=runner)
    out = capsys.readouterr().out
    assert "bravo" in out


def test_execute_pipeline_builtin_runner_ignores_other(capsys):
    runner = lambda seg: "X\n" if seg == "ok" else None
    pipe.execute_pipeline("ok | tr a-z A-Z", builtin_runner=runner)
    out = capsys.readouterr().out
    assert "X" in out


# ---------- fast-path streaming (system-only pipeline) ----------
def test_system_pipeline_streams_real_time(monkeypatch):
    calls = []
    monkeypatch.setattr(
        pipe.subprocess, "run", lambda *a, **k: calls.append((a, k))
    )
    pipe.register_builtin_names({"help"})
    pipe.execute_pipeline(
        "curl -fsSL https://x/install.sh | bash",
        stream_system=True,
    )
    assert calls, "seharusnya pipeline dilimpahkan ke OS shell"
    cmd, kwargs = calls[0]
    assert "curl -fsSL https://x/install.sh | bash" in cmd
    assert kwargs.get("shell") is True
    assert kwargs.get("capture_output") is None  # tidak di-capture


def test_builtin_pipeline_not_streamed(monkeypatch):
    calls = []
    monkeypatch.setattr(
        pipe.subprocess, "run", lambda *a, **k: calls.append((a, k))
    )
    pipe.register_builtin_names({"help"})
    pipe.execute_pipeline("help | grep deploy", stream_system=True)
    # 'help' terdaftar sebagai builtin → jalur capture lama, bukan fast-path
    assert calls
    cmd, kwargs = calls[0]
    assert kwargs.get("capture_output") is True


def test_stream_system_default_off_preserves_behavior(monkeypatch):
    calls = []
    monkeypatch.setattr(
        pipe.subprocess, "run", lambda *a, **k: calls.append((a, k))
    )
    pipe.execute_pipeline("curl -fsSL https://x/i.sh | bash")
    assert calls
    cmd, kwargs = calls[0]
    # default stream_system=False → tetap capture seperti sebelumnya
    assert kwargs.get("capture_output") is True