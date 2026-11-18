#!/usr/bin/env python3
"""make.fun entry: news-image-20261118.

Copies the pre-rendered entry.png (shipped next to this file) into
MAKEFUN_OUTPUT_DIR/entry.png (default /output) and verifies the output:
PNG magic bytes, size <= 1 MiB, dimensions <= 1024x1024 (parsed from
the IHDR chunk). Standard library only; deterministic byte-for-byte.
"""
import os
import shutil
import struct
import sys

MAX_BYTES = 1024 * 1024
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")

    with open(src, "rb") as fh:
        data = fh.read()
    if data[:8] != PNG_MAGIC:
        sys.exit("entry.png: bad PNG magic bytes")
    if len(data) > MAX_BYTES:
        sys.exit("entry.png: %d bytes exceeds 1 MiB" % len(data))
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIM or height > MAX_DIM:
        sys.exit("entry.png: %dx%d exceeds 1024x1024" % (width, height))

    with open(dst, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (dst, len(data), width, height))


if __name__ == "__main__":
    main()
