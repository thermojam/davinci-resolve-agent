import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "davinci-console-bridge"
SKILL = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


def load_script(name):
    path = SKILL_DIR / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


class ConsoleToolTests(unittest.TestCase):
    def test_find_tool_falls_back_to_homebrew(self):
        module = load_script("check_environment")
        with patch.object(module.shutil, "which", return_value=None):
            self.assertEqual(module.find_tool("ffprobe"), Path("/opt/homebrew/bin/ffprobe"))

    def test_environment_reports_missing_target_without_mutation(self):
        module = load_script("check_environment")
        missing = Path(tempfile.gettempdir()) / "missing-resolve-task.py"
        report = module.check_environment(missing)
        self.assertFalse(report["target_exists"])
        self.assertIn("resolve_app", report)
        self.assertIn("resolve_api_readme", report)
        self.assertIn("ffmpeg", report)
        self.assertIn("ffprobe", report)

    def test_generated_command_executes_main_with_injected_resolve(self):
        module = load_script("make_console_command")
        sentinel = object()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "task with spaces.py"
            target.write_text(
                "def main():\n    assert resolve is not None\n    return 7\n",
                encoding="utf-8",
            )
            command = module.make_command(target)
            namespace = {"resolve": sentinel}
            exec(command, namespace)
        self.assertEqual(namespace["result"], 7)
        self.assertIn(repr(str(target.resolve())), command)
        self.assertNotIn("open(", command)

    def test_command_generator_rejects_missing_target(self):
        module = load_script("make_console_command")
        with self.assertRaises(FileNotFoundError):
            module.make_command(Path(tempfile.gettempdir()) / "missing-task.py")


if __name__ == "__main__":
    unittest.main()
