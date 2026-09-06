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