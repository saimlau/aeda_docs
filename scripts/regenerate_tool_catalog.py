#!/usr/bin/env python3
"""Regenerate the tool-catalog pages under docs/tools/.

Walks `modulated_system/tools/` in a checked-out copy of tidyros_iphone,
parses each .py for `@tool(...)` decorators via AST (no imports — works
without ROS or the project's conda env), and emits:

  docs/tools/index.md                — alphabetical, every tool one row.
  docs/tools/<category>.md           — one page per category, with each
                                       tool's full docstring + source link.

Re-run after the upstream tools change:

    python scripts/regenerate_tool_catalog.py \\
        --source /path/to/tidyros_iphone/modulated_system

The script is idempotent — running it twice produces identical output.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

REPO_URL = "https://github.com/Pengyu-Mo/tidyros_iphone"
DOC_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = DOC_REPO_ROOT / "docs" / "tools"

# Order categories deliberately (not alphabetical) so the catalog reads
# the way an operator approaches a new robot.
CATEGORY_ORDER = [
    "perception",
    "navigation",
    "manipulator",
    "trajectory",
    "recording",
    "collection",
    "data",
    "data_analysis",
    "meta",
]
CATEGORY_BLURBS = {
    "perception":
        "See the world. Vision + grounding tools — Gemini Robotics-ER 1.6 "
        "detection, RAM++ open-set labelling, SAM3 masks, depth back-"
        "projection.",
    "navigation":
        "Move the base. Nav2-backed `navigate_to`, parking-candidate search, "
        "approach helpers, lock/unlock-base.",
    "manipulator":
        "Move the arm. Relative motion, single-joint rotation, IK + collision-"
        "aware whole-body execution, recovery from brake/reflex.",
    "trajectory":
        "Design camera paths. View-trajectory generators (sphere_orbit, "
        "look_away_return, bezier, …), feasibility search, whole-body "
        "execution.",
    "recording":
        "Capture episodes. `start_recording` / `stop_recording`, episode "
        "evaluation, keeper-manifest management.",
    "collection":
        "Drive the data-collection loop. Spec definition, stop conditions, "
        "event log, episode summary, state persistence.",
    "data":
        "Inspect a dataset's distribution. Per-axis analyzers "
        "(`analyze_*_distribution`), pairwise correlation, coverage report, "
        "and cross-dataset comparison. Consumed by the data-analyzer "
        "subagent at session start to seed the plan.",
    "data_analysis":
        "Sandbox the data-analyzer subagent uses for ad-hoc Python "
        "execution against in-memory dataset stats.",
    "meta":
        "Tool catalog about itself + supervisor I/O. Notify supervisor, "
        "inspect tool schemas, reset memory.",
}


@dataclass
class ExtractedTool:
    name: str                       # the `name=` from @tool(...)
    fn_name: str                    # the Python function name
    category: str                   # the `category=` from @tool(...)
    summary: str                    # first non-blank line of the docstring
    docstring: str                  # full docstring (cleaned)
    source_path: str                # path relative to modulated_system root
    line: int                       # 1-based line of the @tool decorator


def first_sentence(text: str) -> str:
    """First line, with trailing period if missing. Empty if no docstring."""
    text = (text or "").strip()
    if not text:
        return ""
    line = re.split(r"\n\s*\n", text)[0]
    line = " ".join(line.split())
    return line


def extract_tool_kwargs(call: ast.Call) -> dict:
    """Pull `name=`, `category=`, etc. out of a `@tool(...)` Call node."""
    out: dict = {}
    for kw in call.keywords:
        if kw.arg is None:
            continue
        try:
            out[kw.arg] = ast.literal_eval(kw.value)
        except Exception:
            # Non-literal (e.g. a constant referenced by name) — store
            # a stringified version of the AST so the catalog still shows
            # something.
            try:
                out[kw.arg] = ast.unparse(kw.value)
            except Exception:
                out[kw.arg] = "<expr>"
    return out


def find_tools_in_file(path: pathlib.Path, source_root: pathlib.Path
                       ) -> list[ExtractedTool]:
    """Return every @tool-decorated function in `path`."""
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        print(f"  ! skip {path}: {e}", file=sys.stderr)
        return []
    found: list[ExtractedTool] = []
    rel = path.relative_to(source_root).as_posix()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for deco in node.decorator_list:
            # @tool(name="...", category="...")
            if isinstance(deco, ast.Call) and \
               isinstance(deco.func, ast.Name) and deco.func.id == "tool":
                kw = extract_tool_kwargs(deco)
            # @tool  (no parens)
            elif isinstance(deco, ast.Name) and deco.id == "tool":
                kw = {}
            else:
                continue
            doc = ast.get_docstring(node, clean=True) or ""
            found.append(ExtractedTool(
                name=kw.get("name", node.name),
                fn_name=node.name,
                category=kw.get("category", "(uncategorized)"),
                summary=first_sentence(doc),
                docstring=doc,
                source_path=rel,
                line=deco.lineno,
            ))
    return found


def walk_tools(source_root: pathlib.Path) -> list[ExtractedTool]:
    """Discover every tool under `<source_root>/tools/`."""
    tools_dir = source_root / "tools"
    if not tools_dir.is_dir():
        raise SystemExit(f"no tools/ dir at {tools_dir}")
    out: list[ExtractedTool] = []
    for p in sorted(tools_dir.rglob("*.py")):
        # Skip __init__, _proposed (private), __pycache__, tests.
        parts = set(p.parts)
        if any(part.startswith("_") and part != "__init__.py"
               for part in p.relative_to(tools_dir).parts[:-1]):
            continue
        if p.name == "__init__.py":
            continue
        if "__pycache__" in parts:
            continue
        if "test_" in p.name or "_test.py" in p.name:
            continue
        out.extend(find_tools_in_file(p, source_root))
    return out


def github_url(rel: str, line: int) -> str:
    return f"{REPO_URL}/blob/main/modulated_system/{rel}#L{line}"


def write_catalog(tools: list[ExtractedTool]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_cat: dict[str, list[ExtractedTool]] = defaultdict(list)
    for t in tools:
        by_cat[t.category].append(t)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda t: t.name.lower())

    # ----- index.md ---------------------------------------------------
    by_name = sorted(tools, key=lambda t: t.name.lower())
    with open(OUT_DIR / "index.md", "w") as f:
        f.write("# Tool catalog\n\n")
        f.write(
            "Every `@tool` registered under "
            f"[`modulated_system/tools/`]({REPO_URL}/tree/main/modulated_system/tools). "
            f"Generated from source by "
            "[`scripts/regenerate_tool_catalog.py`](https://github.com/saimlau/aeda_docs/blob/main/scripts/regenerate_tool_catalog.py) "
            "— re-run after upstream changes.\n\n"
        )
        f.write(
            f"**{len(tools)} tools** across "
            f"**{len(by_cat)} categories**. The category pages "
            "(see the nav) group them with prose context; this page is the "
            "flat alphabetical view.\n\n"
        )
        f.write("| Tool | Category | Summary |\n")
        f.write("|---|---|---|\n")
        for t in by_name:
            # MkDocs Material's slugifier lowercases and keeps `_` (Python
            # identifiers stay intact). Match that exactly so the in-page
            # links resolve to the auto-generated heading anchors.
            anchor = t.name.lower()
            f.write(
                f"| [`{t.name}`]({t.category}.md#{anchor}) | "
                f"`{t.category}` | "
                f"{t.summary or '_(no docstring)_'} |\n"
            )

    # ----- category pages ---------------------------------------------
    seen_cats = set()
    for cat in CATEGORY_ORDER + sorted(
            c for c in by_cat if c not in CATEGORY_ORDER):
        if cat not in by_cat or cat in seen_cats:
            continue
        seen_cats.add(cat)
        cat_tools = by_cat[cat]
        with open(OUT_DIR / f"{cat}.md", "w") as f:
            f.write(f"# Tools — `{cat}` ({len(cat_tools)})\n\n")
            blurb = CATEGORY_BLURBS.get(cat)
            if blurb:
                f.write(blurb + "\n\n")
            # quick index
            f.write("## In this category\n\n")
            for t in cat_tools:
                # MkDocs Material's slugifier lowercases and keeps `_` (Python
            # identifiers stay intact). Match that exactly so the in-page
            # links resolve to the auto-generated heading anchors.
            anchor = t.name.lower()
                f.write(f"- [`{t.name}`](#{anchor}) — "
                        f"{t.summary or '_(no docstring)_'}\n")
            f.write("\n---\n\n")
            # full entry per tool
            for t in cat_tools:
                f.write(f"## `{t.name}`\n\n")
                f.write(
                    f"**Module:** "
                    f"[`modulated_system/{t.source_path}`]"
                    f"({github_url(t.source_path, t.line)})  ·  "
                    f"**Python function:** `{t.fn_name}`\n\n"
                )
                if t.docstring.strip():
                    # Wrap the docstring in a quoted block so MkDocs
                    # renders it verbatim (preserves bullet lists,
                    # code spans, etc.) without trying to interpret
                    # nested markdown control characters.
                    f.write(t.docstring.rstrip() + "\n\n")
                else:
                    f.write("_No docstring._\n\n")
                f.write("---\n\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--source",
        type=pathlib.Path,
        default=pathlib.Path(
            "/home/saimai/Documents/Jenn_Pengyu/tidyros_iphone/modulated_system"),
        help="Path to modulated_system root.",
    )
    args = ap.parse_args()
    if not args.source.is_dir():
        raise SystemExit(f"--source not a directory: {args.source}")
    tools = walk_tools(args.source)
    write_catalog(tools)
    print(f"wrote {len(tools)} tools across "
          f"{len(set(t.category for t in tools))} categories "
          f"into {OUT_DIR.relative_to(DOC_REPO_ROOT)}/")


if __name__ == "__main__":
    main()
