> 🌐 **English** · [中文](../zh/TECH-DESIGN.md)

# Chronotope — current technical design (snapshot)

A consolidated, *current-state* view of the stack as built. Vision lives in
[VISION.md](VISION.md); this is the engineering snapshot — what exists, how the
pieces fit, what is contractual, and what is still pending. Detailed specs are
cross-linked, not duplicated.

**Date:** 2026-06-28. **Milestones:** M-L3.1 (P1) ✅, M-L3.2 (P2+P3) ✅, M-L3.3
(P4+P5) ✅, M-L3.4 (P6) ◐ (eval + real-LLM drive; Thor pending), M-L3.5 (P7) ◐
(failover + voice; engines pending). Brain suite: 110 network-free tests.

---

## 1. The stack — five packages, one body metaphor

```
RGB(-D) ─► worldsense (eyes) ─► Detection[] ─┐
                                             ▼
                          tempomem (memory: fuse → persist → query)   ← the only stateful object
                                             │ serialize subgraph
                                             ▼
        mindloop (brain, S2):  route → plan → compile → POLICY → dispatch
                                             │ SubTask[] (verbs + node ids)
                                             ▼
                          bodylink (body seam): MockBody / SimDeviceAdapter / real
                                             │ (Genesis sim backend)
                                             ▼
        skillforge (research): ENPIRE self-learning loop over mem+brain+body+world
```

| Package | Role | Status |
|---|---|---|
| **tempomem** | memory core — `.smem` scene-graph, fuse-before-persist, layered query | stable core |
| **worldsense** | eyes — RGB(-D) → world-frame `Detection`s (CLIP behind `[clip]`) | stable |
| **mindloop** | brain — the S2 cognitive loop (P0–P3 done) | **active** |
| **bodylink** | body seam — fills `ExecutorAdapter`; multi-model + sim | **active** |
| **skillforge** | self-learning lab (ENPIRE walking skeleton, v0.1.0a0) | research |

Dependency direction: `worldsense → tempomem`, `mindloop → tempomem`,
`bodylink → mindloop`, `skillforge → all`. The core never imports the others — it
only ships the *protocols* they fill (`PerceptionAdapter`, `Verbalizer`;
`mindloop` ships `ExecutorAdapter`).

---

## 2. The brain pipeline (mindloop, S2)

`Brain.handle(instruction, safety_context=)` is the spine. Two perception entry
points (`observe`/`ingest`) feed memory; `ask` answers questions; `handle` is the
full task loop:

```
instruction
   │  ① IntentRouter.classify          ◀ LLM      task | question | chat
   ├─ question/chat ─► ask: retrieve subgraph → Reasoner (LLM) → cited Answer
   └─ task
        ② Planner.plan                 ◀ LLM      skill card | general LLM → Command[] (text verbs)
        ③ compile_commands             ◀ RULES    Command[] → SubTask[]: bind node ids (B9),
                                                   fill skill/pre/eff, drop verb ∉ manifest (D3)
        ④ Phylax.check                 ◀ POLICY   vet vs SafetyContext → block (stop+speak) or clear (P3)
        ⑤ ExecutorAdapter.dispatch     ◀ BODY     SubTask → StatusUpdate[] (RUNNING→terminal, echo ids B9)
   ► HandleResult(intent, answer | plan, statuses, violations, blocked)
```

**Three deterministic stages after the LLM.** ② is the only generative step; ③④⑤
are deterministic. The chain is one-directional and never falls back to a rule
*planner* (see [planning chain](../../mindloop/docs/en/devplan/specs/P1-intent-planning.md) §1a):
- **③ compile (D3 gate):** the body's `CapabilityManifest` decides what verbs may
  dispatch; object mentions bind to scene-graph node ids (B9).
- **④ policy (P3 gate):** the Phylax semantic tier blocks any plan that violates a
  declarative `Policy` — *stop + speak, no reroute, no retry*; monotonic
  (lower must-not overrides upper want-to). Opt-in.
- **⑤ dispatch:** verb-level only; the body realizes verbs below L2.

**Stages between compile and dispatch (later phases, opt-in):** an **L5 preference
overlay** (P5 — a person's prefs override card defaults, manifest-gated) sits
between ③ and ④. The dispatch step ⑤ is a **loop**, not one shot: a typed `FAILED`
feeds the **bounded replanner** (P4); a confirmed success writes its effects to a
symbolic **world-state overlay** (P2, injected into the next context so a multi-step
task stays grounded without re-perceiving); a step the world-state already satisfies
is **idempotently skipped** (P3-dyn); and **active perception** may re-look between
steps and trigger a bounded **tail re-plan** from fresh context (P4-dyn). This is
the perceive-act-update cycle —
[dynamic scene context](../../mindloop/docs/en/research/dynamic-scene-context.md).

What's implemented per phase:

| Phase | What | Spec |
|---|---|---|
| **P0** | seam contracts + value types (`execute.py`) | — |
| **P1** ✅ | intent routing + two-stage planning (LLM verbs → rule compile) | [P1](../../mindloop/docs/en/devplan/specs/P1-intent-planning.md) |
| **P2** ✅ | Episteme skill-card library (procedural knowledge as data) | [P2](../../mindloop/docs/en/devplan/specs/P2-episteme-skill-cards.md) |
| **P3** ✅ | Phylax policy tier (semantic safety gate) | [P3](../../mindloop/docs/en/devplan/specs/P3-phylax-policy.md) |
| **P4** ✅ | L4 trace + failure-driven replanning (bounded; B3 typed errors) | [P4](../../mindloop/docs/en/devplan/specs/P4-trace-replanning.md) |
| **P5** ✅ | dialogue + full S2 loop (multi-turn + L5 prefs; e2e reproduced) | [P5](../../mindloop/docs/en/devplan/specs/P5-dialogue-full-loop.md) |
| **P6** ◐ | eval harness + real Cosmos+Qwen drive validated (Thor pending HW) | [P6 §DEV-PLAN](../../mindloop/docs/en/devplan/DEV-PLAN.md) |
| **P7** ◐ | edge fallback — `FailoverVerbalizer` (P7.1) + voice seams (P7.2) done; engines/HW pending | [P7](../../mindloop/docs/en/devplan/specs/P7-edge-fallback.md) |
| **dyn-scene** ✅ | dynamic scene context — seam + world-state write-back + idempotent skip + active perception | [research](../../mindloop/docs/en/research/dynamic-scene-context.md) |

---

## 3. The body seam (bodylink) — swap the body, keep the mind

The brain plans **skill verbs** + **node ids**, never joint angles or geometry
(B8). A robot model is therefore defined by **data + a thin adapter**, and the
brain code never changes (D3). See the
[multi-model design](../../bodylink/docs/en/multi-model-adaptation-design.md).

- **Two-tier `CapabilityManifest`** — a `BodyProfile` (hardware: dof, `base_type`
  wheeled/legged/fixed) + a `VerbSpec` verb tier (what the planner may emit). Only
  the verb tier changes what the brain plans.
- **Catalog** — `load_manifest("g1d"|"h1"|"gr1"|"arm6")` (builtins span all three
  base_types) or a vendor `*.yaml`.
- **`BaseExecutorAdapter` SDK** — a device package implements only `_execute()`;
  the base handles the verb gate (D3), the RUNNING→terminal stream, and the
  node-id echo (B9). `MockBody` and `SimDeviceAdapter` are subclasses.
- **Conformance kit** — `check_executor_adapter()` proves any body honors the seam
  (manifest well-formed, terminal, B9 echo, D3 refusal, B3 typed error).
- **Physics sim** (`bodylink.sim`, `[sim]` extra) — `MockSimBackend` +
  `GenesisSimBackend` (real Genesis scene, mirrors B2R `GenesisL1`), selected via
  `make_sim_backend`. Verified end-to-end on a Linux RTX PRO 6000 host **and**
  macOS Apple Silicon: H1 runs the laundry card, every verb stepping real physics.

---

## 4. The contracts (ratified decisions)

The seam is governed by ratified decisions — the load-bearing invariants:

| Id | Contract |
|---|---|
| **D1** | the brain is **S2 only** (deliberative); reflex/control live below L2 |
| **D3** | **open-vocabulary verbs** + a two-tier `CapabilityManifest` — new body, no brain change |
| **D4** | three-tier **Phylax** guardian (semantic in brain ✅, symbolic-BT in bodylink, reflex in firmware) |
| **B3** | executor faults are **typed** (`ErrorCode` + `RecoveryHint`), never free text |
| **B8** | the brain never speaks **joint space / base-frame geometry** |
| **B9** | scene-graph **node ids cross the seam** and are echoed back — the audit chain stays closed |
| **K2** | skill cards are **flat steps + rules** (DAG reserved via `schema_version`) |

---

## 5. Models & deployment

- **Reasoner**: Cosmos-Reason2-8B (physical-AI VLM) on an RTX PRO 6000 (96 GB),
  served OpenAI-compatible; `CosmosReasonVerbalizer` (stdlib, any `/v1/chat`).
- **Planner / IntentRouter**: a strong instruction-follower (Qwen3.6, thinking
  off via `extra_body`) for clean verb sequences — the dual-model split is the
  quality sweet spot; a single Cosmos also works (with the `default_speak` floor).
- **On-body (P7 edge fallback)**: the **same Qwen-aligned split, smaller** —
  Reasoner = Cosmos-Reason2 (2B/8B), Planner = Qwen3.x-8B, plus Qwen3-ASR /
  Qwen3-TTS (small) for speech — reached via `FailoverVerbalizer` when the network
  drops (no brain change).
- **Sim**: Genesis (CPU backend) on the host and locally on macOS.
- Tests are **network-free**: `ScriptedReasoner`, hash encoders, dict skill cards,
  injected fake-genesis — no LLM or model download in any test.

---

## 6. What's done vs pending

**Done:** P0 seam · P1 plan · P2 skill cards · P3 safety gate · P4 trace + bounded
replanning · **P5 dialogue + full S2 loop (M-L3.1, M-L3.2, M-L3.3)** · P6 eval
harness + real Cosmos+Qwen drive validated · P7.1 LLM failover + P7.2 voice seams ·
**dynamic scene context (4 phases — world-state write-back, idempotent skip, active
perception)** · bodylink multi-model framework (4 builtins, SDK, conformance) ·
Genesis sim (host + mac) · the planner/reasoner LLM deployment. **110 brain tests.**

**Pending:**
- **P6 tail** — make Cosmos the standard reasoner end-to-end + the cloud→Thor
  switch (needs the host kept live / Thor hardware); ratify eval thresholds.
- **P7 tail** — P7.3 on-body engines (Qwen3-ASR/TTS + edge LLM on Jetson) + P7.4
  degradation/telemetry (needs edge hardware).
- **Body** — a true *hardware* adapter (real robot transport, not the sim); and
  deepening the coarse sim (per-robot IK / MJCF keyframes like B2R's 49-DOF G1).
- **Phylax** — the symbolic-BT (bodylink) + reflex (firmware) tiers of D4.
- **P7 edge fallback** — on-body offline AI chain: `FailoverVerbalizer`
  (remote → on-body LLM on a `QueryError`, reusing the `Verbalizer` seam) + new
  `Listener` (ASR) / `Speaker` (TTS) seams + a connectivity-aware mode arbiter.
  When the network drops, the robot still hears, plans (skill-card or on-body
  LLM), passes the local safety gate, acts, and speaks — safety and memory are
  already local, so they never go offline. Spec:
  [P7-edge-fallback](../../mindloop/docs/en/devplan/specs/P7-edge-fallback.md).
