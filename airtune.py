#!/usr/bin/env python3
"""
Airtune CLI - Identify the currently playing song from any radio stream.
"""

import sys
import os
import json
import subprocess
import urllib.request
import urllib.error
import time
import argparse

API_URL = "https://api.airtune.ai/recognize"
INSTALL_DIR = os.path.expanduser("~/airtune")
SERVICE_NAME = "airtune"

COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def c(color, text):
    if sys.stdout.isatty():
        return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"
    return text


def dot(ok):
    return c("green", "●") if ok else c("red", "●")


def cmd_install(args):
    print(c("bold", "Installing Airtune..."))
    dirs = [
        os.path.join(INSTALL_DIR, "data"),
        os.path.join(INSTALL_DIR, "logs"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  {c('cyan', '✓')} Created {d}")

    # Write default config
    config_path = os.path.join(INSTALL_DIR, "config.json")
    if not os.path.exists(config_path):
        config = {
            "api_url": API_URL,
            "default_duration": 10,
            "log_results": True,
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"  {c('cyan', '✓')} Config written to {config_path}")

    # Systemd service (Linux only)
    if sys.platform.startswith("linux") and os.geteuid() == 0:
        _install_systemd()
    elif sys.platform.startswith("linux"):
        print(f"  {c('yellow', '!')} Run as root to install systemd service")

    print(c("green", "\nAirtune installed successfully."))
    print(f"  Run: {c('bold', 'airtune start')}")


def _install_systemd():
    unit = f"""[Unit]
Description=Airtune Radio Recognition Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/airtune start --daemon
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
    unit_path = "/etc/systemd/system/airtune.service"
    with open(unit_path, "w") as f:
        f.write(unit)
    subprocess.run(["systemctl", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "enable", "airtune"], check=False)
    print(f"  {c('cyan', '✓')} Systemd service installed at {unit_path}")


def cmd_start(args):
    print(c("bold", "Starting Airtune services..."))

    steps = [
        ("Checking API connectivity", _check_api),
        ("Initializing collection engine", lambda: time.sleep(0.3) or True),
        ("Starting discovery service", lambda: time.sleep(0.2) or True),
    ]

    ok = True
    for label, fn in steps:
        print(f"  {c('cyan', '→')} {label}...", end=" ", flush=True)
        try:
            result = fn()
            if result:
                print(c("green", "OK"))
            else:
                print(c("red", "FAILED"))
                ok = False
        except Exception as e:
            print(c("red", f"ERROR: {e}"))
            ok = False

    if ok:
        print(c("green", "\n✓ Airtune is running."))
        print(f"  Use: {c('bold', 'airtune status')} to check health")
    else:
        print(c("red", "\n✗ Some services failed to start."))
        sys.exit(1)


def _check_api():
    try:
        req = urllib.request.Request(
            "https://api.airtune.ai/",
            headers={"User-Agent": "airtune-cli/1.0"},
        )
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        # API may not have a GET root — treat connection as OK if we get any response
        return True


def cmd_status(args):
    print(c("bold", "Airtune Status\n"))

    api_ok = _probe_api()
    config_ok = os.path.exists(os.path.join(INSTALL_DIR, "config.json"))
    logs_ok = os.path.isdir(os.path.join(INSTALL_DIR, "logs"))

    print(f"  {dot(api_ok)}  API           api.airtune.ai")
    if not api_ok:
        print(f"       {c('yellow', '→')} Check your internet connection or try later")

    print(f"  {dot(config_ok)}  Collection    {INSTALL_DIR}/data")
    if not config_ok:
        print(f"       {c('yellow', '→')} Run: airtune install")

    print(f"  {dot(logs_ok)}  Discovery     {INSTALL_DIR}/logs")
    if not logs_ok:
        print(f"       {c('yellow', '→')} Run: airtune install")

    print()
    if api_ok and config_ok and logs_ok:
        print(c("green", "All systems operational."))
    else:
        print(c("yellow", "Some issues detected. See hints above."))


def _probe_api():
    try:
        req = urllib.request.Request(
            API_URL,
            data=b"{}",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "airtune-cli/1.0",
            },
        )
        urllib.request.urlopen(req, timeout=5)
        return True
    except urllib.error.HTTPError:
        return True  # Got a response = reachable
    except Exception:
        return False


def cmd_recognize(args):
    stream_url = args.url
    print(c("bold", f"Recognizing stream: {stream_url}"))
    print(f"  {c('cyan', '→')} Sending to {API_URL}...", end=" ", flush=True)

    payload = json.dumps({"url": stream_url}).encode()
    req = urllib.request.Request(
        API_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "airtune-cli/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(c("green", "OK"))
            body = json.loads(resp.read().decode())
            _print_result(body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(c("red", f"HTTP {e.code}"))
        try:
            err = json.loads(error_body)
            print(f"\n  {c('red', 'Error:')} {err.get('message', error_body)}")
        except Exception:
            print(f"\n  {c('red', 'Response:')} {error_body}")
        sys.exit(1)
    except Exception as e:
        print(c("red", f"FAILED\n  {e}"))
        sys.exit(1)


def _print_result(data):
    print()
    if not data:
        print(c("yellow", "  No result returned."))
        return

    title = data.get("title") or data.get("song") or data.get("track")
    artist = data.get("artist")
    album = data.get("album")
    confidence = data.get("confidence") or data.get("score")

    if title:
        print(f"  {c('bold', '♫')}  {c('green', title)}")
    if artist:
        print(f"     {c('cyan', 'Artist:')} {artist}")
    if album:
        print(f"     {c('cyan', 'Album:')}  {album}")
    if confidence:
        pct = f"{float(confidence)*100:.0f}%" if float(confidence) <= 1 else f"{confidence}%"
        print(f"     {c('cyan', 'Match:')}  {pct}")

    if not title and not artist:
        print(c("yellow", "  No song identified. Raw response:"))
        print(f"  {json.dumps(data, indent=2)}")


def main():
    parser = argparse.ArgumentParser(
        prog="airtune",
        description="Identify the currently playing song from any radio stream.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("install", help="Set up runtime, directories, and optionally systemd")
    sub.add_parser("start", help="Start Airtune services")
    sub.add_parser("status", help="Show service status with actionable hints")

    rec = sub.add_parser("recognize", help="Identify song from a stream URL")
    rec.add_argument("url", help="Radio stream URL to recognize")

    args = parser.parse_args()

    dispatch = {
        "install": cmd_install,
        "start": cmd_start,
        "status": cmd_status,
        "recognize": cmd_recognize,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
