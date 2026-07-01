---
name: davinci-console-bridge
description: Use when Codex needs to inspect, plan, create, edit, render, export, or diagnose DaVinci Resolve projects, especially Resolve Free workflows using the embedded Py3 Console and service-specific delivery requirements.
---

# DaVinci Console Bridge

## Core rule

Complete the production brief, inspect evidence, write a verifiable plan, and obtain approval before changing Resolve. Use only locally verified automation paths and current primary-source delivery requirements.

## Mandatory workflow

Ask one concise question at a time. Mark irrelevant fields as not applicable. Do not silently invent creative or technical decisions.

1. **Brief gate:** Collect:
   - Resolve version/edition, operating system, and running state;
   - absolute source paths and permission to read them;
   - video, audio, images, fonts, logos, subtitles, and other assets;
   - script, narrative, shot list, exact wording, and duration;
   - reference videos/stills and the qualities to reproduce;
   - resolution, aspect ratio, frame rate, color space, and audio rate;
   - pacing, transitions, titles, graphics, color, sound, and music rights;
   - destination service and exact placement;
   - orientation and delivery requirements;
   - permission to create/replace a named project and render.
2. **Evidence gate:** Inspect sources read-only. Run `scripts/check_environment.py`. Confirm tool and API paths.
3. **Best-practice gate:** Read only the relevant sections of `references/best-practices.md` and `references/console-api.md`.
4. **Delivery-profile gate:** Read `references/delivery-profiles.md`. Verify current official requirements for the exact service and placement. Record source URLs and verification date in a task-local JSON profile.
5. **Geometry gate:** Confirm display orientation, source interpretation, timeline dimensions, aspect ratio, safe areas, and render dimensions. Use separate timelines/renders for landscape, portrait, or square variants; reframe intentionally.
6. **Plan gate:** Present the edit and implementation plan with timeline structure, output paths, delivery profile, success criteria, and retry/rollback behavior.
7. **Approval gate:** Obtain explicit approval. Do not create files or change Resolve before this gate passes.
8. **Execution gate:** Start from `assets/resolve_task_template.py`. Generate the pasteable command with `scripts/make_console_command.py`. Execute from `Workspace > Console > Py3`.
9. **Verification gate:** Inspect project/timeline state, probe every render, and run `scripts/validate_delivery.py` against the approved profile before claiming completion.

## Verified Console connection

Resolve Free on the verified Mac uses the embedded Py3 Console. Inject its ready `resolve` object into the target script:

```python
p = r"/absolute/path/to/task.py"
g = {"__file__": p, "__name__": "resolve_console_task", "resolve": resolve}
exec(open(p, encoding="utf-8").read(), g)
g["main"]()
```

Target scripts must prefer `globals().get("resolve")`. Treat external `DaVinciResolveScript.scriptapp("Resolve")` as a fallback only after independently verifying external scripting for that Resolve edition.

## Project safety

- Treat existing projects as immutable without explicit authorization.
- Never delete or replace a project implicitly.
- Reuse a project only after verifying exact name and expected recovery state.
- Query `GetSetting()` and installed API docs before using uncertain settings.
- Stop on ambiguous retry state rather than duplicating timelines or media.

## Quick reference

| Need | Resource |
|---|---|
| Check local prerequisites | `scripts/check_environment.py` |
| Create Console command | `scripts/make_console_command.py` |
| Validate orientation/export | `scripts/validate_delivery.py` |
| Start task automation | `assets/resolve_task_template.py` |
| Debug Console/API | `references/console-api.md` |
| Edit/Color/Fairlight/Deliver guidance | `references/best-practices.md` |
| Build platform profile | `references/delivery-profiles.md` |

## Common mistakes

- Module import success does not prove external Resolve connection works.
- Embedded Python may not inherit shell `PATH`; use verified absolute tool paths.
- A service name alone is insufficient; ask for the exact placement.
- Do not rotate or stretch a horizontal master into a vertical deliverable.
- Do not hardcode platform specifications as timeless facts.
