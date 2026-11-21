#!/usr/bin/env python3
"""Copy the bundled front-page image to the output folder, verifying it first.

The image shipped with this entry is treated as a fixed payload: the script
only checks that it is a genuine PNG of an allowed size, copies its bytes
unchanged into /output/entry.png, and then reads the copy back to prove the
write was exact. Nothing is generated, downloaded, or modified along the way,
so running the script twice produces the same printed report.
"""

import hashlib
import os
import struct
import sys

SOURCE_NAME = "entry.png"
DEST_FOLDER = "/output"
DEST_NAME = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576


def fail(message):
    """Print an error to stderr and stop with a non-zero exit status."""
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, SOURCE_NAME)

    try:
        with open(source_path, "rb") as handle:
            payload = handle.read()
    except OSError as exc:
        fail("could not read %s: %s" % (source_path, exc))

    if len(payload) > MAX_BYTES:
        fail(
            "image is %d bytes, over the %d byte limit"
            % (len(payload), MAX_BYTES)
        )

    if payload[: len(PNG_MAGIC)] != PNG_MAGIC:
        fail("image does not start with the PNG signature")

    # The first chunk of a PNG must be IHDR; its first eight data bytes are
    # the width and height as big-endian 32-bit integers. The entry image is
    # a square 1024x1024 front page, so anything else is rejected.
    if len(payload) < 24 or payload[12:16] != b"IHDR":
        fail("image has no IHDR chunk where one is expected")
    width, height = struct.unpack(">II", payload[16:24])
    if (width, height) != (1024, 1024):
        fail("image is %dx%d, expected 1024x1024" % (width, height))

    os.makedirs(DEST_FOLDER, exist_ok=True)
    dest_path = os.path.join(DEST_FOLDER, DEST_NAME)

    try:
        with open(dest_path, "wb") as handle:
            handle.write(payload)
    except OSError as exc:
        fail("could not write %s: %s" % (dest_path, exc))

    try:
        with open(dest_path, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        fail("could not read back %s: %s" % (dest_path, exc))

    if written != payload:
        fail("written file differs from the bundled image")

    digest = hashlib.sha256(written).hexdigest()
    print("bytes: %d" % len(written))
    print("sha256: %s" % digest)


if __name__ == "__main__":
    main()
