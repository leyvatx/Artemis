#!/usr/bin/env python3
"""
Remove full-line Python comments starting with `#` from files under `api/`.

Rules:
- Only remove lines that start (optionally after whitespace) with `#`.
- Preserve shebang (`#!`) if present on the first line of a file.
- Do NOT remove comments that appear after code on the same line.
- Skip files under any `migrations/` directories.

Use with `--apply` to modify files in-place. Without `--apply` it will print a dry-run summary.
"""
import argparse
import os
import re
from pathlib import Path


def process_file(path: Path, apply: bool):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    if not lines:
        return False, 0

    new_lines = []
    removed = 0
    for i, line in enumerate(lines):
        # Preserve shebang on first line
        if i == 0 and line.startswith('#!'):
            new_lines.append(line)
            continue

        # If the line is only whitespace or a comment starting with #, remove it
        if re.match(r'^\s*#', line):
            removed += 1
            continue

        new_lines.append(line)

    if removed and apply:
        bak = path.with_suffix(path.suffix + '.bak')
        if not bak.exists():
            path.rename(bak)
            bak.write_text(''.join(new_lines), encoding='utf-8')
            # restore proper file: move bak content to original path
            # Actually write new content to original path
            path.write_text(''.join(new_lines), encoding='utf-8')
        else:
            # if .bak exists, just overwrite original
            path.write_text(''.join(new_lines), encoding='utf-8')

    return True, removed


def walk_and_process(root: Path, apply: bool):
    py_files = list(root.rglob('*.py'))
    total_removed = 0
    modified_files = []
    for p in py_files:
        # Skip migrations and virtualenvs
        if 'migrations' in p.parts:
            continue
        if p.match('**/__pycache__/**'):
            continue

        ok, removed = process_file(p, apply)
        if ok and removed:
            modified_files.append((str(p), removed))
            total_removed += removed

    return modified_files, total_removed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Apply changes in-place')
    parser.add_argument('--root', default='api', help='Root folder to process')
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Root path {root} does not exist")
        return 2

    modified_files, total_removed = walk_and_process(root, args.apply)

    if not args.apply:
        print(f"Dry-run: found {len(modified_files)} files with removable full-line comments, total lines: {total_removed}\n")
        for f, r in modified_files[:50]:
            print(f"- {f}: {r} lines")
        if len(modified_files) > 50:
            print(f"... and {len(modified_files)-50} more files")
        return 0

    print(f"Applied: modified {len(modified_files)} files, removed {total_removed} comment lines.")
    for f, r in modified_files:
        print(f"- {f}: {r} lines removed")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
