#!/usr/bin/env python3
"""
general-story DeepSeek pipeline entrypoint.

Delegates to ``crime-section/helper/deepseek_pipeline.py`` with ``--crime-root``
set to this package (the ``general-story/`` directory). That makes all paths
resolve here:

  • general-story/bifuracted-template/
  • general-story/stories/<slug>/
  • general-story/story-to-run/story.txt (default sync source)
  • general-story/deepseek.config.example.ini

The crime-section helper script is not modified; this file sets DEEPSEEK_CONFIG_PATH when the local INI exists, forwards --crime-root, then execs the shared pipeline.
"""
from __future__ import annotations

import os
import pathlib
import sys


def main() -> None:
    section_root = pathlib.Path(__file__).resolve().parent.parent
    repo_root = section_root.parent
    delegate = repo_root / "crime-section" / "helper" / "deepseek_pipeline.py"
    if not delegate.is_file():
        print(f"error: missing crime-section pipeline at {delegate}", file=sys.stderr)
        sys.exit(1)
    # Crime-section's bootstrap runs *before* argparse sees ``--crime-root``. Without this,
    # the first INI merge uses crime-section/deepseek.config.example.ini (wrong precedence).
    ini_here = section_root / "deepseek.config.example.ini"
    if ini_here.is_file():
        os.environ.setdefault("DEEPSEEK_CONFIG_PATH", str(ini_here.resolve()))
    argv = [
        sys.executable,
        str(delegate),
        "--crime-root",
        str(section_root),
        *sys.argv[1:],
    ]
    os.execv(sys.executable, argv)


if __name__ == "__main__":
    main()
