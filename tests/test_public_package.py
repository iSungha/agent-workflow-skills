"""Lightweight integrity checks for the published skill-document package."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class PublicPackageTests(unittest.TestCase):
    def test_each_skill_has_matching_metadata_and_sections(self):
        skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skill_files), 3)
        for skill_file in skill_files:
            with self.subTest(skill=skill_file.parent.name):
                content = skill_file.read_text(encoding="utf-8")
                match = re.match(r"\A---\s*\nname:\s*([a-z0-9-]+)\s*\ndescription:\s*.+?\n---\s*\n", content, re.S)
                self.assertIsNotNone(match, "missing valid skill frontmatter")
                self.assertEqual(match.group(1), skill_file.parent.name)
                for heading in ("## Inputs", "## Workflow", "## Output", "## Example", "## Verification and limits"):
                    self.assertIn(heading, content)
                self.assertNotRegex(content, r"\b(TODO|TBD|PLACEHOLDER)\b")

    def test_readme_links_resolve_within_repository(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
        for link in links:
            with self.subTest(link=link):
                self.assertFalse(link.startswith(("http://", "https://", "mailto:")))
                target = (ROOT / link).resolve()
                self.assertTrue(target.is_relative_to(ROOT.resolve()))
                self.assertTrue(target.exists())

    def test_examples_are_present_and_labeled_synthetic(self):
        examples = sorted((ROOT / "examples").glob("*.md"))
        self.assertGreaterEqual(len(examples), 2)
        for example in examples:
            with self.subTest(example=example.name):
                self.assertIn("fictional", example.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
