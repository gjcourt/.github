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
MARKER = re.compile(r"^<!--\s*readme-type:\s*([A-Za-z-]+)\s*-->$")
# CommonMark fence: up to 3 spaces of indent, then 3+ backticks or tildes.
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
H1 = re.compile(r"^ {0,3}#(?:[ \t]|$)")
H2 = re.compile(r"^ {0,3}##[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
STATUS = re.compile(r"^\*\*Status:\*\*")


def strip_code(lines):
    """Drop fenced code blocks so '# comment' inside them isn't a heading.

    A fence closes only on the same character, at least as long, with nothing
    after it; an unclosed fence runs to the end of the document (CommonMark).
    """
    out, fence = [], None
    for ln in lines:
        m = FENCE.match(ln)
        if fence is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = m.group(1)
            else:
                out.append(ln)
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                and not m.group(2).strip():
            fence = None
    return out


def plain(text):
    """Render inline Markdown to the plain text GitHub's About box would hold."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)       # links, images
    text = re.sub(r"`([^`]*)`", r"\1", text)                    # `code`
    text = re.sub(r"(\*\*|\*)(.+?)\1", r"\2", text)             # **strong**, *em*
    text = re.sub(r"(?<!\w)(__|_)(.+?)\1(?!\w)", r"\2", text)    # _em_, not snake_case
    return " ".join(text.split()).rstrip(".")


def check(text, description=None):
    problems = []
    raw = text.lstrip("﻿").splitlines()
    m = MARKER.match(raw[0].strip()) if raw else None
    if not m:
        return ["line 1: missing `<!-- readme-type: … -->` marker"]
    rtype = m.group(1)
    if rtype not in ORDER:
        return [f"line 1: unknown readme-type '{rtype}' (one of: {', '.join(ORDER)})"]

    lines = strip_code(raw[1:])
    first = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if first is None or not lines[first].startswith("# "):
        problems.append("first content line must be the '# name' heading")
    else:
        # Tagline = the paragraph after the H1 (it may be hard-wrapped).
        rest = lines[first + 1:]
        start = next((i for i, ln in enumerate(rest) if ln.strip()), None)
        para = []
        if start is not None:
            for ln in rest[start:]:
                if not ln.strip():
                    break
                para.append(ln.strip())
        if not para or para[0].startswith(("#", "<", "**Status:**", "![")):
            problems.append("missing tagline: one sentence right after '# name'")
        else:
            tagline = plain(" ".join(para))
            if len(tagline) > 120:
                problems.append(f"tagline is {len(tagline)} chars (max 120)")
            if description is not None:
                about = " ".join(description.split()).rstrip(".")
                if not about:
                    problems.append("GitHub About description is empty — set it to the tagline")
                elif tagline != about:
                    problems.append("tagline != GitHub About description\n"
                                    f"    README: {tagline}\n    About:  {about}")

    first_h2 = next((i for i, ln in enumerate(lines) if H2.match(ln)), len(lines))
    status = [i for i, ln in enumerate(lines) if STATUS.match(ln)]
    if not status:
        problems.append("missing '**Status:**' line")
    elif status[0] > first_h2:
        problems.append("'**Status:**' line must come before the first '##' section")

    h1s = [ln for ln in lines if H1.match(ln)]
    if len(h1s) > 1:
        problems.append(f"{len(h1s)} '# ' headings; only the title is H1 (use '##' for sections)")

    found = [H2.match(ln).group(1) for ln in lines if H2.match(ln)]
    known = [h for h in found if h in ORDER[rtype]]
    canon = {h.lower(): h for h in ORDER[rtype]}
    for req in REQUIRED[rtype]:
        if req not in found:
            near = [h for h in found if h.lower() == req.lower()]
            hint = f" (found '## {near[0]}' — spell it exactly)" if near else ""
            problems.append(f"missing required section '## {req}' for type '{rtype}'{hint}")
    for h in found:
        if h not in known and h.lower() in canon and canon[h.lower()] not in REQUIRED[rtype]:
            problems.append(f"'## {h}' should be spelled '## {canon[h.lower()]}'")
    dupes = sorted({h for h in known if known.count(h) > 1})
    if dupes:
        problems.append(f"duplicate sections: {', '.join(dupes)}")
    seen = list(dict.fromkeys(known))
    expected = [h for h in ORDER[rtype] if h in seen]
    if seen != expected:
        problems.append(f"sections out of order for type '{rtype}': {' · '.join(seen)}\n"
                        f"    expected: {' · '.join(expected)}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="README.md")
    ap.add_argument("--description", help="GitHub About text to compare with the tagline")
    args = ap.parse_args()
    try:
        with open(args.path, encoding="utf-8") as fh:
            text = fh.read()
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
