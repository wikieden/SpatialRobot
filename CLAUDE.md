# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`SpatialRobot` is the **workspace root** (engineering dir name only) for **Chronotope**,
an embodied-brain stack split across **independently published, independently
git-versioned** Python packages. The product/brand name is **Chronotope**; `SpatialRobot`
is just this workspace directory (repos not yet renamed). The split mirrors a body: a
numpy-only memory core, optional GPU-heavy eyes, an LLM brain that drives the loop, a
body/executor seam, and a self-learning lab on top. The root itself is **not a git repo
and not a package** — it is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
that gives all members a single shared environment. There are **six workspace members**:
the original triad (`tempomem`/`worldsense`/`mindloop`) plus `bodylink` (executor seam),
`voicelink` (voice seam — ASR/TTS, P7), and `skillforge` (research track, working name,
`v0.1.0a0` walking skeleton). **All six are their own git repos** (root submodules,
private); the root repo holds only the workspace wiring (`pyproject.toml`,
`uv.lock`, `.gitmodules`) + cross-cutting `docs/`.

```
RGB(-D) ─► worldsense (eyes) ─► Detections
                                              │
                                              ▼
                              tempomem (memory: fuse → persist → query)
                                              │ serialize
                                              ▼
              mindloop  Brain.ask ─► Reasoner (LLM) ─► Answer(text, cited node ids)
                                              │ SubTask (ExecutorAdapter)
                                              ▼
                              bodylink (body seam: MockBody / real device pkg)

  skillforge (research track): drives mem+brain+body+world in an ENPIRE self-learning loop
```

| Member dir | Package | Role | Heavy deps |
|---|---|---|---|
| `tempomem/` | `tempomem` | Memory core — `.smem` SQLite scene-graph, fusion arbiter, query, serialize. The hippocampus. | none (numpy-only) |
| `worldsense/` | `worldsense` | Eyes — RGB(-D) → world-frame `Detection`s; camera→world geometry lift, CLIP encoders. | behind `[clip]` (torch) |
| `mindloop/` | `mindloop` | Brain — `Brain` cognitive loop + `Reasoner` + `CosmosReasonVerbalizer`; ships the `ExecutorAdapter` protocol. | none in core; LLM is remote/self-hosted |
| `bodylink/` | `bodylink` | Body seam — fills `mindloop`'s `ExecutorAdapter`: `MockBody` (no-hardware ref) + `CapabilityManifest` (`g1d_manifest`). "Swap the body, keep the mind." | none (stdlib; depends on `mindloop`) |
| `voicelink/` | `voicelink` | Voice seam — fills `mindloop`'s `Listener`/`Speaker` (ASR ears + TTS mouth): `EndpointListener`/`EndpointSpeaker` over an OpenAI-compatible audio endpoint (Qwen3-ASR/TTS). The offline AI chain (P7). | none (stdlib; depends on `mindloop`) |
| `skillforge/` | `skillforge` | Self-learning lab (research track, working name) — ENPIRE loop (Environment/Policy/Rollout/Evolution) over mem+brain+body+world. The **only** member that imports all others. | none (`v0.1.0a0` walking skeleton, network-free) |

**Dependency direction:** `worldsense → core`, `mindloop → core` (+ optional
`mindloop[perception]`), `bodylink → mindloop`, `skillforge → tempomem + mindloop +
bodylink`. The core (`tempomem`) never imports the others; it only ships the
`PerceptionAdapter` and `Verbalizer` *protocols* they fill (`mindloop` ships
`ExecutorAdapter`). Keep it that way — adding a torch/LLM import to `tempomem/` breaks the
numpy-only contract.

## Environment & commands

One env for the whole workspace, driven from this root via uv (Python pinned to
3.12 in `.python-version`; packages support ≥ 3.10):

```bash
uv sync                       # create root .venv, install all 5 members editable + shared dev tools
uv sync --extra clip          # add the GPU/CLIP stack (torch, open-clip, pillow)
```

`[tool.uv.sources]` here maps `tempomem` and `worldsense` to the
local tree, so editing the core is immediately visible to brain/perception with
no reinstall. Run tooling through `uv run` so it uses the shared env:

```bash
# Tests — scope to a member by passing its tests dir
uv run pytest tempomem/tests
uv run pytest mindloop/tests
uv run pytest worldsense/tests
uv run pytest tempomem/tests/unit/test_fusion.py::test_dedup_same_object_merges  # single test
uv run pytest --cov=tempomem/src --cov-report=term-missing            # coverage (gate: ≥75% on core)

# Lint / format / types
uv run ruff check .
uv run ruff format .
uv run pyright tempomem/src/tempomem      # core is the only pyright target (strict-ish)

# CLI (core only) — also runnable as `uv run tempomem ...`
uv run tempomem viz store.smem -o scene.html
```

Each member also defines `[tool.pytest.ini_options]` with `pythonpath` so
`cd <member> && pytest` works standalone, but prefer `uv run` from root to keep
one resolved environment. Tests are **network-free**: brain tests use
`ScriptedReasoner`, perception/semantic tests use hash encoders — never reach for
a real LLM or model download in a test.

## Architecture notes that span files

**`tempomem` (the core) is the only stateful object.** `SpatialMemory` in
`tempomem/src/tempomem/__init__.py` is the entire public surface; everything
else (`store`, `fusion`, `query`, `serialize`, `relations`, `persist`) is a
stateless module it composes. `__all__` is the API contract — anything not
listed is private.

**Fuse-before-persist is an invariant, not a detail.** `add_detections()` /
`add_frame()` only *stage* observations into `self._pending`; nothing is fused
until `commit()`. Every maintenance/structural mutator (`decay`, `forget`,
`resplit`, `consolidate`, `relate`, `update`, `define_region`) first calls
`_flush_pending()` because the sqlite connection runs in implicit-transaction
mode — committing with unfused rows would persist orphan observations. `commit()`
is the *sole* drainer of `_pending`. When adding a new mutator, call
`_flush_pending()` first (see the long docstring on `_flush_pending`).

**Query routing is layered, not a single index.** `query()` tries relational
phrase matching first ("what's on the table" → edge traversal), then intent
detection → semantic-vec (needs an `Encoder`) or keyword fallback. Semantic and
`answer()` are **BYO**: no encoder/verbalizer configured ⇒ keyword/raise, not a
silent default. Heavy backends (`sqlite-vec` ANN, OpenCLIP) live behind extras
with linear/keyword fallbacks so the core stays installable with numpy alone.

**The brain is a thin orchestrator over protocols.** `Brain`
(`mindloop/src/mindloop/`) wires memory + a `Reasoner`;
`VerbalizerReasoner` adapts any `Verbalizer`, and `CosmosReasonVerbalizer` is
stdlib-only and speaks to **any OpenAI-compatible `/v1/chat/completions`**. To
self-host the reasoner, point `base_url` at a local vLLM/NIM server — no code
change. The user runs Cosmos-Reason2-8B on an **RTX PRO 6000 (96 GB)** workstation;
deployment specifics (variants, VRAM, serve commands) are in
[mindloop/docs/en/local-serving.md](mindloop/docs/en/local-serving.md).

## Conventions (from tempomem/spec/ENGINEERING.md — normative for all members)

- **Value types are `@dataclass(frozen=True, slots=True)`.** No global mutable state.
- **`logging.getLogger("tempomem.<module>")`, never `print()`.** No `pickle`,
  no pre-3.10 typing syntax.
- **Returns over raises for expected absence** (`Optional`, `[]`); raise only for
  programmer error or IO failure. Error types live in `_errors.py`.
- **Public methods document units + reference frame** in the docstring (meters,
  world frame) — repeat even when it feels redundant; that's where the bugs are.
- **Comments explain *why* (with a spec section), never *what*.**
- **ruff** line-length 100; core selects `E,F,I,B,UP,SIM,PERF,RUF`. **Conventional
  Commits**, trunk-based, squash-merge, one logical change per PR. Update
  `CHANGELOG.md` in the same PR as the change (core keeps keep-a-changelog).

## Where to read first

> **Docs are bilingual.** Every narrative doc lives in both `docs/en/` (English,
> canonical) and `docs/zh/` (中文). READMEs use a suffix instead: `README.md`
> (English) + `README.zh.md`. `spec/*.md` and `CHANGELOG.md` stay English-only.
> Paths below point at the English canonical.

- System vision (the 3-package whole): `docs/en/VISION.md`
- Product/design (read in order): `tempomem/docs/en/00-VISION.md` → `01-POSITIONING.md`
  → `02-ARCHITECTURE.md` → `03-ROADMAP.md` → `04-MVP-SCOPE.md`
- Normative specs: `tempomem/spec/{API,SCHEMA,FUSION-ARBITER,QUERY-ROUTER,ENGINEERING}.md`
- Full system design (perception + memory + brain): `mindloop/docs/en/cosmos3-tempomem-llm-brain.md`
- Runnable, no GPU: `tempomem/examples/01_quickstart.py`, `mindloop/examples/`
