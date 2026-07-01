import importlib.util
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
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
    def test_readme_guides_new_users_through_safe_resolve_workflow(self):
        self.assertTrue(README.exists(), "README.md is missing")
        text = README.read_text(encoding="utf-8")
        for phrase in (
            "$davinci-console-bridge",
            "Установка",
            "Workspace > Console > Py3",
            "подтверждения плана",
            "ориентац",
            "экспорт",
            "Типовые ошибки",
        ):
            self.assertIn(phrase, text)

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


class DeliveryValidationTests(unittest.TestCase):
    def setUp(self):
        self.module = load_script("validate_delivery")
        self.profile = {
            "verified_at": "2026-07-01",
            "source_urls": ["https://example.com/official-spec"],
            "orientation": "portrait",
            "width": 1080,
            "height": 1920,
            "frame_rate": 25,
            "min_duration": 1.0,
            "max_duration": 30.0,
            "video_codecs": ["h264"],
            "audio_codecs": ["aac"],
            "audio_channels": 2,
            "audio_sample_rate": 48000,
            "max_file_size": 10_000_000,
        }
        self.probe = {
            "width": 1080,
            "height": 1920,
            "frame_rate": 25.0,
            "duration": 20.0,
            "video_codec": "h264",
            "audio_codec": "aac",
            "audio_channels": 2,
            "audio_sample_rate": 48000,
        }

    def test_orientation_detects_landscape_portrait_and_square(self):
        self.assertEqual(self.module.orientation(1920, 1080), "landscape")
        self.assertEqual(self.module.orientation(1080, 1920), "portrait")
        self.assertEqual(self.module.orientation(1080, 1080), "square")

    def test_valid_probe_matches_profile(self):
        self.assertEqual(
            self.module.validate_probe(self.profile, self.probe, file_size=9_000_000),
            [],
        )

    def test_portrait_profile_rejects_landscape_render(self):
        probe = {**self.probe, "width": 1920, "height": 1080}
        errors = self.module.validate_probe(self.profile, probe)
        joined = " ".join(errors)
        self.assertIn("orientation", joined)
        self.assertIn("dimensions", joined)

    def test_validator_reports_media_and_limit_mismatches(self):
        probe = {
            **self.probe,
            "frame_rate": 30.0,
            "duration": 31.0,
            "video_codec": "hevc",
            "audio_codec": "pcm_s24le",
            "audio_channels": 1,
            "audio_sample_rate": 44100,
        }
        errors = self.module.validate_probe(self.profile, probe, file_size=10_000_001)
        joined = " ".join(errors)
        for phrase in (
            "frame rate",
            "duration",
            "video codec",
            "audio codec",
            "audio channels",
            "audio sample rate",
            "file size",
        ):
            self.assertIn(phrase, joined)

    def test_profile_requires_provenance_and_geometry(self):
        for key in ("verified_at", "source_urls", "orientation", "width", "height"):
            profile = {**self.profile}
            profile.pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.module.validate_probe(profile, self.probe)


class ReferenceAndTemplateTests(unittest.TestCase):
    def test_task_template_compiles_and_requires_injected_resolve(self):
        path = SKILL_DIR / "assets" / "resolve_task_template.py"
        text = path.read_text(encoding="utf-8")
        compile(text, str(path), "exec")
        self.assertIn('globals().get("resolve")', text)
        self.assertIn("embedded Py3 Console", text)
        self.assertIn("NotImplementedError", text)
        self.assertNotIn('scriptapp("Resolve")', text)
        self.assertIn("/opt/homebrew/bin", text)

    def test_console_reference_records_verified_failure_modes(self):
        text = (SKILL_DIR / "references" / "console-api.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "No such file or directory: 'ffprobe'",
            "No module named 'DaVinciResolveScript'",
            "external scripting is disabled",
            "undocumented project settings",
            "unsaved current project",
        ):
            self.assertIn(phrase, text)
        self.assertIn(
            "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt",
            text,
        )

    def test_best_practices_use_official_blackmagic_sources(self):
        text = (SKILL_DIR / "references" / "best-practices.md").read_text(
            encoding="utf-8"
        )
        urls = re.findall(r"https://[^)\s]+", text)
        self.assertGreaterEqual(len(urls), 2)
        self.assertTrue(all("blackmagicdesign.com" in url for url in urls))
        for phrase in ("Edit", "Color", "Fairlight", "Fusion", "Deliver"):
            self.assertIn(phrase, text)

    def test_delivery_reference_requires_dated_service_placement_profile(self):
        text = (SKILL_DIR / "references" / "delivery-profiles.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "service",
            "placement",
            "verified_at",
            "source_urls",
            "orientation",
            "validate_delivery.py",
        ):
            self.assertIn(phrase, text)
        self.assertIn("Do not treat platform specifications as timeless", text)


if __name__ == "__main__":
    unittest.main()
