"""LibCST-based codemod to rewrite positional Field(...) usages into keyword form.

This targets common patterns where authors wrote Field('desc') or Field(default, 'desc') etc.
It performs best-effort transformations; review changes in a PR.

Usage:
    python -m tools.codemods.fix_pydantic_field <path-to-code>

Note: run in a branch and review diffs before committing.
"""
from __future__ import annotations
import sys
from pathlib import Path
import libcst as cst
import libcst.matchers as m
from typing import Optional


class FieldTransformer(cst.CSTTransformer):
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        # Match Field(...) calls from pydantic
        if m.matches(updated_node.func, m.Name("Field")):
            # Some Call nodes may not expose .keywords in transformed forms; guard
            if getattr(updated_node, "keywords", None):
                return updated_node

            args = list(updated_node.args)
            if not args:
                return updated_node

            keywords = []
            # Heuristic: single string arg -> description
            if len(args) == 1:
                arg0 = args[0].value
                if m.matches(arg0, m.SimpleString()):
                    keywords.append(cst.Arg(keyword=cst.Name("description"), value=arg0))
                else:
                    # Generic default value
                    keywords.append(cst.Arg(keyword=cst.Name("default"), value=arg0))
            else:
                # Two args: assume (default, description)
                first, second, *rest = args
                keywords.append(cst.Arg(keyword=cst.Name("default"), value=first.value))
                if m.matches(second.value, m.SimpleString()):
                    keywords.append(cst.Arg(keyword=cst.Name("description"), value=second.value))
                else:
                    keywords.append(cst.Arg(keyword=cst.Name("default"), value=second.value))
                # preserve extra args as positional 'default' is ambiguous; append as-is
                for extra in rest:
                    keywords.append(extra)

            return updated_node.with_changes(args=[], keywords=keywords)
        return updated_node


def run_codemd(path: str | None = None) -> int:
    target = Path(path) if path else Path(".")
    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob("*.py"))

    for f in files:
        src = f.read_text(encoding="utf8")
        try:
            tree = cst.parse_module(src)
            mod = tree.visit(FieldTransformer())
            if mod.code != src:
                f.write_text(mod.code, encoding="utf8")
                print(f"Rewrote: {f}")
        except Exception as e:
            print(f"Failed {f}: {e}")
    return 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(run_codemd(path))
