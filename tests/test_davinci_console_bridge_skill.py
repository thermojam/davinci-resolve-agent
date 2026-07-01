import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "davinci-console-bridge"
SKILL = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


class SkillContractTests(unittest.TestCase):
    def test_skill_declares_public_name_and_required_gates(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("name: davinci-console-bridge", text)
        for phrase in (
            "Brief gate",
            "Evidence gate",
            "Best-practice gate",
            "Delivery-profile gate",
            "Geometry gate",
            "Plan gate",
            "Approval gate",
            "Execution gate",
            "Verification gate",
        ):
            self.assertIn(phrase, text)

    def test_skill_requires_intake_before_mutation(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("one concise question at a time", text)
        self.assertIn("Do not create files or change Resolve", text)
        for phrase in (
            "source paths",
            "script",
            "reference",
            "destination service",
            "orientation",
            "delivery requirements",
        ):
            self.assertIn(phrase, text.lower())

    def test_skill_requires_verified_console_and_delivery_workflow(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("embedded Py3 Console", text)
        self.assertIn('globals().get("resolve")', text)
        self.assertIn("official", text)
        self.assertIn("verification date", text)
        self.assertIn("Never delete or replace a project implicitly", text)

    def test_openai_metadata_exposes_public_invocation(self):
        text = OPENAI_YAML.read_text(encoding="utf-8")
        self.assertIn('display_name: "DaVinci Console Bridge"', text)
        self.assertIn("$davinci-console-bridge", text)


if __name__ == "__main__":
    unittest.main()
