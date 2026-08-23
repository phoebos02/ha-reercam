"""Probe camera audio safely: `.venv/bin/python camera-audio-probe.py`."""

from __future__ import annotations

import json
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

import av
from yarl import URL

CONFIG_PATH = Path(__file__).with_name("camera.txt")
SAMPLE_SECONDS = 15


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
    return host, password


def _stream_info(stream: Any) -> dict[str, Any]:
    codec = stream.codec_context
    info = {
        "codec": codec.name,
        "index": stream.index,
        "profile": codec.profile,
        "type": stream.type,
    }
    if codec.bit_rate is not None:
        info["bit_rate"] = codec.bit_rate
    if stream.type == "audio":
        info.update(
            channels=codec.channels,
            layout=codec.layout.name,
            sample_rate=codec.sample_rate,
        )
    return info


def _probe(host: str, password: str) -> dict[str, Any]:
    source = URL.build(
        scheme="http",
        user="admin",
        password=password,
        host=host,
        port=80,
        path="/av.asf",
        query={"stream": "1"},
    )
    av.logging.set_level(av.logging.PANIC)
    with av.open(str(source), timeout=(10.0, 10.0)) as container:
        streams = sorted(container.streams, key=lambda stream: stream.index)
        result = {
            "format": container.format.name,
            "packets_in_15_seconds": {str(stream.index): 0 for stream in streams},
            "streams": [_stream_info(stream) for stream in streams],
        }
        deadline = time.monotonic() + SAMPLE_SECONDS
        for packet in container.demux(*streams):
            if time.monotonic() >= deadline:
                break
            if packet.size:
                result["packets_in_15_seconds"][str(packet.stream.index)] += 1
        return result


def _fail(category: str, error: Exception) -> int:
    print(
        json.dumps({"error": category, "type": type(error).__name__}, sort_keys=True),
        file=sys.stderr,
    )
    return 1


def main() -> int:
    try:
        host, password = _read_config()
    except (OSError, tomllib.TOMLDecodeError, TypeError, ValueError) as error:
        return _fail("configuration", error)

    try:
        result = _probe(host, password)
    except Exception as error:  # PyAV exposes several FFmpeg-specific exception types.
        return _fail("probe", error)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
