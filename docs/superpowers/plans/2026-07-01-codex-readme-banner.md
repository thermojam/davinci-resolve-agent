# CODEX README Banner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the approved CODEX ASCII banner and assisted-by attribution to the top of README.

**Architecture:** Extend the existing README contract test first, then add one static fenced text block and one attribution line. Publish through a Pull Request because `main` is protected.

**Tech Stack:** Markdown, Python `unittest`, Git, GitHub CLI.

## Global Constraints

- Modify only `README.md`, its contract test, and these process documents.
- Preserve all existing README content below the new attribution.
- Use exact attribution text `Assisted-by: OpenAI Codex`.

---

### Task 1: Add tested CODEX attribution

**Files:**
- Modify: `README.md`
- Modify: `tests/test_davinci_console_bridge_skill.py`

**Interfaces:**
- Consumes: existing `README` path in `SkillContractTests`.
- Produces: a stable README header containing the approved banner and attribution.

- [ ] Add assertions for `Assisted-by: OpenAI Codex` and `██████╗ ██████╗ ██████╗` to `test_readme_guides_new_users_through_safe_resolve_workflow`.
- [ ] Run `python3 -m unittest tests.test_davinci_console_bridge_skill.SkillContractTests.test_readme_guides_new_users_through_safe_resolve_workflow -v` and confirm it fails because the banner is absent.
- [ ] Insert the approved fenced `text` banner and attribution immediately after the H1.
- [ ] Run `python3 -m unittest tests.test_davinci_console_bridge_skill -v` and confirm all tests pass.
- [ ] Commit the README and test changes, push the branch, and create a Pull Request to `main`.
