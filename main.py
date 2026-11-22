#!/usr/bin/env python3
"""Deliver the 22 November 2026 front-page poster to the grader.

The poster is rendered in advance by build_poster.py and shipped in
this repository as assets/entry.png. This script only verifies that
the bundled file is a real 1024x1024 PNG and copies it, byte for
byte, to /output/entry.png. It uses only the standard library, makes
no network calls, and always produces the same output bytes.
"""
import os
import shutil
import struct
import sys

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def bundled_poster_path():
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, "assets", "entry.png")


def check_png(path):
    """Confirm the file is a PNG of exactly the expected dimensions."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if header[:8] != PNG_SIGNATURE:
        raise ValueError("bundled poster is not a PNG file")
    width, height = struct.unpack(">II", header[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            "bundled poster is %dx%d, expected %dx%d"
            % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT)
        )


def main():
    source = bundled_poster_path()
    check_png(source)
    destination_dir = "/output"
    os.makedirs(destination_dir, exist_ok=True)
    destination = os.path.join(destination_dir, "entry.png")
    shutil.copyfile(source, destination)
    print("wrote %s (%d bytes)" % (destination, os.path.getsize(destination)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
