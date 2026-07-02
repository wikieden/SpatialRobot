# DEV-STATUS — consolidated development plan (routing page)

> **Consolidated from** [TASK-FAMILIES.md](TASK-FAMILIES.md) §8 × [INTEGRATION-E2E.md](INTEGRATION-E2E.md) §6
> × [mindloop DEV-PLAN](../../mindloop/docs/en/devplan/DEV-PLAN.md). Those remain the single
> sources of truth for their areas; this page is the routing/status view. Updated **2026-07-02**.

## 1. Members × status

| Member | Done | In progress | Next |
|---|---|---|---|
| **tempomem** | core (fuse/persist/query/serialize), regions, decay, viz; **semantic Tier-1 landed** (edges/properties/events, migration 002) | — | step 2 remainder: verify/complete `last_seen`, `last_changed`, `current_occupants` |
| **worldsense** | RGB(-D)→world Detections, CLIP behind extra | — | dynamic-scene P4 live perception (deferred) |
| **mindloop** | P0–P5 ✅; P6 ◐ (eval + real-LLM validated; Thor pending HW); P7 ◐ (7.1 failover + 7.2 voice seams ✅); dynamic-scene 1–4 ✅; **TempoMem rename landed** | — | steps 1 (`_VERB_TABLE`), 3 (Phylax ext), 3b (execution dynamics) |
| **bodylink** | D3 manifest framework, MockBody, Genesis sim, conformance kit, 4 builtin bodies | — | step 1: ~12 new verbs in manifest/mock/sim |
| **voicelink** | EndpointListener/Speaker (Qwen3-ASR/TTS) | — | step 7: real voice barge-in (streaming ASR+VAD, deferred) |
| **skillforge** | ENPIRE skeleton, 4-scenario baseline harness GO ✅, **evolve acceptance gate landed** (held-out strict improvement) | step 4 partial (scenario structure) | step 4 full: 6 family suites + new metrics + regions |

## 2. Unified execution order (dependency chain)

```
0 ✅ land WIP (TempoMem rename + semantic layer + gate)        [done 2026-07-02]
1 ▢  verbs        bodylink manifest/mock/sim + mindloop _VERB_TABLE + place-region eff
2 ◐  memory       Tier-1 landed; verify/complete last_seen · last_changed · current_occupants
3 ▢  safety       Phylax: D-A robot_service · D1 (verb,param) gating · Q6 region defaults · D-K menu.py
3b ▢ dynamics     InterruptSource · BargeClassifier (D2) · Clarifier + ASK_HUMAN (D3) · ask budget
4 ◐  harness      Scenario.regions · EvalReport/Thresholds fields · 6 suites · required_metrics (D-F)
                  → baseline go/no-go vs §7e thresholds        [needs 1+3+3b for real assertions]
5 ▢  real LLM     host 192.168.31.89, temp=0 + fixed seed      [NEEDS GPU GREENLIGHT]
     ∥ E2E phase 3: sim body (Genesis) pass                    [autonomous]
6 ◐  data loop    trace→dataset · LLM PolicyAuthor · Episteme crystallization · promote gate
                  (gate.py landed early as the acceptance-gate piece)
7 ▢  deferred     voice tour / real voice barge-in (P7.3–7.4) · active perception (dyn-scene P4)
```

Steps 1–4 are autonomous + network-free. Step 5 alone needs the host. Step 4's six
suites depend on 1 + 3 + 3b being in place before their assertions are real.

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
