"""Unit tests for scripts/readme_check.py. Run: python3 -m unittest discover -s tests"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from readme_check import check  # noqa: E402

HEAD = "<!-- readme-type: tool -->\n# name\n\nDoes a thing\n\n**Status:** in use.\n\n"
SECTIONS = "## Quick start\n\nx\n\n## Development\n\nx\n\n## License\n\nx\n"


def readme(middle="", head=HEAD, sections=SECTIONS):
    return head + middle + sections


class Valid(unittest.TestCase):
    def test_minimal_tool_passes(self):
        self.assertEqual(check(readme()), [])

    def test_templates_pass(self):
        for t in sorted((ROOT / "templates" / "readme").glob("*.md")):
            with self.subTest(template=t.name):
                self.assertEqual(check(t.read_text(encoding="utf-8")), [])

    def test_bom_and_crlf(self):
        self.assertEqual(check("﻿" + readme().replace("\n", "\r\n")), [])


class Marker(unittest.TestCase):
    def test_missing(self):
        self.assertIn("marker", check("# name\n")[0])

    def test_empty_file(self):
        self.assertIn("marker", check("")[0])

    def test_unknown_type(self):
        self.assertIn("unknown readme-type 'Tool'", check(readme(head=HEAD.replace("tool", "Tool")))[0])


class Fences(unittest.TestCase):
    def assertIgnored(self, block):
        self.assertEqual(check(readme(block + "\n\n")), [], block)

    def test_backtick_fence_with_language(self):
        self.assertIgnored("```bash\n# comment\n## Usage\n```")

    def test_tilde_fence(self):
        self.assertIgnored("~~~\n# comment\n~~~")

    def test_tildes_inside_backticks_do_not_close(self):
        self.assertIgnored("```\n~~~\n# comment\n```")

    def test_shorter_fence_does_not_close_longer(self):
        self.assertIgnored("````markdown\n```\n# comment\n```\n````")

    def test_fence_indented_up_to_three_spaces(self):
        self.assertIgnored("   ```\n# comment\n   ```")

    def test_closing_fence_with_info_string_does_not_close(self):
        self.assertIgnored("```\n```python\n# comment\n```")

    def test_unclosed_fence_swallows_rest(self):
        # CommonMark: an unclosed fence runs to the end, so the sections vanish.
        problems = check(readme("```\n"))
        self.assertTrue(any("missing required section '## Quick start'" in p for p in problems))


class Headings(unittest.TestCase):
    def test_second_h1(self):
        self.assertTrue(any("'# ' headings" in p for p in check(readme("# Another\n\n"))))

    def test_hash_without_space_is_not_heading(self):
        self.assertEqual(check(readme("#hashtag\n\n")), [])

    def test_first_line_not_h1(self):
        self.assertIn("'# name'", check(readme(head="<!-- readme-type: tool -->\nname\n\nx\n\n**Status:** y\n\n"))[0])

    def test_closing_hashes_and_trailing_space(self):
        self.assertEqual(check(readme(sections=SECTIONS.replace("## License", "## License ##  "))), [])


class Tagline(unittest.TestCase):
    def test_missing_when_status_follows_h1(self):
        r = "<!-- readme-type: tool -->\n# name\n\n**Status:** y\n\n" + SECTIONS
        self.assertTrue(any("missing tagline" in p for p in check(r)))

    def test_missing_when_comment_or_badge_follows_h1(self):
        for between in ("<!-- note -->", "![build](b.svg)", "<img src=x>"):
            with self.subTest(between=between):
                r = f"<!-- readme-type: tool -->\n# name\n\n{between}\n\nDoes a thing\n\n**Status:** y\n\n"
                self.assertTrue(any("missing tagline" in p for p in check(r + SECTIONS)))

    def test_too_long(self):
        r = readme(head=HEAD.replace("Does a thing", "x" * 121))
        self.assertTrue(any("121 chars" in p for p in check(r)))

    def test_matches_about(self):
        self.assertEqual(check(readme(), "Does a thing"), [])

    def test_trailing_period_and_whitespace_either_side(self):
        r = readme(head=HEAD.replace("Does a thing", "Does a thing.  "))
        self.assertEqual(check(r, "  Does a thing"), [])
        self.assertEqual(check(readme(), "Does a thing.\n"), [])

    def test_mismatch(self):
        self.assertTrue(any("!= GitHub About" in p for p in check(readme(), "Does another thing")))

    def test_empty_about(self):
        self.assertTrue(any("About description is empty" in p for p in check(readme(), "")))

    def test_inline_markdown_compares_as_plain_text(self):
        r = readme(head=HEAD.replace("Does a thing", "Does **a** `thing` for [you](https://x.y)"))
        self.assertEqual(check(r, "Does a thing for you"), [])

    def test_snake_case_is_not_emphasis(self):
        r = readme(head=HEAD.replace("Does a thing", "Exports node_cpu_seconds"))
        self.assertEqual(check(r, "Exports node_cpu_seconds"), [])

    def test_hard_wrapped_tagline_is_one_sentence(self):
        r = readme(head=HEAD.replace("Does a thing", "Does a thing\nacross two lines"))
        self.assertEqual(check(r, "Does a thing across two lines"), [])


class Status(unittest.TestCase):
    def test_missing(self):
        self.assertTrue(any("Status" in p for p in check(readme(head=HEAD.replace("**Status:** in use.\n", "")))))

    def test_must_precede_sections(self):
        r = readme(head=HEAD.replace("**Status:** in use.\n", ""), sections=SECTIONS + "\n**Status:** late\n")
        self.assertTrue(any("before the first '##'" in p for p in check(r)))


class Sections(unittest.TestCase):
    def test_missing_required(self):
        r = readme(sections="## Quick start\n\n## License\n")
        self.assertEqual(check(r), ["missing required section '## Development' for type 'tool'"])

    def test_misspelled_required_gets_hint(self):
        r = readme(sections=SECTIONS.replace("Quick start", "Quick Start"))
        self.assertTrue(any("found '## Quick Start'" in p for p in check(r)))

    def test_misspelled_optional(self):
        r = readme(sections=SECTIONS.replace("## Development", "## Usage\n\n## How It Works\n\n## Development"))
        self.assertEqual(check(r), ["'## How It Works' should be spelled '## How it works'"])

    def test_out_of_order(self):
        r = readme(sections="## Development\n\n## Quick start\n\n## License\n")
        self.assertTrue(any("out of order" in p for p in check(r)))

    def test_unknown_sections_interleaved_are_fine(self):
        r = readme(sections="## Quick start\n\n## FAQ\n\n## Development\n\n## Credits\n\n## License\n")
        self.assertEqual(check(r), [])

    def test_duplicate_reported_once_not_as_order(self):
        r = readme(sections=SECTIONS + "\n## Quick start\n")
        self.assertEqual(check(r), ["duplicate sections: Quick start"])

    def test_heading_in_html_details_counts(self):
        # A '## ' line inside <details> is still a Markdown heading on GitHub
        # when separated by blank lines; the check treats it as one.
        r = readme(sections="## Quick start\n\n<details>\n\n## Usage\n\n</details>\n\n## Development\n\n## License\n")
        self.assertEqual(check(r), [])

    def test_types_have_own_required(self):
        r = "<!-- readme-type: content -->\n# n\n\nt\n\n**Status:** s\n\n## Layout\n\n## License\n"
        self.assertEqual(check(r), [])
        self.assertTrue(check(r.replace("content", "exporter")))


if __name__ == "__main__":
    unittest.main()
