#!/usr/bin/env python3
"""Verify that slide code blocks are verbatim copies of files in this repository.

Convention (see README.md): a fenced code block that is preceded by

    <!-- src: examples/ros2_examples/ros2_examples/topics/minimal_publisher.py#L12-L26 -->

must equal lines 12-26 of that file (paths are relative to the repository root).
Both sides are compared after stripping trailing whitespace and removing a uniform
leading indent (textwrap.dedent), so a method lifted out of a class may be dedented.

Usage:
    python3 check_snippets.py            # check all *.md decks in this directory
    python3 check_snippets.py --fix      # locate each block in its source and (re)write the range
    python3 check_snippets.py 03-rclpy.md
"""
import pathlib
import re
import sys
import textwrap

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SRC_RE = re.compile(r'<!--\s*src:\s*(?P<path>[^\s#]+)(?:#L(?P<a>\d+)(?:-L(?P<b>\d+))?)?\s*-->')
FENCE_RE = re.compile(r'^\s*```')


def normalise(lines):
    return textwrap.dedent('\n'.join(line.rstrip() for line in lines))


def find_blocks(md_lines):
    """Yield (comment_line_index, path, a, b, block_lines) for every src comment."""
    i = 0
    while i < len(md_lines):
        m = SRC_RE.search(md_lines[i])
        if not m:
            i += 1
            continue
        j = i + 1
        while j < len(md_lines) and not FENCE_RE.match(md_lines[j]):
            if md_lines[j].strip() and not md_lines[j].lstrip().startswith('<'):
                break  # prose between comment and fence: no block attached
            j += 1
        if j >= len(md_lines) or not FENCE_RE.match(md_lines[j]):
            yield i, m['path'], m['a'], m['b'], None
            i += 1
            continue
        k = j + 1
        while k < len(md_lines) and not FENCE_RE.match(md_lines[k]):
            k += 1
        yield i, m['path'], m['a'], m['b'], md_lines[j + 1:k]
        i = k + 1


def locate(block, src_lines):
    """Return (a, b) 1-based inclusive range where block occurs in src_lines, or None."""
    want = normalise(block)
    n = len(block)
    for start in range(0, len(src_lines) - n + 1):
        if normalise(src_lines[start:start + n]) == want:
            return start + 1, start + n
    return None


def main(argv):
    fix = '--fix' in argv
    files = [pathlib.Path(a) for a in argv if not a.startswith('--')]
    if not files:
        files = sorted(HERE.glob('[0-9][0-9]-*.md'))

    failures = 0
    total = 0
    for md_path in files:
        md_lines = md_path.read_text().split('\n')
        changed = False
        for idx, rel, a, b, block in find_blocks(md_lines):
            total += 1
            where = f'{md_path.name}:{idx + 1}'
            src_path = ROOT / rel
            if not src_path.exists():
                print(f'FAIL {where}: {rel} does not exist')
                failures += 1
                continue
            if block is None:
                print(f'FAIL {where}: no fenced block after src comment')
                failures += 1
                continue
            src_lines = src_path.read_text().split('\n')

            if fix:
                found = locate(block, src_lines)
                if not found:
                    print(f'FAIL {where}: block not found in {rel}')
                    failures += 1
                    continue
                new = f'<!-- src: {rel}#L{found[0]}-L{found[1]} -->'
                if md_lines[idx].strip() != new:
                    md_lines[idx] = new
                    changed = True
                print(f'ok   {where}: {rel}#L{found[0]}-L{found[1]}')
                continue

            if a is None:
                print(f'FAIL {where}: missing line range (run with --fix)')
                failures += 1
                continue
            a_i, b_i = int(a), int(b or a)
            expected = normalise(src_lines[a_i - 1:b_i])
            if expected == normalise(block):
                print(f'ok   {where}: {rel}#L{a_i}-L{b_i}')
            else:
                failures += 1
                print(f'FAIL {where}: {rel}#L{a_i}-L{b_i} differs from slide block')
                for e, g in zip(expected.split('\n'), normalise(block).split('\n')):
                    if e != g:
                        print(f'       source: {e!r}\n       slide:  {g!r}')
                        break
        if fix and changed:
            md_path.write_text('\n'.join(md_lines))
            print(f'     updated {md_path.name}')

    print(f'{total - failures}/{total} snippets match')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
