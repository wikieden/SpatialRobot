> 🌐 **English** · [中文](../zh/INTEGRATION-E2E.md)

# Production end-to-end integration — plan

**Status:** planning + building (2026-06-29). The L3 brain software is feature-complete
(P0–P5 ✅, P6 real-LLM validated); this is the capstone that proves the **whole stack
works as one system** under production requirements. Companion: [TECH-DESIGN.md](TECH-DESIGN.md).

## 1. Goal

One runnable harness drives the **full stack** through household scenarios:

```
real LLM brain (Cosmos-Reason2 + Qwen3.6, via FailoverVerbalizer)
   → SceneContextProvider + WorldState  (dynamic context)
   → SkillCardPlanner / LLM planner → compile (D3) → Phylax (P3) → dispatch
   → SimDeviceAdapter + GenesisSimBackend  (physics body)   [or MockBody]
   → bounded Replanner (P4) + TraceStore (L4)   → Conversation (P5)   → VoiceLoop (P7)
```

…and **measures** it: accuracy, success rate, safety compliance, latency — with the
full trace captured for audit.

## 2. The six production requirements → mechanisms

The owner's bar: **buildable · reproducible · traceable · safe-and-reliable · high
accuracy · high success rate.** Each maps to concrete machinery already in the stack:

| Requirement | Mechanism (what makes it true) |
|---|---|
| **可做 buildable / runnable** | one entrypoint `ScenarioRunner.run(scenarios)`; a runnable example; CI-wired |
| **可复现 reproducible** | network-free baseline (ScriptedReasoner) is fully deterministic (seeded RNG, scripted plans); the real-LLM pass pins models + records config; the report is a stable artifact |
| **可追溯 traceable** | `TraceStore` logs every dispatch + failure citing scene **node ids** (B9); answers cite node ids; the report embeds the per-scenario trace + the config that produced it |
| **安全可靠 safe & reliable** | `Phylax` gate on every plan (P3); `FailoverVerbalizer` (remote→on-body, never crash on a network drop); bounded `Replanner` (P4, no infinite loop); typed `ErrorCode`/`RecoveryHint` (B3); a bad turn degrades, never aborts the harness |
| **准确率 accuracy** | `run_eval` metrics — planning accuracy, citation compliance, policy compliance — scored vs `EvalThresholds` (planning ≥0.9, policy =1.0) |
| **成功率 success rate** | aggregate task-terminal-SUCCESS across scenarios (incl. recovered-via-replan), reported as a rate vs a threshold |

## 3. Harness architecture (`skillforge.scenario`)

skillforge is the member that imports all others — the lab that drives
mem+brain+body+world. The integration harness lives there:

- **`Scenario`** — a named multi-turn script: a scene (detections), turns
  (instruction + person + role + expectations), and the wiring knobs (which body,
  which reasoner). Reuses `mindloop.EvalCase` expectations.
- **`ScenarioRunner`** — builds a **production-wired `Brain`** (all faculties:
  context provider, world-state, SkillCardPlanner+LLM fallback, Phylax, Replanner,
  TraceStore, preferences) over a body (`MockBody` or `SimDeviceAdapter`+Genesis),
  runs each scenario turn via `brain.converse`, and collects results + latency.
- **`IntegrationReport`** — per-scenario pass/fail + the four eval metrics +
  success rate + latency percentiles + the embedded trace + the run config (repro).
  `meets(thresholds)` gives one production go/no-go.

**Two run modes, same harness:**
1. **baseline (network-free, CI):** ScriptedReasoner/Planner + MockBody — deterministic,
   reproducible, fast; proves the *loop + safety + replan + trace* logic.
2. **real (validation):** `FailoverVerbalizer`→host Cosmos+Qwen + Genesis sim — proves
   *accuracy + success rate* against the production models. Run on the GPU host.

## 4. Scenario set (household, B2R-aligned)

A small, growing suite exercising every faculty:

- **question** — "what is in the kitchen?" → cited answer.
- **task / success** — "bring me the bottle" → navigate+grasp → SUCCESS, traced.
- **task / replan-recover** — a grasp that fails once → bounded replan → SUCCESS.
- **task / safety-block** — a child asks an adult-only op → Phylax blocks, nothing dispatched.
- **multi-turn dialogue** — a follow-up resolving against a prior turn.
- **preference** — a person's preference overrides a card default.
- **skill card** — laundry/cooking card → multi-step plan → SUCCESS.

## 5. Reproducibility & traceability artifacts

- The runner takes a seed + a config object; the report records both.
- Baseline mode has zero network + zero model downloads (CLAUDE.md test rule).
- Every dispatched subtask is in the `TraceStore`, queryable by node id; the report
  serializes the trace so a run is auditable after the fact.

## 6. Phasing

> Live status across all phases: [DEV-STATUS.md](DEV-STATUS.md).

1a. **Harness + baseline** (network-free, deterministic): `Scenario`,
   `ScenarioRunner`, `IntegrationReport`, the 4-scenario household suite, tests.
   CI go/no-go. **✅ done — GO, all metrics 100%.**
1b. **Family-suite extension**: the six TASK-FAMILIES suites (tour/chores/find/
   cleaner/receptionist/execution-dynamics) + new metrics. **▢ in progress**
   (real assertions need TASK-FAMILIES §8 steps 1+3+3b).
2. **Real-LLM validation pass**: swap in `FailoverVerbalizer`→host; run on the GPU
   host; capture accuracy + success-rate + latency; archive the report.
3. **Sim body**: run the suite through `SimDeviceAdapter`+Genesis (physics stepping)
   in addition to MockBody.
4. **Voice**: optionally drive turns through `VoiceLoop` (voicelink fills).

---

## Appendix — deferred software tracks (light plan)

> **Scope expansion (planned).** Three new task families (tour-guide · household chores ·
> find-lost-object), execution dynamics (barge-in · failure-replan · ask-human), and the
> data/training closed-loop are planned in [TASK-FAMILIES.md](TASK-FAMILIES.md); all flow
> diagrams (component · spine · dynamics · families · data-loop) are in [FLOWS.md](FLOWS.md).
> They extend this capstone's scenario set + metrics — same six-criteria go/no-go gate.

**Track 2 — finish the remaining brain software**
- *Dynamic scene phase 4 (active perception):* on a stale focus or reasoner request,
  re-`observe` between steps → fuse → re-query fresh context → re-plan the tail. Hooks
  exist (`_dispatch_plan`, version bump). Network-free testable with a scripted perceiver.
- *P7.4 (degradation + telemetry):* offline mode prefers skill-cards, tightens safety
  to conservative, records which mode (online/offline) served each turn; honest
  "I'm offline" UX. Builds on `FailoverVerbalizer.mode`.

**Track 3 — skillforge self-learning deepening**
- The ENPIRE loop (Environment/Policy/Rollout/Evolution) currently a walking skeleton.
  Deepen: richer reward shaping, an LLM `PolicyAuthor` (vs ScriptedAuthor), skill
  crystallization back into Episteme cards (close the learn→reuse loop). Research track.

Both are scoped + parked; the integration capstone (above) is the focus.
