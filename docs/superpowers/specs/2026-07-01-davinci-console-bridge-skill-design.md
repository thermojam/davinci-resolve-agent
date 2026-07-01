# DaVinci Console Bridge Skill Design

## Goal

Create a personal Codex skill named `davinci-console-bridge` for repeatable work with DaVinci Resolve on this Mac. The skill must use only locally verified automation paths and must not start editing before collecting the production brief and presenting an implementation plan.

## Installation

Install the discoverable skill at `~/.codex/skills/davinci-console-bridge`.

The skill contains:

- `SKILL.md` with the mandatory workflow and decision gates;
- `agents/openai.yaml` with discovery metadata;
- `scripts/check_environment.py` for read-only environment and target-script checks;
- `scripts/make_console_command.py` for generating the exact Py3 Console command;
- `scripts/validate_delivery.py` for comparing a rendered file with the approved delivery profile;
- `assets/resolve_task_template.py` as a self-contained starting point for new Resolve tasks;
- `references/best-practices.md` for official Blackmagic training and delivery guidance;
- `references/delivery-profiles.md` for selecting and documenting service-specific requirements;
- `references/console-api.md` for the locally verified Resolve Free scripting constraints and error diagnostics.

## Trigger and intake

Use the skill for requests to inspect, create, edit, render, export, or diagnose a DaVinci Resolve project.

On every new production task, ask one concise question at a time until the applicable fields are known:

1. Resolve version, Free or Studio, operating system, and whether Resolve is running.
2. Absolute source paths and permission to read them.
3. Inventory of video, audio, images, fonts, logos, subtitles, and other assets.
4. Script, narrative structure, shot list, required wording, and duration.
5. Reference videos or stills and the exact qualities to reproduce without copying protected material.
6. Timeline requirements: resolution, aspect ratio, frame rate, color space, and audio sample rate.
7. Editing requirements: pacing, transitions, titles, graphics, color, sound design, and music rights.
8. Destination service and placement: for example YouTube video or Shorts, Instagram Reel, Story or feed, TikTok, VK Video or Clips, Telegram, website, broadcast, or a custom master.
9. Delivery requirements: display orientation, aspect ratio, resolution, duration limits, safe areas, container, codecs, frame rate, bitrate or quality target, audio layout, maximum file size, file name, project archive, and deadlines.
10. Whether Codex may create or replace a project with the requested name and start rendering.

Mark irrelevant fields explicitly as not applicable. Do not silently invent missing creative or technical decisions.

## Workflow gates

1. **Brief gate:** Do not create files or change Resolve until the intake is complete.
2. **Evidence gate:** Inspect sources with read-only tools and verify Resolve/API/tool availability.
3. **Best-practice gate:** Select only the relevant official Blackmagic guidance for Edit, Color, Fairlight, Fusion, or Deliver.
4. **Delivery-profile gate:** Verify the current official requirements for the selected service and placement. Record the source URL and verification date. If the service does not publish a required value, label the chosen value as a production decision rather than an official requirement.
5. **Geometry gate:** Confirm that source interpretation, timeline orientation, aspect ratio, resolution, safe areas, and render dimensions match the approved delivery profile.
6. **Plan gate:** Write a concrete edit and implementation plan with success criteria, output paths, delivery profile, and rollback behavior.
7. **Approval gate:** Obtain user approval before project mutation or rendering.
8. **Execution gate:** Generate a task script and run it from Resolve's embedded Py3 Console.
9. **Verification gate:** Verify the project/timeline and probe rendered media against the delivery profile before claiming completion.

## Verified connection architecture

DaVinci Resolve Free on this Mac is controlled from `Workspace > Console > Py3`. The target script receives the Console's already-created `resolve` object:

```python
p = r"/absolute/path/to/task.py"
g = {"__file__": p, "__name__": "resolve_console_task", "resolve": resolve}
exec(open(p, encoding="utf-8").read(), g)
g["main"]()
```

The target script must prefer `globals().get("resolve")`. External `DaVinciResolveScript.scriptapp("Resolve")` is only a fallback for environments where external scripting is independently verified. The skill must never describe external scripting as working in Resolve Free merely because the module imports.

Embedded Python may not inherit the user's shell `PATH`. Resolve `ffmpeg` and `ffprobe` through `shutil.which`, `/opt/homebrew/bin`, then `/usr/local/bin`.

## Project safety

- Treat existing user projects as immutable unless the user explicitly authorizes changes.
- Reuse an existing project only when its exact name matches and the expected recovery state is verified.
- Never delete or replace a project implicitly.
- Avoid undocumented project settings. Query `GetSetting()` and use installed API documentation when a setting is uncertain.
- Make task scripts idempotent where practical, and stop rather than duplicate timelines or media on an ambiguous retry.

## Best-practice references

Prefer primary sources:

- the installed API reference at `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt`;
- the installed Blackmagic scripting examples;
- Blackmagic Design's current certified training page and current Beginner, Editor, Colorist, Fairlight, and Visual Effects guides.

The reference must translate these sources into a short task checklist: organize media before editing, lock timeline specifications before import, preserve source frame-rate intent, use restrained transitions, manage color consistently, preserve dialogue headroom, verify legal music usage, and validate the final deliverable with media probing.

## Service-specific delivery profiles

Do not hardcode social-platform specifications as timeless facts. Requirements and accepted formats can change.

For each task:

1. Identify both the service and exact placement; a service can support several incompatible orientations and durations.
2. Prefer the service's current official publishing, advertising, or creator documentation. Use reputable secondary references only when the official source omits the required parameter, and label that distinction.
3. Save a small task-local JSON profile containing the verification date, source URLs, orientation (`landscape`, `portrait`, or `square`), aspect ratio, dimensions, frame rate policy, duration range, video and audio codecs, audio channels and sample rate, bitrate or quality policy, and file-size limit when applicable.
4. Use the same profile to configure the Resolve timeline/render and to validate the exported file.
5. Fail validation on wrong width, height, orientation, aspect ratio, frame rate, duration, codecs, audio layout, or file size. Report unspecified fields without inventing an official limit.

When a horizontal master must produce vertical or square versions, create separate timelines or renders. Do not rotate a landscape edit or stretch the frame. Reframe shots intentionally and verify title/action safe areas for each placement.

## Validation

Validation is read-only with respect to Resolve projects:

- run `quick_validate.py` on the skill folder;
- compile all Python files;
- unit-test environment detection and Console-command generation using temporary files;
- execute the generated command against a fake `resolve` object and a temporary target script;
- unit-test landscape, portrait, and square delivery profiles, including mismatched dimensions and aspect ratios;
- run `validate_delivery.py` against generated probe fixtures and one local test render when available;
- confirm that the reference contains only official URLs and locally observed behavior.

Live project creation and rendering remain an explicit user-approved production action, not part of skill installation tests.
