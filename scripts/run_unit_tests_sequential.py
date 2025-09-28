#!/usr/bin/env python3
"""Run unit tests sequentially with a per-test timeout to avoid hangs.

Usage: ./scripts/run_unit_tests_sequential.py

This script uses the repo venv Python to run pytest collect-only, then
invokes pytest for each collected node id with a timeout (seconds).
It sets AI_NURSE_DISABLE_REDIS=1 for deterministic runs.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PY = ROOT / '.venv' / 'bin' / 'python'
if not VENV_PY.exists():
    VENV_PY = 'python'

COLLECT_CMD = [str(VENV_PY), '-m', 'pytest', '--collect-only', '-q', 'tests/unit']
RUN_CMD_BASE = [str(VENV_PY), '-m', 'pytest', '-q']
TIMEOUT_SECONDS = 8


def collect_nodes():
    print('Collecting unit tests...')
    try:
        out = subprocess.check_output(COLLECT_CMD, cwd=ROOT, text=True)
    except subprocess.CalledProcessError as e:
        print('Failed collecting tests:', e)
        sys.exit(2)
    nodes = [line.strip() for line in out.splitlines() if line.strip() and '::' in line]
    print(f'Found {len(nodes)} test nodes')
    return nodes


def run_node(node):
    cmd = [str(x) for x in RUN_CMD_BASE] + [node]
    env = os.environ.copy()
    env['AI_NURSE_DISABLE_REDIS'] = '1'
    print(f'RUNNING ({TIMEOUT_SECONDS}s): {node}')
    try:
        subprocess.run(cmd, cwd=ROOT, env=env, check=True, timeout=TIMEOUT_SECONDS)
        print(f'PASS: {node}')
        return 0
    except subprocess.TimeoutExpired:
        print(f'TIMEOUT: {node} (>{TIMEOUT_SECONDS}s)')
        return 3
    except subprocess.CalledProcessError as e:
        print(f'FAIL: {node} (exit {e.returncode})')
        return e.returncode


def main():
    nodes = collect_nodes()
    if not nodes:
        print('No tests found')
        return 0

    failures = 0
    for node in nodes:
        rc = run_node(node)
        if rc != 0:
            failures += 1
    if failures:
        print(f'Completed with {failures} failing/timeouts')
        return 1
    print('All tests passed (sequential run)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
