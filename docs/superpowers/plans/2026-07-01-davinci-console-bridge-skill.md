# DaVinci Console Bridge Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, validate, version, and install a personal `$davinci-console-bridge` skill that gathers a complete production brief, plans before mutation, runs verified Resolve Free automation through the embedded Py3 Console, and validates platform-specific exports.

**Architecture:** Keep the versioned source under `skills/davinci-console-bridge` and install the validated folder at `~/.codex/skills/davinci-console-bridge`. The skill orchestrates an intake and approval workflow; small Python tools handle deterministic environment checks, Console-command generation, and delivery-profile validation. Service specifications remain task-local dated JSON profiles sourced from current official documentation instead of stale built-in presets.

**Tech Stack:** Markdown Agent Skills, Python 3 standard library, `ffprobe`, DaVinci Resolve 21 embedded Py3 Console, `unittest`, Blackmagic Resolve scripting API.

## Global Constraints

- The public invocation name is `$davinci-console-bridge`.
- Ask one concise intake question at a time and do not mutate Resolve before brief, plan, and approval gates pass.
- Treat external `scriptapp("Resolve")` as an unverified fallback; Resolve Free on this Mac uses the embedded Py3 Console and injected `resolve` object.
- Never delete or replace a project implicitly.
- Do not hardcode social-platform delivery specifications as timeless facts; store official source URLs and verification dates in task-local profiles.
- Validate orientation, dimensions, aspect ratio, frame rate, duration, codecs, audio, and file size when specified.
- Tests must not modify a live Resolve project.

---

### Task 1: Scaffold and discovery contract

**Files:**
- Create: `skills/davinci-console-bridge/SKILL.md`
- Create: `skills/davinci-console-bridge/agents/openai.yaml`
- Create: `tests/test_davinci_console_bridge_skill.py`

**Interfaces:**
- Consumes: approved design at `docs/superpowers/specs/2026-07-01-davinci-console-bridge-skill-design.md`.
- Produces: discoverable skill metadata and `SkillContractTests` that later tasks extend.

- [ ] **Step 1: Initialize the skill**

Run `init_skill.py` with `scripts,references,assets` resources and interface values:

```bash
python3 /Users/nikitamensky/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  davinci-console-bridge \
  --path skills \
  --resources scripts,references,assets \
  --interface 'display_name=DaVinci Console Bridge' \
  --interface 'short_description=Plan and automate verified DaVinci Resolve workflows' \
  --interface 'default_prompt=Use $davinci-console-bridge to gather the production brief, plan the Resolve workflow, and execute only after approval.'
```

Expected: `skills/davinci-console-bridge/SKILL.md` and `agents/openai.yaml` exist.

- [ ] **Step 2: Write the failing contract tests**

Create tests that load `SKILL.md` and assert the public name, description trigger, ordered gates, one-question intake rule, embedded Console requirement, project safety, current official delivery lookup, and export verification. Assert `agents/openai.yaml` contains `$davinci-console-bridge`.

```python
class SkillContractTests(unittest.TestCase):
    def test_skill_declares_public_name_and_required_gates(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("name: davinci-console-bridge", text)
        for phrase in ("Brief gate", "Plan gate", "Approval gate", "Verification gate"):
            self.assertIn(phrase, text)

    def test_skill_requires_embedded_console_and_current_delivery_sources(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("embedded Py3 Console", text)
        self.assertIn("official", text)
        self.assertIn("verification date", text)
```

- [ ] **Step 3: Run tests to verify RED**

Run: `python3 -m unittest tests.test_davinci_console_bridge_skill.SkillContractTests -v`

Expected: FAIL because generated placeholder content lacks required gates.

- [ ] **Step 4: Write the minimal skill workflow**

Replace the generated `SKILL.md` with concise frontmatter and an ordered workflow. Include the ten intake categories from the spec, the nine workflow gates, safety rules, resource routing, and a short quick-reference table. Keep platform values out of the skill body.

- [ ] **Step 5: Regenerate UI metadata**

Run `generate_openai_yaml.py` with the same three interface values from Step 1.

Expected: valid `agents/openai.yaml` with the public invocation in `default_prompt`.

- [ ] **Step 6: Run contract tests to verify GREEN**

Run: `python3 -m unittest tests.test_davinci_console_bridge_skill.SkillContractTests -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/davinci-console-bridge tests/test_davinci_console_bridge_skill.py
git commit -m "feat: scaffold DaVinci console bridge skill"
```

### Task 2: Environment and Console command tools

**Files:**
- Create: `skills/davinci-console-bridge/scripts/check_environment.py`
- Create: `skills/davinci-console-bridge/scripts/make_console_command.py`
- Modify: `tests/test_davinci_console_bridge_skill.py`

**Interfaces:**
- Produces: `find_tool(name: str) -> Path | None`, `check_environment(target: Path | None) -> dict`, and `make_command(target: Path) -> str`.
- `make_command` output executes a target with `resolve` injected and calls `main()`.

- [ ] **Step 1: Write failing tool tests**

Cover Homebrew fallback, missing target reporting, absolute-path encoding, and generated command execution with a fake `resolve` object and temporary target:

```python
def test_generated_command_executes_main_with_injected_resolve(self):
    target.write_text(
        "def main():\n    assert resolve is sentinel\n    return 7\n",
        encoding="utf-8",
    )
    command = module.make_command(target)
    namespace = {"resolve": sentinel}
    exec(command, namespace)
    self.assertEqual(namespace["result"], 7)
```

- [ ] **Step 2: Run focused tests to verify RED**

Run: `python3 -m unittest tests.test_davinci_console_bridge_skill.ConsoleToolTests -v`

Expected: FAIL because both scripts are absent.

- [ ] **Step 3: Implement minimal tools**

`check_environment.py` must check, without modifying Resolve: target existence, Resolve app, installed scripting README/module, `ffmpeg`, and `ffprobe`. `make_console_command.py` must resolve the target and print one pasteable line equivalent to:

```python
p=r"/absolute/task.py"; g={"__file__":p,"__name__":"resolve_console_task","resolve":resolve}; exec(open(p,encoding="utf-8").read(),g); result=g["main"]()
```

Use `repr(str(path))` rather than manual quoting.

- [ ] **Step 4: Run focused and full tests**

Run:

```bash
python3 -m unittest tests.test_davinci_console_bridge_skill.ConsoleToolTests -v
python3 -m unittest tests.test_davinci_console_bridge_skill -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/davinci-console-bridge/scripts tests/test_davinci_console_bridge_skill.py
git commit -m "feat: add Resolve console bridge tools"
```

### Task 3: Delivery profile validator

**Files:**
- Create: `skills/davinci-console-bridge/scripts/validate_delivery.py`
- Modify: `tests/test_davinci_console_bridge_skill.py`

**Interfaces:**
- Consumes: task-local JSON profile and either a rendered media path or injected probe dictionary.
- Produces: `orientation(width: int, height: int) -> str`, `validate_probe(profile: dict, probe: dict, file_size: int | None = None) -> list[str]`, and CLI exit status 0/1.

- [ ] **Step 1: Write failing validator tests**

Add profiles for landscape `1920x1080`, portrait `1080x1920`, and square `1080x1080`. Test correct detection plus rejection of swapped geometry, wrong aspect ratio, excessive duration, wrong codecs/audio channels, and oversized files.

```python
def test_portrait_profile_rejects_landscape_render(self):
    errors = validate_probe(PORTRAIT_PROFILE, {**GOOD_PROBE, "width": 1920, "height": 1080})
    self.assertIn("orientation", " ".join(errors))
```

- [ ] **Step 2: Run validator tests to verify RED**

Run: `python3 -m unittest tests.test_davinci_console_bridge_skill.DeliveryValidationTests -v`

Expected: FAIL because validator is absent.

- [ ] **Step 3: Implement profile validation and ffprobe adapter**

Require profile keys `verified_at`, `source_urls`, `orientation`, `width`, and `height`. Treat other constraints as optional. Probe media using JSON output from the resolved `ffprobe`; compare rational frame rates numerically and aspect ratios with a small tolerance. Return actionable errors without inventing unspecified limits.

- [ ] **Step 4: Run focused and full tests**

Run:

```bash
python3 -m unittest tests.test_davinci_console_bridge_skill.DeliveryValidationTests -v
python3 -m unittest tests.test_davinci_console_bridge_skill -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/davinci-console-bridge/scripts/validate_delivery.py tests/test_davinci_console_bridge_skill.py
git commit -m "feat: validate platform delivery profiles"
```

### Task 4: Resolve template and primary-source references

**Files:**
- Create: `skills/davinci-console-bridge/assets/resolve_task_template.py`
- Create: `skills/davinci-console-bridge/references/console-api.md`
- Create: `skills/davinci-console-bridge/references/best-practices.md`
- Create: `skills/davinci-console-bridge/references/delivery-profiles.md`
- Modify: `tests/test_davinci_console_bridge_skill.py`

**Interfaces:**
- Template produces `connect_resolve()`, `tool_path(name)`, `main()`, and explicit project/timeline safety checks.
- References provide routing instructions and primary-source URLs; they do not contain stale per-platform presets.

- [ ] **Step 1: Write failing asset/reference tests**

Assert that the template compiles, prefers `globals().get("resolve")`, has no unconditional external connection, and resolves Homebrew tools. Assert official Blackmagic URLs use `blackmagicdesign.com`, delivery guidance requires service plus placement, source URLs, verification date, orientation, and post-render validation.

- [ ] **Step 2: Run tests to verify RED**

Run: `python3 -m unittest tests.test_davinci_console_bridge_skill.ReferenceAndTemplateTests -v`

Expected: FAIL because assets and references are absent.

- [ ] **Step 3: Implement the task template**

Create a compact self-contained Python template. `connect_resolve()` returns the injected object first and raises a clear embedded-Console message otherwise. Include no project mutation beyond a marked `run(resolve)` function that raises `NotImplementedError`; future task implementations must fill it only after plan approval.

- [ ] **Step 4: Write the references**

Document verified errors from this project (`ffprobe` PATH, isolated globals, ignored `resolve`, undocumented settings, unsaved current project). Link the installed Blackmagic scripting README/examples and the current official Blackmagic training page for Edit, Color, Fairlight, Fusion, and Deliver. Explain how to create a dated delivery JSON profile from the selected service's official documentation.

- [ ] **Step 5: Run focused and full tests**

Run:

```bash
python3 -m unittest tests.test_davinci_console_bridge_skill.ReferenceAndTemplateTests -v
python3 -m unittest tests.test_davinci_console_bridge_skill -v
python3 -m compileall -q skills/davinci-console-bridge
```

Expected: PASS with no compile errors.

- [ ] **Step 6: Commit**

```bash
git add skills/davinci-console-bridge/assets skills/davinci-console-bridge/references tests/test_davinci_console_bridge_skill.py
git commit -m "docs: add verified Resolve workflow references"
```

### Task 5: Validate and install the personal skill

**Files:**
- Install: `~/.codex/skills/davinci-console-bridge/**`
- Verify: `skills/davinci-console-bridge/**`

**Interfaces:**
- Consumes: validated versioned source folder.
- Produces: globally discoverable `$davinci-console-bridge` skill.

- [ ] **Step 1: Run complete verification**

Run:

```bash
python3 -m unittest tests.test_davinci_console_bridge_skill -v
python3 -m compileall -q skills/davinci-console-bridge
python3 /Users/nikitamensky/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/davinci-console-bridge
python3 skills/davinci-console-bridge/scripts/check_environment.py \
  .worktrees/morphos-intro/src/morphos_intro.py
python3 skills/davinci-console-bridge/scripts/make_console_command.py \
  .worktrees/morphos-intro/src/morphos_intro.py
```

Expected: all tests PASS, validation reports success, environment check finds installed Resolve API plus `ffmpeg`/`ffprobe`, and the command contains the absolute MORPHOS script path with injected `resolve`.

- [ ] **Step 2: Install without merging unrelated files**

Copy only the validated skill folder to `~/.codex/skills/davinci-console-bridge`. If a destination already exists, stop and inspect it instead of overwriting silently.

- [ ] **Step 3: Validate the installed copy**

Run:

```bash
python3 /Users/nikitamensky/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/nikitamensky/.codex/skills/davinci-console-bridge
diff -qr skills/davinci-console-bridge /Users/nikitamensky/.codex/skills/davinci-console-bridge
```

Expected: validation success and no differences.

- [ ] **Step 4: Verify invocation metadata**

Run `rg -n 'davinci-console-bridge|\$davinci-console-bridge'` against installed `SKILL.md` and `agents/openai.yaml`.

Expected: both files identify the public skill and default invocation.

- [ ] **Step 5: Commit final verification adjustments if any**

```bash
git add skills/davinci-console-bridge tests/test_davinci_console_bridge_skill.py
git commit -m "test: verify DaVinci console bridge installation"
```

