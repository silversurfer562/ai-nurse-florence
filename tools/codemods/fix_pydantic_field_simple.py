"""Simple regex-based codemod to convert common positional Field(...) usages.

This is a best-effort tool — run in a branch and review changes.
"""

import re
import sys
from pathlib import Path

SINGLE_ARG_RE = re.compile(r"Field\(\s*([^)\n]+?)\s*\)")
TWO_ARG_RE = re.compile(r"Field\(\s*([^,\n]+)\s*,\s*('(?:[^']*)'|\"(?:[^\"]*)\")\s*\)")


def transform_code(src: str) -> str:
    # First handle two-arg patterns: Field(default, 'desc') -> Field(default=..., description='...')
    def two_arg_sub(m):
        dflt = m.group(1).strip()
        desc = m.group(2)
        return f"Field(default={dflt}, description={desc})"

    src2 = TWO_ARG_RE.sub(two_arg_sub, src)

    # Next handle single string arg: Field('desc') -> Field(description='desc')
    def single_arg_sub(m):
        inner = m.group(1).strip()
        # if it's a simple string literal, treat as description
        if inner.startswith("'") or inner.startswith('"'):
            return f"Field(description={inner})"
        # otherwise preserve as default
        return f"Field(default={inner})"

    src3 = SINGLE_ARG_RE.sub(single_arg_sub, src2)
    return src3


def run(path: str | None = None) -> int:
    target = Path(path) if path else Path(".")
    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob("*.py"))

    changed = 0
    for f in files:
        text = f.read_text(encoding="utf8")
        new = transform_code(text)
        if new != text:
            f.write_text(new, encoding="utf8")
            print(f"Rewrote: {f}")
            changed += 1
    print(f"Files changed: {changed}")
    return 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(run(path))
