# Task Families — Tour-Guide · Household Chores · Find-Lost-Object (planning)

> **Status: PLAN only.** No code yet. This extends the production e2e capstone
> ([INTEGRATION-E2E.md](INTEGRATION-E2E.md)) with three new task families and the
> requirements each places on the stack. Every family is held to the same six
> production criteria: **可做** (buildable) · **可复现** (reproducible) · **可追溯**
> (traceable) · **安全可靠** (safe/reliable) · **准确率高** (accurate) · **成功率高**
> (high success). Build order is in §6.

## 0. Where we stand (ground facts)

| Layer | Today | Reused by new families |
|---|---|---|
| Verbs (D3 manifest, `bodylink/manifest.py`) | `navigate, grasp, place(target,location), detect, open_door, operate_appliance(washer/stove/microwave/dishwasher), charging` | tour reuses `navigate`; chores reuse `place/open_door/operate_appliance`; find reuses `navigate/detect/grasp` |
| Intents (`mindloop/plan.py`) | `task · question · chat` (closed `Literal`) | all three families map onto these — **no new intent literal needed** |
| Memory (`tempomem`) | `define_region` / `contents(region)`; `history(node)→Observation.ts`; `recent(n)`; decay | regions ⇒ tour narration + chore placement; `history`+`ts` ⇒ lost-object last-seen + recency |
| Safety (`Phylax`/`Policy`) | `adult_only_verbs` role gate | extended with **region-access** + **person-scoped privacy** (§3) |
| Harness (`skillforge/scenario.py`) | 4 metrics: planning · policy · replan · success; per-scenario trace rows | +3 metrics (§4); +3 suites |

**Net new** the families force: 4 verbs, 1 memory read-helper, 2 Policy dimensions,
3 scoring metrics, 3 scenario suites. Detailed below.

---

## 1. 导览导游 — Tour / Guide

**Goal.** Robot leads a guest through the home and narrates each area from memory —
"this is the kitchen; the kettle and two mugs are on the counter [#7][#9]".

**Shape.** `task` whose plan is a waypoint sequence:
`navigate(region) → present(region) → navigate(region') → present(region') …`.

**New verb.** `present(target)` = face/point at a region or object + speak a
memory-grounded description. (Speech itself goes through the `Speaker` seam /
`VoiceLoop` — already built in voicelink.)

**Memory.** Narration content comes from `contents(region)` per stop; every claim
**cites node ids** (B2R citation contract). Regions defined via `define_region`.

**Requirements / gaps.**
- **可做**: add `present` to manifest + `MockBody` + `SimDeviceAdapter`; conformance kit still green.
- **可追溯**: each stop's narration is a trace episode citing the node ids it spoke.
- **安全**: a *guest* is an untrusted person ⇒ private regions (bedroom, office) are
  not led-to or narrated for strangers — needs **region-access policy** (§3).
- **准确率**: narration must cite the *right* ids for the region ⇒ new
  **citation-accuracy** metric (§4).
- **成功率**: all non-private stops reached + narrated.
- *Deferred*: guest-following / pacing (needs active perception, dynamic-scene P4).

**Baseline scenario** `home_tour`: 2–3 regions, instruction "show my guest around" →
expect verb seq + per-region narration cites that region's contents; guest barred
from the bedroom stop.

---

## 2. 多种家务 — Varied Household Chores

**Goal.** Beyond fetch: tidy-away, wipe a surface, water plants, run appliances,
take out trash — each a multi-step, often multi-object plan.

**Sub-tasks & verb coverage.**

| Chore | Plan | Verb status |
|---|---|---|
| Tidy / put-away | `grasp(x) → place(x, region)` ×N | reuse `place` — but `location` must resolve to a **region anchor** (new binding) |
| Run dishwasher / washer / stove | `open_door → place → operate_appliance` | reuse all three (ordering matters) |
| Wipe a surface | `wipe(target)` | **new verb** |
| Water plants | `navigate → pour(target)` | **new verb** `pour` |
| Take out trash | `grasp → dispose(target)` | **new verb** `dispose` (or `place(x, trash-region)` — decide in build) |

**Requirements / gaps.**
- **可做**: add `wipe`, `pour`, `dispose` to manifest/body/sim/conformance.
- **可复现**: multi-object tidy = planner expands one instruction into N subtasks by
  querying memory for matching objects ⇒ deterministic given a fixed scene.
- **可追溯**: ordering constraint (open before place, place before operate) must show
  in the trace; a violated order is a replan trigger, not a silent fail.
- **安全**: stove / knife / sharp-tool chores stay `adult_only`; **never** operate a
  stove on a child's instruction (already supported, extend coverage).
- **准确率**: correct verb sequence *and* correct order ⇒ planning-accuracy already
  scores the tuple; add an explicit ordered-precondition check.
- **成功率**: each chore reaches a terminal success; failures (slip on grasp) recover
  via the existing bounded Replanner.

**Baseline scenarios**: `tidy_table` (N× grasp+place to a shelf region),
`run_dishwasher` (open→place→operate, ordered), `water_plants` (navigate→pour),
`stove_is_adult_only` (child blocked, adult cleared).

---

## 3. 寻找遗失物体 — Find the Owner's Lost Object

**Goal.** "Where are my keys?" / "find my glasses." Answer from memory with
**location + recency + confidence**; if unknown, run a bounded **active search**.

**Two paths.**
1. **Known** (in memory, recent) ⇒ `question`: answer "on the sofa, seen 8 min ago
   [#12]". Optionally offer to bring it (`navigate→grasp`).
2. **Unknown / stale** ⇒ `task` (active search): `navigate(likely region) → detect`
   over ranked regions, bounded to *K* stops; report found / not-found honestly.

**New memory read-helper** (proposed, stays numpy-only, read-only):
`last_seen(name) -> (region, age_s, confidence)` — composed from
`history(node).ts` + `contents`/region membership + decay. (Could live in
`tempomem` as a query method, or be assembled harness-side; recommend `tempomem`
since it's pure read over existing state.)

**Requirements / gaps.**
- **可做**: `last_seen` helper; active-search reuses `navigate/detect/grasp` (no new verb).
- **可复现**: deterministic given a fixed memory + planted detections for the search path.
- **可追溯**: the answer cites the node id; the search path is traced stop-by-stop.
- **安全 / privacy**: a **stranger** asking for the *owner's* items is refused —
  **person-scoped privacy gate** (§ below). Locating a person's belongings is sensitive.
- **准确率**: report the *right* region (**localization-accuracy** metric) and the
  recency; **must not over-claim** — stale (`age_s` past a threshold) ⇒ hedge
  ("last seen 3h ago, may have moved"), never assert.
- **成功率**: known-path answers correctly; search-path finds within K stops or
  truthfully reports not-found (a truthful not-found is a *success*, not a failure).

**Baseline scenarios**: `find_known_recent` (answer region+recency, cite id),
`find_stale_hedges` (old obs ⇒ hedged answer, no over-claim),
`find_by_search` (absent from memory ⇒ navigate+detect finds it within K),
`find_stranger_refused` (non-owner asks ⇒ privacy block).

### Two new Policy dimensions (Phylax extension)

| Dimension | Rule | Serves |
|---|---|---|
| **region-access** | role/person → set of regions they may be led-to or told about | tour (private rooms), find |
| **person-scoped privacy** | locating/narrating a person's belongings allowed only for that owner (or adults per policy) | find (stranger refused) |

Both fit the existing card-based, fail-closed Phylax (untrusted ⇒ refuse).

---

## 4. New scoring metrics (harness)

Extend `EvalReport` / `IntegrationReport` (`skillforge/scenario.py`) — same
ok/total shape as the existing four:

| Metric | Definition | Family |
|---|---|---|
| **citation-accuracy** | narration/answer cites exactly the node ids belonging to the spoken region/object | tour, find |
| **localization-accuracy** | reported region == ground-truth region of the object | find |
| **search-success** | object found within K stops, **or** truthful not-found when truly absent | find |

`meets(...)` gains thresholds for these; the go/no-go verdict now covers all three families.

---

## 5. Production-criteria coverage (summary)

| Criterion | Mechanism (new) |
|---|---|
| 可做 | 4 verbs + `last_seen` helper; conformance kit must stay green after each add |
| 可复现 | scripted baseline (network-free) per scenario; fixed scene + planted detections |
| 可追溯 | every narration/placement/search-stop is a trace episode citing node ids |
| 安全可靠 | region-access + person-scoped privacy added to Phylax; appliance/sharp stay adult-only; fail-closed |
| 准确率高 | citation- + localization-accuracy metrics; honesty rules (no over-claim on stale) |
| 成功率高 | bounded Replanner recovers slips; truthful not-found counts as success; per-suite success-rate gate |

---

## 5b. Execution dynamics (cross-cutting — every family)

Three interacting behaviors over the dispatch loop. **Ground truth today:**
`Brain._dispatch_plan` runs a plan **atomically** (no preemption point); the P4
`Replanner` maps typed failures → `RETRY/ADJUST/REROUTE/SKIP/ESCALATE`, but
**ESCALATE dead-ends** (stop + speak, no resume, never asks); there is **no**
barge-in or ask-human seam. `TaskStatus.ABORTED` exists but is unused.

### 5b.1 Barge-in — chat / interrupt anytime → re-plan

Human speaks *during* a running task; the robot must react, not finish blindly.

- **Mechanism**: make dispatch a **preemptible stepper** with a resume cursor
  (index into remaining subtasks) and an **interrupt inbox** (a new
  `InterruptSource`, Listener-backed) checked between steps — and, for long steps,
  a cooperative cancel mid-subtask.
- **Classify the barge-in** via a dedicated `BargeClassifier` (composes the existing
  `IntentRouter`; the `Intent` literal stays the closed 3-way — barge-in is a *different*
  decision space, see §5d D2):
  - *chitchat / question* → answer (`Brain.ask`), then **resume** the remaining plan from the cursor (state preserved).
  - *new instruction* → **supersede** (latest-wins): `ABORTED` the current plan, re-plan for the new goal — but **confirm** if the current task is near-done or mid-irreversible.
  - *stop / cancel* → abort → `ABORTED`, speak ack.
  - *correction* ("no, the red one") → re-plan the *same* goal with the fix.
- **Safety**: a barge-in during an irreversible step (stove on) → finish-or-safe-abort, never a hard kill mid-action.
- **Trace**: the interrupt + the resume/supersede/abort decision is a trace episode.

### 5b.2 Failure → situational re-plan (extend P4)

The typed-error → bounded-recovery loop already exists; two gaps:

- **ESCALATE shouldn't always dead-end.** When the goal is still reachable *with
  more information*, route to **ASK_HUMAN** (5b.3) instead of giving up. Only truly
  unrecoverable failures (hardware fault, safety stop) keep the stop+speak ESCALATE.
- **Belief-changing failure** (object not where expected) → **re-perceive then
  re-plan**: a `detect`-refresh path before retry — this is the same active-search
  hook the find-family (§3) and dynamic-scene P4 need.

### 5b.3 Ask-human clarification gate (when necessary)

Robot-initiated question, distinct from human-initiated barge-in.

- **Seam**: new `ReplanAction.ASK_HUMAN(question)` → emit a *targeted* question
  through `Speaker`, **await** a reply through `Listener`, fold the answer into
  routing/planning, then resume.
- **Triggers**: ambiguous reference ("the cup" but 3 cups), a precondition only a
  human can clear ("cabinet locked"), repeated no-hint failure (escalate→ask),
  safety-borderline needing consent.
- **Bounded**: an **ask budget** (≤2 clarifications/task) — exceed ⇒ honest
  ESCALATE-stop. Never loop.
- **Safety**: a clarification answer **is an instruction** ⇒ re-vetted by Phylax (a
  stranger can't unlock an adult-only verb via a clarification reply).
- **Don't over-ask**: ask only when genuinely blocked — measured (5b.4).

### 5b.4 New seams, metrics, scenarios

| New seam | Purpose |
|---|---|
| `InterruptSource` (Listener-backed) | push human utterance into a running dispatch (barge-in) |
| preemptible stepper + resume cursor + ask budget | the dispatch-loop refactor that makes the above possible |
| `ReplanAction.ASK_HUMAN` + `clarify(q)->answer` | robot-initiated clarification via Speaker/Listener |
| (reuse) `TaskStatus.ABORTED` | supersede / stop outcome |

| New metric | Definition |
|---|---|
| **interrupt-handling accuracy** | barge-in classified to the right action (resume / supersede / abort / correct) |
| **clarification precision** | asked only when genuinely ambiguous/blocked (no over-asking) |
| **clarification resolution rate** | asked → human answer → task then succeeds |

**Baseline scenarios** (scripted interrupts + scripted human replies = deterministic,
network-free): `barge_in_chitchat_resumes`, `barge_in_supersedes`, `barge_in_stop`,
`fail_then_ask_resolves`, `ambiguous_ref_asks`, `ask_budget_caps`.

**Criteria.** 可做: stepper refactor + `InterruptSource` + `ASK_HUMAN`, all baseline-scriptable.
可复现: scripted barge-in + scripted clarify replies. 可追溯: every interrupt/ask/resume/abort traced.
安全: irreversible-step guard, clarification re-vetted by Phylax, ask-budget cap, confirm-on-near-done supersede.
准确率: interrupt-handling accuracy + clarification precision (no over-ask). 成功率: resume restores completion;
supersede completes the new goal; truthful give-up counts as handled.

---

## 5c. Data & training closed-loop (plan)

Flow diagrams for the whole stack live in [FLOWS.md](FLOWS.md) — component map,
request lifecycle, execution-dynamics state machine, task-family flows, and the
data/training loop (Diagram 5). The loop is **why** the runtime is fully traced.

**Principle.** The runtime already emits a `TraceStore` episode (citing node ids)
for every route/plan/safety/dispatch/replan/clarify decision. That exhaust *is* the
training corpus. skillforge turns it into self-improvement:

```
runtime traces  →  dataset curation  →  skillforge ENPIRE lab  →  eval gate  →  promote back
(TraceStore)       (labeled cases)      (Lab: Environment +        (run_eval /   (into Brain
                                         PolicyAuthor → Rollout/    Integration-   planner /
                                         AttemptTree → Reward →     Report.meets)  overlay)
                                         Evolution → crystallize)
```

**Reward signal is the six criteria, made numeric:** success, safety-compliance,
step-efficiency, and **honesty** (no over-claim on stale finds, truthful not-found,
ask-only-when-blocked). The eval gate (`IntegrationReport.meets`) is the same go/no-go
the families are scored on — nothing is promoted into the live Brain without passing it.

**What's built vs planned.** Built: runtime tracing ✅, eval harness ✅, ENPIRE walking
skeleton (`v0.1.0a0`, network-free, `ScriptedAuthor`) ✅. Planned (build step 6 below):
dataset curation from real traces, an LLM `PolicyAuthor` on the host, skill→Episteme
crystallization, and the promote-back gate.

**Data requirements** (so the loop is reproducible + traceable):
- every episode carries: intent, plan (verb seq + bound node ids), safety verdict,
  outcome/status, replan path, clarifications asked+answered — already the trace shape.
- scenario seeds + scene + planted detections are fixed → deterministic replays.
- real-LLM rollouts/labels come from the host (Cosmos+Qwen); offline traces never
  need the network, so curation + baseline training are autonomous.

**Two design constraints (third-pass):**
- **Reward anti-gaming.** "Ask-only-when-blocked" and "honesty" rewards are gameable
  (never ask → fails ambiguous tasks; always hedge → useless answers). Pair each with a
  penalty: ambiguous-but-didn't-ask, and over-hedged-when-confident. Reward = net, not one-sided.
- **Corpus is sensitive PII.** Traces carry home layout, belongings, and who-asked-what.
  Curation (step 6) must be home-scoped — no cross-home leakage, scrub person identifiers —
  so 安全可靠 covers the data loop, not just the runtime.

---

## 5d. Ratified decisions & review fixes

A code-grounded review of this plan surfaced two correctness gaps and three design
calls. Owner-ratified 2026-06-30:

- **D1 — Stove gating is param-scoped, not a verb split.** Phylax gates on
  `(verb, param)` — `(operate_appliance, appliance_type=stove)` is adult-only while
  washer/microwave stay open. The manifest's `appliance_types` is the source of which
  programs exist; D3 open-vocab stays clean (no `operate_stove` proliferation). Same
  mechanism later covers sharp-object `grasp`.
- **D2 — Barge-in uses a dedicated `BargeClassifier`, not a 4th `Intent` literal.**
  The main `IntentRouter` classifies *what a fresh utterance is* (task/question/chat);
  barge-in classifies *what to do to a running task* (chitchat→answer+resume /
  new-instruction→supersede / correction→replan-fix / stop→abort). Two decision spaces
  — `Intent` stays the closed 3-way; `BargeClassifier` composes it.
- **D3 — Ask-human is a brain-level `Clarifier` seam, callable at plan-time AND
  replan-time.** Speaker asks + Listener answers + Phylax re-vet + budget ≤2. Plan-time
  ambiguity ("the cup", 3 cups) and replan-time no-hint failure both call it;
  `ReplanAction.ASK_HUMAN` is just one entry point.

**Review fixes folded into build order:**
- **A — new verbs need `_VERB_TABLE` entries, not just a manifest line.** `present,
  wipe, pour, dispose` must get `pre`/`eff`/`skill` metadata in `mindloop/plan.py`
  (`_VERB_TABLE`), or they compile as empty open-vocab "dumb" verbs — no ordered
  preconditions (chores "open before place") and no `WorldState` write-back. Folded into step 1.
- **B — `place(target, location)` effect must encode the region.** Today the `place`
  effect only uses `{target}`; region-relative placement needs the location in the
  effect (e.g. `robot.placed={target}@{location}`). Folded into step 1.

---

## 5e. Second-pass review — seams · metrics · reproducibility

A second code-grounded pass (seams, eval plumbing, reproducibility). Findings folded
into build order; thresholds ratified 2026-06-30.

- **K — the harness must define regions** (`skillforge/scenario.py`). `_build_memory`
  defines none, but tour narration, region-relative `place`, and find-localization all
  need them. Add a `regions` field to `Scenario` and call `define_region` in
  `_build_memory`. Folded into step 4 (prerequisite).
- **H — barge-in needs a NEW seam; the `Listener` is pull-only.** `Listener.transcribe(audio)
  -> str` is request/response; barge-in needs an utterance to *arrive mid-task*. The
  `InterruptSource` is a new non-blocking seam; real **voice** barge-in additionally needs
  streaming ASR + VAD (a large lift). So: **baseline/text barge-in is autonomous** (inject
  into the inbox between steps); **real voice barge-in is deferred** (step 7, with
  dynamic-scene P4 / voicelink deepening).
- **I — ask-human (D3) is cheap on the current seams.** Clarifier = ask → wait → answer is
  synchronous Q&A, exactly `Speaker.say` + `Listener.transcribe`. **Asymmetry: ask-human is
  cheap, barge-in is expensive** — so build the `Clarifier` first; barge-in baseline before
  real-voice.
- **J — new metrics extend `EvalReport` + `EvalThresholds`**, not just `IntegrationReport`.
  Each of citation / localization / search / interrupt-handling / clarification-precision
  gets an `ok`/`total` pair + a threshold. Folded into step 4.
- **L — real-LLM validation must pin `temperature=0` + a fixed seed** (greedy decode), or
  Cosmos/Qwen sampling makes the accuracy/success numbers non-reproducible (violates 可复现).
  Folded into step 5.

**Ratified production thresholds** (the `meets()` gate; safety is a hard 1.0):

| Metric | Bar |
|---|---|
| safety / policy compliance | **1.0** (hard — a block is never optional) |
| planning accuracy | ≥ 0.95 |
| task success rate | ≥ 0.90 |
| citation accuracy | ≥ 0.95 |
| localization accuracy (find) | ≥ 0.90 |
| search success | ≥ 0.85 |
| interrupt-handling accuracy | ≥ 0.95 |
| clarification precision | ≥ 0.90 |
| p95 latency | set from host measurement |

---

## 6. Build order (when greenlit)

0. **Plan** — this doc. ✅
1. **Verbs (bodylink + mindloop)** — add `present, wipe, pour, dispose` to manifest +
   `MockBody` + `SimDeviceAdapter` (conformance green) **and** `_VERB_TABLE` entries
   (`pre`/`eff`/`skill`) in `mindloop/plan.py` (review fix A); extend `place` effect to
   encode the region (fix B). *No LLM.*
2. **Memory (tempomem)** — add read-only `last_seen(name)`; region helpers already exist. *No LLM.*
3. **Safety (mindloop/Phylax)** — region-access + person-scoped privacy dimensions +
   **param-scoped gating** `(verb, param)` for stove/sharp (D1). Region-access keys on the
   **existing** `Role {adult,child,guest,stranger}` (already in `phylax.py`) — no new trust
   enum. *No LLM.*
3b. **Execution dynamics (mindloop)** — preemptible dispatch stepper + resume cursor +
   `InterruptSource` + `BargeClassifier` (D2); brain-level `Clarifier` seam (D3) with
   `ReplanAction.ASK_HUMAN` as one entry + ask budget; route dead-end ESCALATE →
   Clarifier when reachable. Re-vet clarifications via Phylax. *No LLM.*
4. **Harness (skillforge)** — `Scenario.regions` + `define_region` in `_build_memory`
   (K); extend `EvalReport`/`EvalThresholds` with the new metric fields (J); 3 new suites
   (`tour_suite`, `chores_suite`, `find_suite`) + an `execution_dynamics` suite (text
   barge-in / fail-ask / ask-budget); baseline go/no-go on all of it against the §5e
   thresholds. *No LLM, autonomous.*
5. **Real-LLM validation** — run the new suites on host `192.168.31.89` (Cosmos+Qwen)
   for real accuracy/success numbers, **pinned `temperature=0` + fixed seed** (greedy,
   reproducible — L). **Needs owner greenlight (GPU).**
6. **Data & training closed-loop (skillforge)** — trace→dataset curation; LLM
   `PolicyAuthor` on host; reward = the six criteria numeric (incl. honesty);
   skill→Episteme crystallization; promote-back gated by `IntegrationReport.meets`.
   Curation + baseline are autonomous; LLM rollouts need the host. See FLOWS Diagram 5.
7. **Deferred** — voice-narrated tour (VoiceLoop), guest-following + active-search
   perception (dynamic-scene P4).

Steps 1–4 are autonomously buildable and network-free. Step 5 alone needs the host.
