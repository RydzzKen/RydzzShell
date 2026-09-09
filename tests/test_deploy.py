# -*- coding: utf-8 -*-
"""Tes untuk perintah deploy (Vercel CLI wrapper).

Semua fungsi yang memanggil binary asli 'vercel' di-mock agar tes
berjalan tanpa instalasi Vercel CLI maupun koneksi jaringan.
"""
import os

from rydzz import deploy


# ---------- parse_vercel_args ----------
def test_parse_args_empty_defaults():
    opts = deploy.parse_vercel_args([])
    assert opts == {"path": None, "prod": False, "help": False}


def test_parse_args_prod():
    opts = deploy.parse_vercel_args(["--prod"])
    assert opts["prod"] is True


def test_parse_args_path():
    opts = deploy.parse_vercel_args(["/tmp/foo"])
    assert opts["path"] == "/tmp/foo"


def test_parse_args_path_and_prod():
    opts = deploy.parse_vercel_args(["/tmp/foo", "--prod"])
    assert opts == {"path": "/tmp/foo", "prod": True, "help": False}


def test_parse_args_help():
    opts = deploy.parse_vercel_args(["--help"])
    assert opts["help"] is True


# ---------- resolve_target ----------
def test_resolve_target_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert deploy.resolve_target(None) == str(tmp_path)


def test_resolve_target_valid_dir(tmp_path):
    target = deploy.resolve_target(str(tmp_path))
    assert target == str(tmp_path)


def test_resolve_target_not_dir(capsys):
    assert deploy.resolve_target("/no/such/folder/xyz") is None
    out, _ = capsys.readouterr()
    assert "bukan folder" in out


# ---------- vercel_available ----------
def test_vercel_available_found(monkeypatch):
    monkeypatch.setattr(
        deploy.shutil, "which", lambda name: "/usr/local/bin/%s" % name
    )
    assert deploy.vercel_available() is True


def test_vercel_available_missing(monkeypatch):
    monkeypatch.setattr(deploy.shutil, "which", lambda name: None)
    assert deploy.vercel_available() is False


def test_vercel_executable_windows_alias(monkeypatch):
    monkeypatch.setattr(
        deploy.shutil,
        "which",
        lambda name: "C:\\Users\\x\\AppData\\Roaming\\npm\\vercel.cmd"
        if name == "vercel.cmd"
        else None,
    )
    assert deploy.vercel_executable() is not None


# ---------- build_vercel_command ----------
def test_build_command_preview(monkeypatch, tmp_path):
    monkeypatch.setattr(
        deploy, "vercel_executable", lambda: "/usr/bin/vercel"
    )
    cmd = deploy.build_vercel_command(str(tmp_path), prod=False)
    assert cmd == ["/usr/bin/vercel", "deploy", "--yes", str(tmp_path)]


def test_build_command_prod(monkeypatch, tmp_path):
    monkeypatch.setattr(
        deploy, "vercel_executable", lambda: "/usr/bin/vercel"
    )
    cmd = deploy.build_vercel_command(str(tmp_path), prod=True)
    assert cmd[-1] == "--prod"


# ---------- vercel_deploy (high level, semua ter-mock) ----------
def test_deploy_missing_cli_print_hint(monkeypatch, capsys):
    monkeypatch.setattr(deploy, "vercel_available", lambda: False)
    code = deploy.vercel_deploy("")
    assert code == 1
    out, _ = capsys.readouterr()
    assert "npm install -g vercel" in out


def test_deploy_help_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(deploy, "vercel_available", lambda: True)
    code = deploy.vercel_deploy("--help")
    assert code == 0
    out, _ = capsys.readouterr()
    assert "deploy vercel" in out


def test_deploy_not_dir(monkeypatch, capsys):
    monkeypatch.setattr(deploy, "vercel_available", lambda: True)
    code = deploy.vercel_deploy("/no/such/folder/xyz --prod")
    assert code == 1
    out, _ = capsys.readouterr()
    assert "bukan folder" in out


def test_deploy_not_logged_in(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(deploy, "vercel_available", lambda: True)
    monkeypatch.setattr(deploy, "_is_authenticated", lambda: False)
    code = deploy.vercel_deploy("")
    assert code == 1
    out, _ = capsys.readouterr()
    assert "vercel login" in out


def test_deploy_blocks_sandbox_home(
    monkeypatch, capsys, tmp_path
):
    monkeypatch.setattr(deploy, "vercel_available", lambda: True)
    monkeypatch.setattr(deploy.config, "CUSTOM_HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    code = deploy.vercel_deploy("")
    assert code == 1
    out, _ = capsys.readouterr()
    assert "home sandbox" in out or "sandbox home" in out


def test_deploy_success_shows_url(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(deploy, "vercel_available", lambda: True)
    monkeypatch.setattr(deploy, "_is_authenticated", lambda: True)
    monkeypatch.setattr(deploy, "vercel_executable", lambda: "/usr/bin/vercel")
    monkeypatch.setattr(deploy, "_run_deploy", lambda cmd: 0)
    monkeypatch.setattr(
        deploy, "_latest_urls",
        lambda: ["https://my-app-7q03.vercel.app"],
    )
    code = deploy.vercel_deploy("--prod")
    assert code == 0
    out, _ = capsys.readouterr()
    assert "Deployment selesai" in out
    assert "https://my-app-7q03.vercel.app" in out


def test_deploy_failure_skips_url(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(deploy, "vercel_available", lambda: True)
    monkeypatch.setattr(deploy, "_is_authenticated", lambda: True)
    monkeypatch.setattr(deploy, "vercel_executable", lambda: "/usr/bin/vercel")
    monkeypatch.setattr(deploy, "_run_deploy", lambda cmd: 3)
    monkeypatch.setattr(deploy, "_latest_urls", lambda: [])
    code = deploy.vercel_deploy("")
    assert code == 3
    out, _ = capsys.readouterr()
    assert "Deployment selesai" not in out
    assert "Gagal" in out


# ---------- _is_authenticated ----------
def test_is_authenticated_whoami_ok(monkeypatch):
    class _Res:
        returncode = 0

    monkeypatch.setattr(
        deploy, "vercel_executable", lambda: "/usr/bin/vercel"
    )
    monkeypatch.setattr(
        deploy.subprocess, "run", lambda *a, **k: _Res()
    )
    assert deploy._is_authenticated() is True


def test_is_authenticated_whoami_denied(monkeypatch):
    class _Res:
        returncode = 1

    monkeypatch.setattr(
        deploy, "vercel_executable", lambda: "/usr/bin/vercel"
    )
    monkeypatch.setattr(
        deploy.subprocess, "run", lambda *a, **k: _Res()
    )
    assert deploy._is_authenticated() is False


# ---------- _latest_urls (versi mocked) ----------
def test_latest_urls_parse(monkeypatch):
    class _Result:
        returncode = 0
        stdout = (
            "> 4 deployments found\n"
            "  https://my-app-7q03.vercel.app  [19s]  user  Sep 09  Production\n"
            "  https://my-app-old.vercel.app   [1m]   user  Sep 09\n"
        )

    monkeypatch.setattr(deploy, "vercel_executable", lambda: "/usr/bin/vercel")
    monkeypatch.setattr(
        deploy.subprocess,
        "run",
        lambda *a, **k: _Result(),
    )
    urls = deploy._latest_urls()
    assert "https://my-app-7q03.vercel.app" in urls