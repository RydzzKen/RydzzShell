import json
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin

from . import config, i18n
from .i18n import t

DEFAULT_MODEL = "gemini-3.6-flash"
DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"
TIMEOUT = 60


def _cfg():
    return {
        "enabled": config.CONFIG.get("ai", True),
        "key": str(config.CONFIG.get("ai_key", "")).strip(),
        "model": str(config.CONFIG.get("ai_model", DEFAULT_MODEL)).strip()
        or DEFAULT_MODEL,
        "base": str(config.CONFIG.get("ai_base", DEFAULT_BASE)).strip()
        or DEFAULT_BASE,
        "name": str(config.CONFIG.get("ai_nama", "RydzAgent")).strip()
        or "RydzAgent",
    }


def _system_prompt(cfg):
    return (
        t("ai.system.intro", name=cfg["name"])
        + f"\n\n{i18n.ai_overview()}\n\n"
        + t("ai.system.closing")
    )


def _build_url(cfg):
    base = cfg["base"].rstrip("/")
    return urljoin(base + "/", "chat/completions")


def _post(payload, cfg):
    """POST JSON ke endpoint OpenAI-compatible, kembalikan response terbuka."""
    req = urllib.request.Request(
        _build_url(cfg),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['key']}",
        },
    )
    try:
        return urllib.request.urlopen(req, timeout=TIMEOUT)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {detail[:300]}") from e
    except OSError as e:
        raise RuntimeError(f"Gagal terhubung: {e}") from e


def _clean_md(text):
    """Bersihkan markdown agar terbaca rapi di terminal (tanpa ** ` #)."""
    text = re.sub(r"(?m)^\s*```[^\n]*$", "", text)  # baris penanda code block
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)  # bold **x**
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)  # italic *x*
    text = re.sub(r"__([^_\n]+)__", r"\1", text)  # bold __x__
    text = re.sub(r"_([^_\n]+)_", r"\1", text)  # italic _x_
    text = re.sub(r"`([^`\n]+)`", r"\1", text)  # inline code `x`
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)  # heading #
    text = re.sub(r"(?m)^(\s*)\*+\s+", r"\1- ", text)  # bullet * / ** -> -
    return text


def _stream_answer(cfg, messages):
    payload = {"model": cfg["model"], "messages": messages, "stream": True}
    resp = _post(payload, cfg)
    pending = ""
    for raw in resp:
        line = raw.decode("utf-8", "replace").strip()
        if not line or not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
            delta = obj["choices"][0]["delta"].get("content", "") or ""
        except (json.JSONDecodeError, KeyError, IndexError):
            continue
        if not delta:
            continue
        pending += delta
        # Flush per baris agar tetap terasa streaming & markdown bisa dibersihkan
        while "\n" in pending:
            para, pending = pending.split("\n", 1)
            cleaned = _clean_md(para)
            if cleaned:
                sys.stdout.write(cleaned + "\n")
                sys.stdout.flush()
    if pending:
        cleaned = _clean_md(pending)
        if cleaned:
            sys.stdout.write(cleaned)
            sys.stdout.flush()
    sys.stdout.write("\n")


def _offline_respond(cfg, prompt):
    """Fallback tanpa key/internet: bantu dari daftar fitur lokal."""
    low = prompt.lower()
    known = {k.lower(): v for k, v in i18n.ai_topics().items()}
    for word, usage in known.items():
        if word in low:
            print(
                t(
                    "ai.offline.hit",
                    cyan=config.CYAN,
                    reset=config.RESET,
                    name=cfg["name"],
                    word=word,
                    usage=usage,
                )
            )
            print(
                t(
                    "ai.offline.tip",
                    dim=config.DIM,
                    reset=config.RESET,
                )
            )
            return
    print(
        t(
            "ai.offline.generic",
            cyan=config.CYAN,
            reset=config.RESET,
            name=cfg["name"],
        )
    )


def is_online(cfg):
    return cfg["enabled"] and bool(cfg["key"])


def chat(user_prompt):
    """Jawab pertanyaan lewat RydzAgent."""
    cfg = _cfg()
    if not cfg["enabled"]:
        print(t("ai.disabled"))
        return
    if not cfg["key"]:
        _offline_respond(cfg, user_prompt)
        return
    messages = [
        {"role": "system", "content": _system_prompt(cfg)},
        {"role": "user", "content": user_prompt},
    ]
    print(f"{config.CYAN}{cfg['name']}{config.RESET}: ", end="")
    try:
        _stream_answer(cfg, messages)
    except RuntimeError as e:
        msg = str(e)
        print(t("ai.error", red=config.RED, reset=config.RESET, msg=msg))
        if "401" in msg or "403" in msg or "API key" in msg:
            print(t("ai.key_hint"))


def explain_last_error():
    """Jelaskan error perintah terakhir (dipanggil manual via `ai error`)."""
    cfg = _cfg()
    cmd = config.LAST_CMD
    err = config.LAST_ERROR
    if not err:
        print(t("ai.no_error"))
        return
    if not cfg["key"]:
        print(
            t(
                "ai.offline.error",
                cyan=config.CYAN,
                reset=config.RESET,
                dim=config.DIM,
                name=cfg["name"],
                cmd=cmd,
                err=err,
            )
        )
        return
    prompt = t("ai.error_prompt", cmd=cmd, err=err[:2000])
    messages = [
        {"role": "system", "content": _system_prompt(cfg)},
        {"role": "user", "content": prompt},
    ]
    print(f"{config.CYAN}{cfg['name']}{config.RESET}: ", end="")
    try:
        _stream_answer(cfg, messages)
    except RuntimeError as e:
        print(t("ai.error", red=config.RED, reset=config.RESET, msg=e))


def tour():
    """Tur interaktif memperkenalkan fitur shell satu per satu."""
    cfg = _cfg()
    steps = i18n.tour_steps()
    print(t("ai.tour.title", green=config.GREEN_NEON, reset=config.RESET, name=cfg["name"]))
    for i, (judul, desc, contoh) in enumerate(steps, 1):
        print(f"\n{config.CYAN}{i}. {judul}{config.RESET} — {desc}")
        print(f"   {config.DIM}{t('ai.tour.example')}{contoh}{config.RESET}", end=" ")
        if i < len(steps):
            try:
                jawab = input(t("ai.tour.prompt")).strip().lower()
            except (KeyboardInterrupt, EOFError):
                print(t("ai.tour.stopped"))
                return
            if jawab == "q":
                print(t("ai.tour.done"))
                return
    print(t("ai.tour.done"))