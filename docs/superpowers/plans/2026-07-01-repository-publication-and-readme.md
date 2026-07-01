# Repository Publication and README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the complete DaVinci skill in `main`, document novice usage in Russian, and protect `main` on GitHub.

**Architecture:** Extend the existing feature branch and PR rather than duplicating files. Validate README requirements with the existing unittest suite, merge the verified PR, then apply branch protection after the repository becomes public.

**Tech Stack:** Markdown, Python `unittest`, Git, GitHub CLI and REST API.

## Global Constraints

- Keep the repository private until the tracked-file secret scan passes.
- Never add local credentials or DaVinci source media.
- Require Pull Requests on `main`; disallow force-push and deletion.
- Do not require approvals or status checks until collaborators or CI exist.

---

### Task 1: Git identity and publication safety

**Files:**
- Modify outside repository: `~/.gitconfig`
- Read only: `~/.git-credentials-thermojam`

- [ ] Configure `credential.helper` as `store --file=/Users/nikitamensky/.git-credentials-thermojam` and verify the active GitHub account is `thermojam`.
- [ ] Scan tracked filenames and content for environment files, private keys, and common token prefixes without printing credential values.
- [ ] Change `thermojam/davinci-resolve-agent` visibility to public only after the scan passes.

### Task 2: Beginner README with a regression test

**Files:**
- Create: `README.md`
- Modify: `tests/test_davinci_console_bridge_skill.py`

- [ ] Add a failing unittest that requires `README.md` to contain `$davinci-console-bridge`, `Workspace > Console > Py3`, installation guidance, the approval gate, orientation/export validation, and troubleshooting.
- [ ] Run `python3 -m unittest tests.test_davinci_console_bridge_skill -v` and confirm failure because README is absent.
- [ ] Write the minimal Russian README covering installation, invocation, expected workflow, console execution, delivery validation, safety, troubleshooting, repository structure, and tests.
- [ ] Re-run the full suite and confirm all tests pass.
- [ ] Commit the README and its regression test.

### Task 3: Publish and merge

**Files:**
- No additional repository files.

- [ ] Push `codex/davinci-console-bridge-skill` and verify PR №1 includes README and the full `skills/davinci-console-bridge` tree.
- [ ] Mark PR №1 ready and merge it into `main` using a merge commit.
- [ ] Fetch `origin/main` and verify README, skill rules, scripts, assets, references, and tests are present.

### Task 4: Protect main and verify final state

**Files:**
- No repository file changes.

- [ ] Apply GitHub branch protection requiring Pull Requests and disabling force-push/deletion, including for administrators.
- [ ] Read protection through the GitHub API and verify the required settings.
- [ ] Run the full unittest suite from the merged `main` state.
