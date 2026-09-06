import ast
import math
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote

from . import config
from .i18n import t

# --- KALKULATOR (AST whitelist — bukan eval asal-usul) ---
_MATH_FUNCS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "abs": abs,
    "round": round,
    "pow": math.pow,
    "pi": math.pi,
    "e": math.e,
}

_ALLOWED_OPERATORS = (
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
)
_ALLOWED_UNARY = (ast.UAdd, ast.USub)


def _safe_ast_eval(expr, allowed_names):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id not in allowed_names:
                raise ValueError(t("calc.unknown_name", name=node.id))
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in allowed_names:
                raise ValueError(t("calc.funcs_only"))
            if len(node.args) > 2:
                raise ValueError(t("calc.too_many_args"))
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError(t("calc.constants_only"))
        elif isinstance(node, ast.BinOp):
            if not isinstance(node.op, _ALLOWED_OPERATORS):
                raise ValueError(t("calc.op_not_allowed", op=type(node.op).__name__))
        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, _ALLOWED_UNARY):
                raise ValueError(t("calc.unary_not_allowed", op=type(node.op).__name__))
        elif isinstance(node, _ALLOWED_OPERATORS + _ALLOWED_UNARY):
            continue
        elif isinstance(node, (ast.Expression, ast.Load)):
            continue
        else:
            raise ValueError(t("calc.expr_unsupported", t=type(node).__name__))
    code = compile(tree, "<calc>", "eval")
    return eval(code, {"__builtins__": {}}, allowed_names)


def calc(expr):
    """Kalkulator aman: + - * / // % ** dan fungsi math dasar."""
    if not expr:
        print(t("calc.usage"))
        return
    try:
        result = _safe_ast_eval(expr, _MATH_FUNCS)
    except (ValueError, SyntaxError) as e:
        print(f"calc: {e}")
        return
    except ZeroDivisionError:
        print(t("calc.divzero"))
        return
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    print(f"= {result}")


# --- TIMER & STOPWATCH ---
def _parse_duration(s):
    s = s.strip().lower()
    if ":" in s:
        mm, _, ss = s.partition(":")
        return int(mm) * 60 + int(ss)
    if s.endswith("h"):
        return int(s[:-1]) * 3600
    if s.endswith("m"):
        return int(s[:-1]) * 60
    if s.endswith("s"):
        return int(s[:-1])
    return int(s)


def _fmt_seconds(sec):
    hh, rem = divmod(int(sec), 3600)
    mm, ss = divmod(rem, 60)
    if hh:
        return f"{hh:02d}:{mm:02d}:{ss:02d}"
    return f"{mm:02d}:{ss:02d}"


def timer(arg):
    """Countdown. Format: timer 90 | timer 2:30 | timer 1h30m (cancel: Ctrl+C)."""
    if not arg:
        print(t("timer.usage"))
        return
    try:
        total = _parse_duration(arg)
    except ValueError:
        print(t("timer.invalid"))
        return
    if total <= 0:
        print(t("timer.positive"))
        return

    print(t("timer.running"))
    start = time.monotonic()
    remaining = total
    try:
        while remaining > 0:
            sys.stdout.write(t("timer.remaining", time=_fmt_seconds(remaining)))
            sys.stdout.flush()
            time.sleep(min(remaining, 1))
            remaining = total - int(time.monotonic() - start)
    except KeyboardInterrupt:
        print(t("timer.cancelled"))
        return

    print(t("timer.done"))
    for _ in range(3):
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(0.4)
    print(t("timer.timeup"))


def stopwatch(arg):
    """Stopwatch sederhana (berhenti: Ctrl+C)."""
    if not arg:
        print(t("stopwatch.running"))
    start = time.monotonic()
    prev = -1
    try:
        while True:
            sec = int(time.monotonic() - start)
            if sec != prev:
                sys.stdout.write(t("stopwatch.elapsed", time=_fmt_seconds(sec)))
                sys.stdout.flush()
                prev = sec
            time.sleep(0.2)
    except KeyboardInterrupt:
        total = time.monotonic() - start
        print(t("stopwatch.stopped", time=_fmt_seconds(total), total=total))


# --- CUACA via wttr.in (gratis, tanpa API key) ---
WEATHER_UA = "curl/8.0"


def weather(city=""):
    """Tampilkan cuaca kota lewat wttr.in. Default dari .rydzzrc (weather city=)."""
    city = city.strip() or config.CONFIG.get("weather_city", "jakarta")
    url = "https://wttr.in/" + quote(city) + "?format=%l:+%C,+%t,+%w,+humidity+%h"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": WEATHER_UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8", "replace").strip()
    except urllib.error.HTTPError as e:
        if e.code >= 400:
            print(t("weather.not_found", city=city))
        else:
            print(t("weather.fetch_failed_http", code=e.code))
        return
    except Exception as e:
        print(t("weather.fetch_failed", e=e))
        return
    if not data or data.startswith("Unknown location") or "Sorry" in data:
        print(t("weather.not_found", city=city))
        return
    print(t("weather.label", cyan=config.CYAN, reset=config.RESET, data=data))