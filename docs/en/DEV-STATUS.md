# DEV-STATUS — consolidated development plan (routing page)

> **Consolidated from** [TASK-FAMILIES.md](TASK-FAMILIES.md) §8 × [INTEGRATION-E2E.md](INTEGRATION-E2E.md) §6
> × [mindloop DEV-PLAN](../../mindloop/docs/en/devplan/DEV-PLAN.md). Those remain the single
> sources of truth for their areas; this page is the routing/status view. Updated **2026-07-02**.

## 1. Members × status

| Member | Done | In progress | Next |
|---|---|---|---|
| **tempomem** | core (fuse/persist/query/serialize), regions, decay, viz; **semantic Tier-1 landed** (edges/properties/events, migration 002); **`last_seen` landed** (step 2 ✅) | — | dynamic-scene P4 feeds (deferred) |
| **worldsense** | RGB(-D)→world Detections, CLIP behind extra | — | dynamic-scene P4 live perception (deferred) |
| **mindloop** | P0–P5 ✅; P6 ◐ (eval + real-LLM validated; Thor pending HW); P7 ◐ (7.1 failover + 7.2 voice seams ✅); dynamic-scene 1–4 ✅; **TempoMem rename landed**; **step-1 `_VERB_TABLE` + place@location landed** | — | steps 3 (Phylax ext), 3b (execution dynamics) |
| **bodylink** | D3 manifest framework, MockBody, Genesis sim, conformance kit, 4 builtin bodies; **step-1 verbs landed** (13 common + arm subset) | — | D-P skill scorecard (with step 6) |
| **voicelink** | EndpointListener/Speaker (Qwen3-ASR/TTS) | — | step 7: real voice barge-in (streaming ASR+VAD, deferred) |
| **skillforge** | ENPIRE skeleton, 4-scenario baseline harness GO ✅, **evolve acceptance gate landed** (held-out strict improvement) | step 4 partial (scenario structure) | step 4 full: 6 family suites + new metrics + regions |

## 2. Unified execution order (dependency chain)

> **PLANNING FROZEN (2026-07-02)** — 17 D-decisions is saturation. New design questions
> are decided at build time (one-line log here); only safety-critical items reopen
> TASK-FAMILIES.

```
T1 ──────────────────────────────────────────────────────────── mechanical, low-risk
  0 ✅ land WIP (TempoMem rename + semantic layer + gate)      [done 2026-07-02]
  1 ✅ verbs       done 2026-07-02 — 13 verbs (manifest+arm subset) · _VERB_TABLE · place@location eff
  2 ✅ memory      done 2026-07-02 — Tier-1 verified · last_seen landed (+5 tests) ·
                   current_occupants = D-B composition (no method needed)
T2 ──────────────────────────────────────────────────────────── highest-risk batch
  3 ▢  safety      Phylax: D-A robot_service · D1 (verb,param) gating · Q6 region defaults · D-K menu.py
  3b ▢ dynamics    InterruptSource · BargeClassifier (D2) · Clarifier + ASK_HUMAN (D3) · ask budget
                   ⚠ refactors Brain._dispatch_plan (109 tests on it): TDD-first,
                   own commits, never mixed with step 3
T3 ──────────────────────────────────────────────────────────── closure batch
  4a ◐ harness     Scenario.regions · EvalReport/Thresholds fields + required_metrics (D-F)
                   · L1 invariants in ScenarioRunner (D-N) · 6 suites
                   → baseline go/no-go vs §7e thresholds       [real assertions need 1+3+3b]
  4b ▢ harness     load_role + double-key grant (D-O) · templates.py + 8-property vocab (D-Q)
T4 ──────────────────────────────────────────────────────────── validation batch
  5 ▢  real LLM    host 192.168.31.89, temp=0 + fixed seed     [NEEDS GPU GREENLIGHT]
      ∥ E2E phase 3: sim body (Genesis) pass                   [autonomous]
──────────────────────────────────────────────────────────────
  6 ◐  data loop   trace→dataset · LLM PolicyAuthor · Episteme crystallization · promote gate
                   (gate.py landed early as the acceptance-gate piece)
  7 ▢  deferred    voice tour / real voice barge-in (P7.3–7.4) · active perception (dyn-scene P4)
```

T1–T3 are autonomous + network-free; each tranche ends tests-green + committed.
Step 5 alone needs the host.

## 3. Review findings (2026-07-02 consolidation pass)

1. **Execution order deviated from §8 numbering** (step 2 started before 1) — harmless
   (1/2/3 are independent), but step 4's suites can only be shells until 1+3+3b land.
2. **The rename was a cross-repo coordinated change** — `SpatialMemory → TempoMem` hard
   cut (no alias). Landed across all 6 members + root docs in one pass; sweep verified
   (`grep SpatialMemory` → 0 code refs).
3. **skillforge `gate.py` belongs to step 6**, not step 4 — it is the SkillOpt-borrowed
   held-out acceptance gate for the evolution loop (see skillforge/docs/en/skillopt-borrow-decision.md),
   landed early.
4. **Doc status drift fixed** — INTEGRATION-E2E phase 1 split into 1a (4-scenario baseline,
   GO ✅) / 1b (6 family suites, in progress); TASK-FAMILIES §8 now carries status markers.
5. **Planning/code ratio alert → planning frozen (2026-07-02)** — ~2600 lines of planning,
   17 D-decisions, 0 lines of task-family code. Saturation reached: design questions are
   now build-time decisions (logged one line here); execution runs in tranches T1–T4 (§2);
   step 3b carries an explicit TDD/isolation discipline; step 4 split into 4a/4b.

## 4. Tracked-open items (do not lose)

| Item | State | Home |
|---|---|---|
| Phylax FMEA (policy from failure-mode analysis) | open | mindloop DEV-PLAN §8 |
| D2: L4 trace → tempomem core merge | deferred | mindloop DEV-PLAN §8 |
| `negation_constraints` SubTask field | not added (B2R parity) | mindloop DEV-PLAN §8 |
| Cloud → Thor switch (P6 exit) | pending hardware | mindloop DEV-PLAN P6 |
| P7.3–7.4 edge stack + degradation telemetry | deferred | mindloop DEV-PLAN P7 |
| D3 real-HW body track (BT/reflex tiers) | pending | bodylink design docs |
| Owner access-control spec (runtime region-policy override) | flagged | TASK-FAMILIES §1.2 |
