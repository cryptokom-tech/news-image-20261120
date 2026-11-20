#!/usr/bin/env python3
"""Front-page summary image for Friday 20 November 2026.

Copies the bundled entry.png (36 numbered world-news stories plus a
dotted world map with numbered pins) to /output/entry.png. The copy is
checked before it is written: the PNG signature, the 1 MiB size limit,
and a byte-for-byte comparison of what was written against the bundle.
Deterministic: both runs write exactly the same bytes.

The bundled image was rendered from 36 researched stories of the day
(front page: masthead, red date banner, dotted world map with numbered
pins, three columns of numbered stories).
"""

import hashlib
import os
import sys

PNG_SIGNATURE = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
SIZE_LIMIT = 1_048_576


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    with open(source, "rb") as handle:
        data = handle.read()
    if data[:8] != PNG_SIGNATURE:
        sys.exit("bundled entry.png is not a valid PNG file")
    if len(data) > SIZE_LIMIT:
        sys.exit("entry.png exceeds the 1 MiB limit")
    os.makedirs("/output", exist_ok=True)
    target = os.path.join("/output", "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    with open(target, "rb") as handle:
        written = handle.read()
    if written != data:
        sys.exit("output does not match the bundled image")
    digest = hashlib.sha256(data).hexdigest()
    print("wrote /output/entry.png (%d bytes, sha256 %s)" % (len(data), digest))


if __name__ == "__main__":
    main()
