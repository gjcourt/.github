#!/usr/bin/env python3
"""Structural check for READMEs against gjcourt/.github README-STANDARD.md.

    readme_check.py [README.md] [--description "GitHub About text"]

Checks structure only — never prose, length or accuracy. Exits 1 with one
line per problem. Stdlib only, so the reusable workflow needs no installs.
"""
import argparse
import re
import sys

ORDER = {
    "tool": ["Quick start", "Usage", "Configuration", "How it works", "Development", "License"],
    "service": ["Quick start", "Usage", "Configuration", "How it works", "Development",
                "Deployment", "License"],
    "exporter": ["Why", "Metrics", "Quick start", "Configuration", "How it works", "Development",
                 "Deployment", "License"],
    "infra": ["Layout", "Making a change", "Development", "License"],
    "content": ["Layout", "Conventions", "License"],
}
REQUIRED = {
    "tool": ["Quick start", "Development", "License"],
    "service": ["Quick start", "Development", "License"],
    "exporter": ["Why", "Metrics", "Quick start", "License"],
    "infra": ["Layout", "Making a change", "License"],
    "content": ["Layout", "License"],
}
MARKER = re.compile(r"^<!--\s*readme-type:\s*([a-z]+)\s*-->\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def strip_code(lines):
    """Drop fenced code blocks so '# comment' inside them isn't a heading."""
    out, in_fence = [], False
    for ln in lines:
        if FENCE.match(ln):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(ln)
    return out


def check(text, description=None):
    problems = []
    raw = text.splitlines()
    if not raw or not MARKER.match(raw[0].strip()):
        return ["line 1: missing `<!-- readme-type: … -->` marker"]
    rtype = MARKER.match(raw[0].strip()).group(1)
    if rtype not in ORDER:
        return [f"line 1: unknown readme-type '{rtype}' (one of: {', '.join(ORDER)})"]

    lines = strip_code(raw[1:])
    body = [ln for ln in lines if ln.strip()]
    if not body or not body[0].startswith("# "):
        problems.append("first content line must be the '# name' heading")
    else:
        # tagline = first non-blank line after the H1
        after = body[1] if len(body) > 1 else ""
        if not after or after.startswith("#") or after.startswith("<!--"):
            problems.append("missing tagline: one sentence right after '# name'")
        else:
            tagline = after.strip()
            if len(tagline) > 120:
                problems.append(f"tagline is {len(tagline)} chars (max 120)")
            if description is not None:
                about = description.strip()
                if not about:
                    problems.append("GitHub About description is empty — set it to the tagline")
                elif tagline.rstrip(".") != about.rstrip("."):
                    problems.append(f"tagline != GitHub About description\n    README: {tagline}\n    About:  {about}")

    if not any(ln.startswith("**Status:**") for ln in lines):
        problems.append("missing '**Status:**' line")

    h1s = [ln for ln in lines if re.match(r"^# ", ln)]
    if len(h1s) > 1:
        problems.append(f"{len(h1s)} '# ' headings; only the title is H1 (use '##' for sections)")

    found = [ln[3:].strip() for ln in lines if ln.startswith("## ")]
    known = [h for h in found if h in ORDER[rtype]]
    for req in REQUIRED[rtype]:
        if req not in found:
            problems.append(f"missing required section '## {req}' for type '{rtype}'")
    expected = [h for h in ORDER[rtype] if h in known]
    if known != expected:
        problems.append(f"sections out of order for type '{rtype}': {' · '.join(known)}\n"
                        f"    expected: {' · '.join(expected)}")
    dupes = sorted({h for h in known if known.count(h) > 1})
    if dupes:
        problems.append(f"duplicate sections: {', '.join(dupes)}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="README.md")
    ap.add_argument("--description", help="GitHub About text to compare with the tagline")
    args = ap.parse_args()
    try:
        text = open(args.path, encoding="utf-8").read()
    except OSError as exc:
        print(f"{args.path}: {exc.strerror}")
        return 1
    problems = check(text, args.description)
    for p in problems:
        print(f"{args.path}: {p}")
    if not problems:
        print(f"{args.path}: ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
