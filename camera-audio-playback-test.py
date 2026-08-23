"""Play a 15-second camera audio test; use headphones or low volume.

Run: `.venv/bin/python camera-audio-playback-test.py`
"""

from __future__ import annotations

import contextlib
import json
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

from yarl import URL

CONFIG_PATH = Path(__file__).with_name("camera.txt")
TOTAL_TIMEOUT = 45


def _print(result: dict) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))


def _read_config() -> tuple[str, str]:
    with CONFIG_PATH.open("rb") as config_file:
        config = tomllib.load(config_file)

    host = config.get("host")
    password = config.get("password")
    if not isinstance(host, str) or not isinstance(password, str):
        raise ValueError
    if not host or not password or "REPLACE_ME" in (host, password):
        raise ValueError
    if host != host.strip() or any(part in host for part in (":", "/", "?", "#", "@")):
        raise ValueError
    if any(
        ord(character) < 32 or ord(character) == 127
        for value in (host, password)
        for character in value
    ):
        raise ValueError
    return host, password


def _curl_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _stop(processes: dict[str, subprocess.Popen]) -> None:
    for process in processes.values():
        if process.poll() is None:
            process.terminate()
    for process in processes.values():
        if process.poll() is None:
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=1)
        if process.poll() is None:
            process.kill()
            process.wait()


def _statuses(processes: dict[str, subprocess.Popen]) -> dict[str, int | None]:
    return {name: process.poll() for name, process in processes.items()}


def _run(tools: dict[str, str], host: str, password: str) -> tuple[str | None, dict]:
    url = URL.build(
        scheme="http",
        host=host,
        port=80,
        path="/av.asf",
        query={"stream": "1"},
    )
    curl_config = (
        f"url = {_curl_quote(str(url))}\n"
        f"user = {_curl_quote(f'admin:{password}')}\n"
        "digest\n"
        "silent\n"
        "fail\n"
        "connect-timeout = 10\n"
        "max-time = 30\n"
    ).encode()
    processes: dict[str, subprocess.Popen] = {}
    try:
        curl = subprocess.Popen(
            [tools["curl"], "--config", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        processes["curl"] = curl
        ffmpeg = subprocess.Popen(
            [
                tools["ffmpeg"],
                "-hide_banner",
                "-loglevel",
                "error",
                "-nostdin",
                "-i",
                "pipe:0",
                "-map",
                "0:a:0",
                "-vn",
                "-t",
                "15",
                "-c:a",
                "aac",
                "-profile:a",
                "aac_low",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-b:a",
                "32k",
                "-f",
                "adts",
                "pipe:1",
            ],
            stdin=curl.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        processes["ffmpeg"] = ffmpeg
        curl.stdout.close()
        ffplay = subprocess.Popen(
            [
                tools["ffplay"],
                "-hide_banner",
                "-loglevel",
                "error",
                "-nodisp",
                "-autoexit",
                "-f",
                "aac",
                "-i",
                "pipe:0",
            ],
            stdin=ffmpeg.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        processes["ffplay"] = ffplay
        ffmpeg.stdout.close()
        with contextlib.suppress(BrokenPipeError):
            curl.stdin.write(curl_config)
        with contextlib.suppress(BrokenPipeError):
            curl.stdin.close()

        deadline = time.monotonic() + TOTAL_TIMEOUT
        for process in (ffplay, ffmpeg, curl):
            process.wait(timeout=max(0, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        _stop(processes)
        return "timeout", {"process_exit_codes": _statuses(processes)}
    except (OSError, ValueError) as error:
        _stop(processes)
        return "process_start", {
            "process_exit_codes": _statuses(processes),
            "type": type(error).__name__,
        }

    statuses = _statuses(processes)
    details = {"process_exit_codes": statuses}
    if statuses["curl"] not in (0, 23):
        return "network", details
    if statuses["ffmpeg"] != 0:
        return "conversion", details
    if statuses["ffplay"] != 0:
        return "playback", details
    return None, details


def main() -> int:
    tools = {name: shutil.which(name) for name in ("curl", "ffmpeg", "ffplay")}
    missing = [name for name, path in tools.items() if path is None]
    if missing:
        _print({"error": "missing_tools", "tools": missing})
        return 1

    try:
        host, password = _read_config()
    except (OSError, tomllib.TOMLDecodeError, TypeError, ValueError) as error:
        _print({"error": "configuration", "type": type(error).__name__})
        return 1

    error, result = _run(tools, host, password)  # type: ignore[arg-type]
    if error:
        _print({"error": error, **result})
        return 1

    heard_audio = None
    continuous = None
    if sys.stdin.isatty():
        heard_audio = (
            input("Did you hear audio? [y/N] ").strip().lower() in ("y", "yes")
        )
        continuous = (
            input("Was it continuous for 15 seconds? [y/N] ").strip().lower()
            in ("y", "yes")
        )
    _print(
        {
            "continuous_15_seconds": continuous,
            "heard_audio": heard_audio,
            **result,
            "technical_status": "pass",
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
