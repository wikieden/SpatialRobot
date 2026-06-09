> 🌐 **English** · [中文](README.zh.md)

# SpatialRobot

Workspace umbrella for the **embodied-brain** stack — a memory core, optional
eyes, and an LLM brain, split across three independently published,
independently versioned repos and bundled here as git submodules + one
[uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/).

> This repo holds **no source of its own** — only the submodule pointers and the
> shared dev config (uv workspace, lockfile, Python pin, `CLAUDE.md`, this
> README). Each package develops in isolation in its own repo; the workspace
> just gives them one resolved environment.

```
RGB(-D) ─► spatialmem-perception (eyes) ─► Detections
                                              │
                                              ▼
                              spatialmem (memory: fuse → persist → query)
                                              │ serialize
                                              ▼
              spatialmem-brain  Brain.ask ─► Reasoner (LLM) ─► Answer(text, cited node ids)
```

| Submodule | Package | Role | Repo |
|---|---|---|---|
| `SpatialMem/` | `spatialmem` | Memory core — `.smem` SQLite scene-graph, fusion, query (numpy-only). | [wikieden/spatialmem](https://github.com/wikieden/spatialmem) |
| `spatialmem-perception/` | `spatialmem-perception` | Eyes — RGB(-D) → world-frame `Detection`s (CLIP behind `[clip]`). | [wikieden/spatialmem-perception](https://github.com/wikieden/spatialmem-perception) |
| `spatialmem-brain/` | `spatialmem-brain` | Brain — `Brain` loop + `Reasoner` + `CosmosReasonVerbalizer`. | [wikieden/spatialmem-brain](https://github.com/wikieden/spatialmem-brain) |

Dependency direction: `perception → core`, `brain → core` (+ optional
`brain[perception]`). The core never imports the other two.

## Clone

```bash
git clone --recurse-submodules https://github.com/wikieden/SpatialRobot.git
cd SpatialRobot
# forgot --recurse-submodules?
git submodule update --init --recursive
```

## Setup

One env for all three, from this root (Python pinned to 3.12 in `.python-version`):

```bash
uv sync                 # .venv at root, all 3 members editable + shared dev tools
uv sync --extra clip    # + the GPU/CLIP stack (torch, open-clip, pillow)
```

`[tool.uv.sources]` maps `spatialmem` / `spatialmem-perception` to the local
tree — edit the core, brain/perception see it immediately, no reinstall.

## Common commands

A `Makefile` wraps the usual `uv run` invocations:

```bash
make sync            # uv sync
make test            # pytest across all 3 members
make test-core       # one member (also: test-brain, test-perception)
make lint            # ruff check .
make fmt             # ruff format .
make types           # pyright on all 3 src trees
make bump            # pull each submodule's tracked branch to latest
```

Run anything directly too, e.g. `uv run pytest SpatialMem/tests` or
`uv run spatialmem viz store.smem -o scene.html`.

## Daily submodule flow

1. Work inside a member dir (`SpatialMem/`, …) — commit + push in that child repo.
2. Back at the root, record the new pointer:
   ```bash
   git submodule update --remote   # or just `make bump`
   git add <member> && git commit -m "chore: bump <member> → <sha>"
   git push
   ```

Tracked branches: `SpatialMem` → `feat/cosmos-integration`, the other two → `main`.

## More

- Workspace guide for agents / contributors: [CLAUDE.md](CLAUDE.md)
- Per-package docs: each submodule's own `README.md` + `docs/`.
