# MORPHOS Intro Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать и проверить проект DaVinci Resolve с 25-секундной заставкой «Пробуждение MORPHOS», а также экспортировать готовый MP4.

**Architecture:** Один Python-модуль хранит детерминированный монтажный лист и чистые функции расчёта кадров, а тонкий адаптер вызывает установленный DaVinci Resolve 21 scripting API. Звук извлекается из `morph_manifest.mov` во временный WAV с короткими фейдами, затем видеофрагменты и звуковая дорожка помещаются в новый таймлайн и рендерятся самим Resolve.

**Tech Stack:** Python 3 standard library, `unittest`, DaVinci Resolve 21 Python API, `ffmpeg`, `ffprobe`.

## Global Constraints

- Таймлайн и экспорт: 1920×1080, 25 FPS, 16:9.
- Длительность: ровно 625 кадров, то есть 25 секунд.
- Проект: `MORPHOS — Пробуждение`; таймлайн: `MORPHOS Intro 25s`.
- Исходники читаются только из `/Users/nikitamensky/Desktop/Hobbie/MORPHOS/video` и не изменяются.
- Не добавлять сторонние изображения, музыку, логотипы или текст.
- Экспорт: H.264 MP4 со стереозвуком AAC.

---

### Task 1: Детерминированный монтажный лист

**Files:**
- Create: `src/morphos_intro.py`
- Create: `tests/test_morphos_intro.py`

**Interfaces:**
- Produces: `Segment(filename: str, source_in_seconds: float, duration_frames: int, phase: str)`, `EDIT_PLAN: tuple[Segment, ...]`, `validate_edit_plan(source_dir: Path) -> list[str]`, `timeline_duration_frames(segments) -> int`.

- [ ] **Step 1: Write the failing tests**

```python
class EditPlanTests(unittest.TestCase):
    def test_plan_is_exactly_25_seconds(self):
        self.assertEqual(timeline_duration_frames(EDIT_PLAN), 625)

    def test_plan_has_expected_story_order(self):
        self.assertEqual(
            [segment.phase for segment in EDIT_PLAN],
            ["signal", "awakening", "awakening", "activation", "activation",
             "activation", "response", "response", "response", "impulse",
             "impulse", "hero"],
        )

    def test_all_sources_exist_and_are_long_enough(self):
        self.assertEqual(validate_edit_plan(SOURCE_DIR), [])
```

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests/test_morphos_intro.py -v`

Expected: FAIL because `src.morphos_intro` does not exist.

- [ ] **Step 3: Implement the minimal edit plan**

Use these clips and durations, in order:

```python
EDIT_PLAN = (
    Segment("morph_manifest.mov", 0.0, 75, "signal"),
    Segment("b_Prompt__Extreme_wide.mp4", 1.0, 62, "awakening"),
    Segment("a_Prompt__Cinematic_zo.mp4", 2.0, 50, "awakening"),
    Segment("morph-hands.mp4", 2.0, 44, "activation"),
    Segment("kling-2.6-pro-image-to-video-fal_b_Prompt__Cinematic_wi.mp4", 2.0, 44, "activation"),
    Segment("grok-imagine-video-720p_a_Prompt__Medium_wide_.mp4", 2.0, 37, "activation"),
    Segment("a_Prompt__Wide_profile.mp4", 2.0, 38, "response"),
    Segment("a_Prompt__Wide_cinemat.mp4", 3.0, 37, "response"),
    Segment("grok-imagine-video-720p_b_Prompt__Wide_cinemat.mp4", 3.0, 38, "response"),
    Segment("a_Prompt___Masterpiece.mp4", 2.0, 50, "impulse"),
    Segment("b_Prompt___8K_cinemati.mp4", 2.0, 75, "impulse"),
    Segment("pixverse-v5.6-image-to-video_b_Prompt___8K_Ultra-re.mp4", 2.0, 75, "hero"),
)
```

`validate_edit_plan` must report missing files and clips whose probed duration is shorter than `source_in_seconds + duration_frames / 25`. Use `ffprobe` through `subprocess.run(..., check=True, capture_output=True, text=True)`.

- [ ] **Step 4: Run tests and verify pass**

Run: `python3 -m unittest tests/test_morphos_intro.py -v`

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/morphos_intro.py tests/test_morphos_intro.py
git commit -m "feat: define MORPHOS intro edit plan"
```

---

### Task 2: Сборка проекта через DaVinci API

**Files:**
- Modify: `src/morphos_intro.py`
- Modify: `tests/test_morphos_intro.py`

**Interfaces:**
- Consumes: `EDIT_PLAN`, `Segment`, `SOURCE_DIR` from Task 1.
- Produces: `source_frame_range(segment, native_fps) -> tuple[int, int]`, `create_project(resolve) -> Project`, `build_timeline(resolve, project, source_dir: Path, audio_path: Path) -> Timeline`.

- [ ] **Step 1: Write failing calculation and adapter tests**

```python
def test_source_frame_range_uses_native_rate(self):
    segment = Segment("clip.mp4", 2.0, 50, "activation")
    self.assertEqual(source_frame_range(segment, 24.0), (48, 95))

def test_create_project_sets_required_settings(self):
    project = create_project(self.resolve)
    self.assertEqual(project.settings["timelineFrameRate"], "25")
    self.assertEqual(project.settings["timelineResolutionWidth"], "1920")
    self.assertEqual(project.settings["timelineResolutionHeight"], "1080")
```

The fake Resolve objects must implement only the API methods called by the production adapter and record their arguments.

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests/test_morphos_intro.py -v`

Expected: FAIL because adapter functions are undefined.

- [ ] **Step 3: Implement project and timeline construction**

Implementation requirements:

```python
project_manager.CreateProject("MORPHOS — Пробуждение", str(ARTIFACT_DIR))
project.SetSetting("timelineFrameRate", "25")
project.SetSetting("timelinePlaybackFrameRate", "25")
project.SetSetting("timelineResolutionWidth", "1920")
project.SetSetting("timelineResolutionHeight", "1080")
media_pool.CreateEmptyTimeline("MORPHOS Intro 25s")
```

Import only the 12 plan files plus the generated WAV. Append every video segment with `mediaType: 1`, `trackIndex: 1`, and consecutive `recordFrame` positions. Calculate native source frame ranges from each imported item's `GetClipProperty("FPS")`; use inclusive `endFrame = startFrame + round(duration_frames * native_fps / 25) - 1`. Append the WAV with `mediaType: 2`, `trackIndex: 1`, `startFrame: 0`, `endFrame: 624`, and the timeline start as `recordFrame`. Set timeline scaling to crop centrally only where needed and add phase markers at frames 0, 75, 188, 275, 475, and 550.

- [ ] **Step 4: Run all tests and verify pass**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/morphos_intro.py tests/test_morphos_intro.py
git commit -m "feat: build MORPHOS timeline in Resolve"
```

---

### Task 3: Звук, рендер и проверка артефактов

**Files:**
- Modify: `src/morphos_intro.py`
- Modify: `tests/test_morphos_intro.py`
- Create at runtime: `artifacts/MORPHOS_atmosphere.wav`
- Create at runtime: `artifacts/MORPHOS_Intro_25s.mp4`
- Create at runtime: `artifacts/MORPHOS_Probuzenie.drp`

**Interfaces:**
- Consumes: project and timeline from Task 2.
- Produces: `prepare_audio(source: Path, destination: Path)`, `render_project(project, output_dir: Path) -> Path`, `verify_render(path: Path) -> list[str]`, `main() -> int`.

- [ ] **Step 1: Write failing render-verification tests**

```python
def test_verify_render_accepts_required_probe(self):
    probe = {"duration": 25.0, "width": 1920, "height": 1080,
             "fps": 25.0, "video_codec": "h264", "has_audio": True}
    self.assertEqual(validate_probe(probe), [])

def test_verify_render_rejects_wrong_duration(self):
    probe = {"duration": 19.0, "width": 1920, "height": 1080,
             "fps": 25.0, "video_codec": "h264", "has_audio": True}
    self.assertIn("duration", " ".join(validate_probe(probe)))
```

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests/test_morphos_intro.py -v`

Expected: FAIL because probe validation is undefined.

- [ ] **Step 3: Implement audio preparation, render, export, and CLI**

`prepare_audio` must run:

```bash
ffmpeg -ss 0 -t 25 -i morph_manifest.mov -vn -af "afade=t=in:st=0:d=0.5,afade=t=out:st=24.5:d=0.5,alimiter=limit=0.95" -ar 48000 -ac 2 -c:a pcm_s24le MORPHOS_atmosphere.wav
```

Rendering must set single-clip mode, choose MP4/H.264 from `GetRenderFormats()` and `GetRenderCodecs("mp4")`, then use:

```python
project.SetRenderSettings({
    "SelectAllFrames": True,
    "TargetDir": str(output_dir),
    "CustomName": "MORPHOS_Intro_25s",
    "ExportVideo": True,
    "ExportAudio": True,
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": 25,
    "AudioCodec": "aac",
    "AudioSampleRate": 48000,
    "PixelAspectRatio": "square",
    "VideoQuality": "Best",
})
```

Poll `IsRenderingInProgress()` at one-second intervals. Save the project and export it with `project_manager.ExportProject("MORPHOS — Пробуждение", drp_path)`. `main()` must fail without deleting or replacing an existing project of the same name, print actionable errors, and return non-zero on validation, API, render, or probe failure.

- [ ] **Step 4: Run tests**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 5: Start Resolve and run the builder**

Run Resolve, then execute:

```bash
RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting" \
RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so" \
PYTHONPATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules" \
python3 src/morphos_intro.py
```

Expected: project and timeline names are printed, render reaches 100%, `.mp4` and `.drp` paths are printed.

- [ ] **Step 6: Verify the final media independently**

Run:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,channels -of json artifacts/MORPHOS_Intro_25s.mp4
```

Expected: duration approximately 25 seconds, H.264 video at 1920×1080 and 25 FPS, plus an AAC stereo audio stream.

- [ ] **Step 7: Commit**

```bash
git add src/morphos_intro.py tests/test_morphos_intro.py
git commit -m "feat: render and verify MORPHOS intro"
```
