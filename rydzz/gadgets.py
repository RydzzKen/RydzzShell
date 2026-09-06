import ast
import math
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote

from . import config

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
                raise ValueError(f"nama '{node.id}' tidak dikenali/diizinkan")
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in allowed_names:
                raise ValueError("hanya fungsi matematika dasar yang diizinkan")
            if len(node.args) > 2:
                raise ValueError("terlalu banyak argumen fungsi")
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("konstanta hanya angka")
        elif isinstance(node, ast.BinOp):
            if not isinstance(node.op, _ALLOWED_OPERATORS):
                raise ValueError(f"operator '{type(node.op).__name__}' tak dizinkan")
        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, _ALLOWED_UNARY):
                raise ValueError(f"operator unary '{type(node.op).__name__}' tak dizinkan")
        elif isinstance(node, _ALLOWED_OPERATORS + _ALLOWED_UNARY):
            continue
        elif isinstance(node, (ast.Expression, ast.Load)):
            continue
        else:
            raise ValueError(f"ekspresi tak didukung: {type(node).__name__}")
    code = compile(tree, "<calc>", "eval")
    return eval(code, {"__builtins__": {}}, allowed_names)


def calc(expr):
    """Kalkulator aman: + - * / // % ** dan fungsi math dasar."""
    if not expr:
        print("Guna: calc <ekspresi>  contoh: calc 2+2*3  |  calc sqrt(144)")
        return
    try:
        result = _safe_ast_eval(expr, _MATH_FUNCS)
    except (ValueError, SyntaxError) as e:
        print(f"calc: {e}")
        return
    except ZeroDivisionError:
        print("calc: pembagian dengan nol!")
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
        print("Guna: timer <detik|mm:ss>  contoh: timer 90, timer 2:30")
        return
    try:
        total = _parse_duration(arg)
    except ValueError:
        print("Durasi tidak valid. Contoh: timer 90 atau timer 2:30")
        return
    if total <= 0:
        print("Durasi harus lebih dari 0.")
        return

    print("Timer berjalan — Ctrl+C untuk batalkan.")
    start = time.monotonic()
    remaining = total
    try:
        while remaining > 0:
            sys.stdout.write(f"\r  Tersisa {_fmt_seconds(remaining)}  ")
            sys.stdout.flush()
            time.sleep(min(remaining, 1))
            remaining = total - int(time.monotonic() - start)
    except KeyboardInterrupt:
        print("\nTimer dibatalkan.")
        return

    print("\r  Selesai!                       ")
    for _ in range(3):
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(0.4)
    print("Waktu habis!")


def stopwatch(arg):
    """Stopwatch sederhana (berhenti: Ctrl+C)."""
    if not arg:
        print("Stopwatch jalan — Ctrl+C untuk berhenti.")
    start = time.monotonic()
    prev = -1
    try:
        while True:
            sec = int(time.monotonic() - start)
            if sec != prev:
                sys.stdout.write(f"\r  Elapsed {_fmt_seconds(sec)}  ")
                sys.stdout.flush()
                prev = sec
            time.sleep(0.2)
    except KeyboardInterrupt:
        total = time.monotonic() - start
        print(f"\n  Berhenti. Total: {_fmt_seconds(total)} ({total:.1f}s)")


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
            print(f"Lokasi '{city}' tidak ditemukan.")
        else:
            print(f"Gagal mengambil cuaca (butuh internet): HTTP {e.code}")
        return
    except Exception as e:
        print(f"Gagal mengambil cuaca (butuh internet): {e}")
        return
    if not data or data.startswith("Unknown location") or "Sorry" in data:
        print(f"Lokasi '{city}' tidak ditemukan.")
        return
    print(f"{config.CYAN}Cuaca:{config.RESET} {data}")