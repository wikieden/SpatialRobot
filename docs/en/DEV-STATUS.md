# DEV-STATUS — consolidated development plan (routing page)

> **Consolidated from** [TASK-FAMILIES.md](TASK-FAMILIES.md) §8 × [INTEGRATION-E2E.md](INTEGRATION-E2E.md) §6
> × [mindloop DEV-PLAN](../../mindloop/docs/en/devplan/DEV-PLAN.md). Those remain the single
> sources of truth for their areas; this page is the routing/status view. Updated **2026-07-04**.

## 1. Members × status

| Member | Done | In progress | Next |
|---|---|---|---|
| **tempomem** | core (fuse/persist/query/serialize), regions, decay, viz; **semantic Tier-1 landed** (edges/properties/events, migration 002); **`last_seen` landed** (step 2 ✅) | — | dynamic-scene P4 feeds (deferred) |
| **worldsense** | RGB(-D)→world Detections, CLIP behind extra | — | dynamic-scene P4 live perception (deferred) |
| **mindloop** | P0–P5 ✅; P6 ◐ (eval + real-LLM validated; Thor pending HW); P7 ◐ (7.1 failover + 7.2 voice seams ✅); dynamic-scene 1–4 ✅; **TempoMem rename landed**; **steps 3/3b landed**; **step-7 software landed** (D-I binding ambiguity, D-D macro expansion, D-P advisory reliability, P7.3 ListenerInterruptSource, P7.4 degraded mode) | — | hardware tracks: Thor switch; mid-step preempt (needs bodylink cancel/pause/resume) |
| **bodylink** | D3 manifest framework, MockBody, Genesis sim, conformance kit, 4 builtin bodies; **step-1 verbs landed** (13 common + arm subset) | — | D3 real-HW track (BT/reflex tiers); cancel/pause/resume handshake (mid-step preempt) |
| **voicelink** | EndpointListener/Speaker (Qwen3-ASR/TTS); barge seam reachable via mindloop `ListenerInterruptSource` | — | on-body streaming ASR+VAD fill of `audio_source` (hardware) |
| **skillforge** | ENPIRE skeleton, 4-scenario baseline harness GO ✅, **evolve acceptance gate landed**; six suites GO; templates (D-Q); data loop (curate/author/crystallize); **D-G composite reward**; **D-P Scorecard**; voice-tour example | — | LLM-rollout scale-up on the host (optional deepening) |

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
  3 ✅ safety      done 2026-07-02 — named_params · D1 param gate · D-A service regions · Q6 defaults · D-K menu/allergen (fail-closed)
  3b ✅ dynamics   done 2026-07-02 — 3 TDD slices, each committed green: inbox+classifier ·
                   between-step barge (abort/resume/supersede/correct, Phylax re-vet) ·
                   Clarifier + per-task ask budget + ESCALATE routing (150 tests total)
T3 ──────────────────────────────────────────────────────────── closure batch
  4a ✅ harness    done 2026-07-02 — 11 family metrics + required_metrics (D-F) · L1
                   invariants in the runner (D-N) · six suites (tour/chores/find/cleaner/
                   receptionist/execution-dynamics) baseline GO, every exercised metric 1.0
  4b ✅ harness    done 2026-07-02 — load_role/effective_verbs/vet_role (D-O) · templates.py
                   (tidy/privacy/find generators, seed-deterministic, 19 variants GO — D-Q)
T4 ──────────────────────────────────────────────────────────── validation batch
  5 ✅ real LLM    done 2026-07-04 — host 172.16.1.12 (new IP), Cosmos-Reason2-8B via vLLM,
                   temp=0+seed: 4/4 GO (intent/plan/policy/citation 1.0), turn p95 ~0.25 s
      ∥ E2E phase 3 ✅ sim body (Genesis): 21/21 physical scenarios GO (~48 s, 2026-07-04)
──────────────────────────────────────────────────────────────
  6 ✅ data loop   done 2026-07-04 — curate (home-scoped, speech-scrubbed, no cross-home merge)
                   · LLMPolicyAuthor (BYO Verbalizer) · crystallize (learned SkillCard, no safety
                   keys — D-L) · gate.py promote gate; learn→reuse closed (learning_loop.py).
                   Remaining deepening: D-G composite reward shaping (task/handle/honesty weights)
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

## 3a. Review round (2026-07-04, step-7 batch)

Independent review of the 10 landed commits: **0 CRITICAL · 1 HIGH · 3 MEDIUM · 3 LOW**;
no ratified-semantics violations, no safety regressions (all vet points verified on the
per-turn gate). Fixed same day: HIGH-1 serve_mode telemetry leaking into the skill
scorecard; MEDIUM-1 macro missing-arg silent degrade (now warns); MEDIUM-2 zero-score
binding ties silently trusting position 0 (now ambiguous when labels differ). LOWs
logged as intentional (first-ambiguity-only ask; non-unit Weights sums allowed;
unanswered asks still spend budget).

## 3b. Build-time decisions (logged per the planning freeze)

- **D-I**: "close in score" = within 0.75x of the top hit (scale-free ratio); a binding
  ask consumes the same per-task ask budget as escalate-asks; clarifier-less brains
  proceed on top-1 (logged).
- **D-D**: expansion table `deliver→navigate+offer`, `sweep→navigate+vacuum`,
  `mop→warn+navigate+mop+warn`; single-pass, so mop's atomic core keeps its name;
  trace migration = additive `macro_parent` column.
- **D-P**: scorecard lives in skillforge (lab side); planner-context disclosure bar 0.8;
  never-tried buckets stay `None` (no self-fulfilling avoidance).
- **P7.4**: offline = `mode_probe() == "fallback"`; the offline Phylax gate is a swap-in
  (tighten-only); disclosure appends to task `speak` only (answers keep citation text
  intact, `HandleResult.mode` carries the tier for the UX layer).

## 4. Tracked-open items (do not lose)

| Item | State | Home |
|---|---|---|
| Phylax FMEA (policy from failure-mode analysis) | open | mindloop DEV-PLAN §8 |
| D2: L4 trace → tempomem core merge | deferred | mindloop DEV-PLAN §8 |
| `negation_constraints` SubTask field | not added (B2R parity) | mindloop DEV-PLAN §8 |
| Cloud → Thor switch (P6 exit) | pending hardware | mindloop DEV-PLAN P6 |
| P7.3–7.4 edge stack + degradation telemetry | software done 2026-07-04 (seam + P7.4); on-body ASR/TTS/LLM install pending HW | mindloop DEV-PLAN P7 |
| D3 real-HW body track (BT/reflex tiers) | pending | bodylink design docs |
| Owner access-control spec (runtime region-policy override) | flagged | TASK-FAMILIES §1.2 |
