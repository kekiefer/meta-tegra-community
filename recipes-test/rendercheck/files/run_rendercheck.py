#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025, NVIDIA Corporation and OE4T Contributors
"""Rendercheck test suite for standalone use."""

import os
import re
import subprocess
import sys
from collections import defaultdict

RENDERCHECK = 'rendercheck'
REQUIRED_FORMAT = 'a8r8g8b8'
DISPLAY = os.environ.get('DISPLAY', ':0')

TRIANGLE_OPS = (
    'Dst,Over,OverReverse,OutReverse,Atop,Xor,Add,Saturate,DisjointDst,'
    'DisjointOver,DisjointOverReverse,DisjointOutReverse,DisjointAtop,'
    'DisjointXor,ConjointDst,ConjointOver,ConjointOverReverse,'
    'ConjointOutReverse,ConjointAtop,ConjointXor,'
    'Clear,Src,In,InReverse,Out,AtopReverse'
)

GRADIENT_OPS = 'Clear,Dst,DisjointClear,DisjointDst,ConjointClear,ConjointDst'

GRADIENT_OPS_NO_10BIT = (
    'Add,Atop,AtopReverse,ConjointAtop,ConjointAtopReverse,'
    'ConjointIn,ConjointInReverse,ConjointOut,ConjointOutReverse,'
    'ConjointOver,ConjointOverReverse,ConjointSrc,ConjointXor,'
    'DisjointAtop,DisjointAtopReverse,DisjointIn,DisjointInReverse,'
    'DisjointOut,DisjointOutReverse,DisjointOver,DisjointOverReverse,'
    'DisjointSrc,DisjointXor,In,InReverse,Out,OutReverse,Over,'
    'OverReverse,Saturate,Src,Xor'
)

BLEND_GROUP_SIZE = 5
COMPOSITE_GROUP_SIZE = 2
GRADIENT_GROUP_SIZE = 5


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def run(cmd, timeout=600):
    env = os.environ.copy()
    env['DISPLAY'] = DISPLAY
    print('  $ ' + ' '.join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


def get_formats():
    result = run([RENDERCHECK, '-f', 'GARBAGE'])
    formats = []
    for line in result.stdout.splitlines():
        if re.search(r'Ignoring', line):
            formats.append(line.split()[3])
    return formats


def main():
    # Get version
    result = run([RENDERCHECK, '--version'], timeout=5)
    version = result.stdout.split()[1] if result.stdout else '?'
    print(f'rendercheck version: {version}')

    formats = get_formats()
    print(f'Found {len(formats)} formats: {formats}')

    formats_no_required = [f for f in formats if f != REQUIRED_FORMAT]
    formats_no_10bit = [f for f in formats_no_required if '10' not in f]

    cmds = []
    cmds.append(['-t', 'fill,dcoords,scoords,mcoords,bug7366'])
    cmds.append(['-t', 'tscoords,tmcoords'])

    for chunk in chunk_list(formats_no_required, BLEND_GROUP_SIZE):
        cmds.append(['-t', 'blend', '-f', ','.join([REQUIRED_FORMAT] + chunk)])

    for chunk in chunk_list(formats_no_required, COMPOSITE_GROUP_SIZE):
        cmds.append(['-t', 'composite', '-f', ','.join([REQUIRED_FORMAT] + chunk)])

    for chunk in chunk_list(formats_no_required, COMPOSITE_GROUP_SIZE):
        cmds.append(['-t', 'cacomposite', '-f', ','.join([REQUIRED_FORMAT] + chunk)])

    cmds.append(['-t', 'triangles', '-o', TRIANGLE_OPS])

    for chunk in chunk_list(formats_no_required, GRADIENT_GROUP_SIZE):
        cmds.append(['-t', 'gradients', '-o', GRADIENT_OPS,
                     '-f', ','.join([REQUIRED_FORMAT] + chunk)])

    for chunk in chunk_list(formats_no_10bit, GRADIENT_GROUP_SIZE):
        cmds.append(['-t', 'gradients', '-o', GRADIENT_OPS_NO_10BIT,
                     '-f', ','.join([REQUIRED_FORMAT] + chunk)])

    cmds.append(['-t', 'repeat', '-o', 'Over', '-f', REQUIRED_FORMAT])

    cmds = [cmd + ['--minimalrendering'] for cmd in cmds]
    cmds = [[RENDERCHECK] + cmd for cmd in cmds]

    total_run = 0
    total_failures = 0
    subtest_errors = defaultdict(int)

    for cmd in cmds:
        result = run(cmd)
        match = re.search(r'^(\d+) tests passed of (\d+) total$', result.stdout, re.M)
        if not match:
            print(f'  ERROR: could not parse output')
            print(result.stdout[-500:])
            continue
        passed = int(match.group(1))
        total = int(match.group(2))
        failed = total - passed
        total_run += total
        total_failures += failed

        for m in re.finditer(r'(.*) test error of [\d.]+ at .* --', result.stdout, re.M):
            subtest_errors[m.group(1)] += 1

        status = 'PASS' if not failed else f'FAIL ({failed} failures)'
        print(f'  {status}: {passed}/{total}')

    print()
    print(f'Total: {total_run - total_failures}/{total_run} passed')
    if subtest_errors:
        print('Failures:')
        for name, count in sorted(subtest_errors.items()):
            print(f'  {name}: {count}x')

    return 1 if total_failures else 0


if __name__ == '__main__':
    sys.exit(main())
