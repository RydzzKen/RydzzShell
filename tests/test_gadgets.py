from rydzz import gadgets


def test_calc_basic(capsys):
    gadgets.calc("2+2*3")
    assert "= 8" in capsys.readouterr().out


def test_calc_math_func(capsys):
    gadgets.calc("sqrt(144)")
    assert "= 12" in capsys.readouterr().out


def test_calc_injection_rejected(capsys):
    gadgets.calc("__import__('os').system('echo hack')")
    out = capsys.readouterr().out
    assert out.startswith("calc:")


def test_calc_unknown_name_rejected(capsys):
    gadgets.calc("os.getcwd()")
    out = capsys.readouterr().out
    assert out.startswith("calc:")


def test_calc_division_by_zero(capsys):
    gadgets.calc("1/0")
    assert "nol" in capsys.readouterr().out


def test_parse_duration():
    assert gadgets._parse_duration("90") == 90
    assert gadgets._parse_duration("2:30") == 150
    assert gadgets._parse_duration("1h") == 3600
    assert gadgets._parse_duration("2m") == 120
    assert gadgets._parse_duration("5s") == 5


def test_fmt_seconds():
    assert gadgets._fmt_seconds(59) == "00:59"
    assert gadgets._fmt_seconds(90) == "01:30"
    assert gadgets._fmt_seconds(3725) == "01:02:05"