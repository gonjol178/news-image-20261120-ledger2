#!/usr/bin/env python3
"""The World Ledger — entrypoint for make.fun news-image-20261120.

Copies the pre-rendered broadsheet (assets/entry.png, built by
compose.py) to the output directory as entry.png. Standard library
only, no network: the same bytes on every run.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
