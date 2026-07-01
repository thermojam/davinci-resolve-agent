# Verified Resolve Console and API Notes

Use this reference when connecting to Resolve, retrying a partial task, or diagnosing API failures.

## Known-good connection

DaVinci Resolve Free 21 on the verified Mac exposes both `bmd` and a ready `resolve` object inside `Workspace > Console > Py3`. Pass `resolve` into an isolated target-script namespace and make the target prefer `globals().get("resolve")`.

Do not infer external scripting support from a successful module import. On the verified Free installation, external `scriptapp("Resolve")` returned `None`; the embedded object worked.

## Installed primary references

- API: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt`
- Examples: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Examples`
- Module: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/DaVinciResolveScript.py`

Read the installed README and matching examples completely before using an unfamiliar API call.

## Verified failure modes

| Error or symptom | Root cause | Working response |
|---|---|---|
| `No such file or directory: 'ffprobe'` | Embedded Python did not inherit the shell `PATH`. | Resolve with `shutil.which`, `/opt/homebrew/bin`, then `/usr/local/bin`. |
| `No module named 'DaVinciResolveScript'` | The module directory was not on embedded Python's import path. | Prefer injected `resolve`; only load the absolute module when an external workflow is independently supported. |
| `DaVinci Resolve is not running or external scripting is disabled` | Code ignored the injected `resolve` object and called external `scriptapp`. | Return `globals().get("resolve")` first. |
| A setting call returns `False` | The key/value is unavailable, read-only, or invalid in this Resolve version. | Query `GetSetting()` and the installed API docs; avoid undocumented project settings. |
| Project title is visible but project list is empty | A newly created unsaved current project may not yet appear in the folder list. | Inspect the unsaved current project first, verify exact name and recovery state, then decide whether reuse is safe. |

## Retry safety

- Never delete or replace a project implicitly.
- Before reuse, verify project name, timeline count/names, media state, and expected partial step.
- Stop when retry state is ambiguous. Duplicate timelines and repeated media imports are not an acceptable recovery strategy.
- Save at explicit checkpoints after project settings, timeline construction, and final render configuration when the task plan calls for them.
