# Task Families — Tour-Guide · Household Chores · Find-Lost-Object · Cleaner · Receptionist (planning)

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

**Net new** (updated after Round 3 review — see §7f for exact counts):
~12 atomic verbs + 1 macro verb, 6 Tier-1 memory methods (+2 `.smem` tables),
3 Phylax extensions (`robot_service`, service-region gate, named-param inspection),
9 metrics, 6 suites. Detailed below.

---

## 1. 导览导游 — Tour / Guide

**Goal.** Robot leads one or more guests through a venue/home and narrates each area
from memory — "this is the kitchen; the kettle and two mugs are on the counter [#7][#9]".

**Core verb.** `present(target)` = face/point at a region or object + speak a
memory-grounded description. Speech goes through the `Speaker` seam / `VoiceLoop`
(already built in voicelink). Every claim **cites node ids** (B2R citation contract).
Narration content comes from `contents(region)` per stop; regions defined via `define_region`.

---

### 1.1 Tour Modes

Three operating modes share the same waypoint plan structure but differ in who controls pacing and how many guests are served.

#### Mode A — Interactive Tour (自由导览)

One-on-one or small-group, human-paced. A user or guide signals each transition.

```
navigate(stop_i) → present(stop_i) → wait_for_signal()
  → [optional Q&A at stop] → navigate(stop_i+1) → …
```

- **Trigger**: explicit instruction from guest/guide ("next", "continue", or barge-in
  with a question that counts as "I'm done here").
- `wait_for_signal()` is a **Listener-gated hold** (voicelink `EndpointListener`):
  robot stays at the stop, ready to answer questions, until it hears a continue cue
  or a timeout fires.
- Questions asked at a stop → handled as a sub-conversation (single `converse` turn);
  tour resumes when the guest signals readiness.
- **Policy gate**: if guest asks about a private region, Phylax blocks; robot says "I
  can't show you that area" and stays on route.

#### Mode B — Auto-Leader Tour (领队模式)

Robot autonomously paces the full tour; no human trigger needed between stops.
Designed for groups (museum, office, showroom).

```
for stop in itinerary:
    navigate(stop) → present(stop) → timed_pause(stop.dwell_s)
→ conclude_tour()
```

- `dwell_s` per stop comes from the task manifest or a default (e.g., 30 s).
- Robot manages its own timing; guests follow (dynamic following / crowd perception
  deferred to active-scene P4).
- Barge-in still accepted at any time (§1.3); robot inserts an answer then resumes
  the auto-paced loop.
- `conclude_tour()` = navigate back to home position + speak closing remarks.

#### Mode C — Ambient Service (自由聊天 / 主动服务)

When **not** on a structured tour task, robot operates in a *free-service* mode:
responds to ad-hoc requests, proactively offers help within its **responsibility scope**.

- Not modelled as a `task`; implemented as an idle `VoiceLoop` iteration: listen → if
  intent matches a service → fulfill; else converse freely.
- **Scope filter** (Phylax pre-check before any movement): robot only acts on requests
  within its defined role (e.g., guide to bathroom, answer venue questions, lead to
  an exhibit). Requests outside scope (e.g., "buy me food") → polite decline.
- **Proactive offers**: if robot perceives a guest looking lost or asking a vague
  question, it may volunteer "Would you like me to guide you to X?" — one offer
  only, no repeat nagging (anti-spam policy).
- Ambient mode is the **default fallback** when no `task` is active and the
  `VoiceLoop` is running.

---

### 1.2 Region-Access Policy (Phylax extension)

A *guest* is untrusted. Private regions (bedroom, office, server room) carry an
`access_policy: guest_blocked` annotation on the `define_region` record.

- Any plan step that would `navigate` or `present` a blocked region is vetoed by
  Phylax **at compile time** (not at execution time).
- Ambient-mode service requests that would enter a blocked region are blocked the
  same way and robot speaks: "That area is private — I can't guide you there."
- Owner / trusted user can override the policy at runtime by resetting the annotation
  (out-of-scope for this doc; flag for access-control spec).

**Who defines regions, and when (ratified).** Regions are annotated **once at install
time** by the owner / setup walkthrough — human-labeled name + bbox via `define_region`,
not autonomously inferred. Region semantics ("is this private?") are a *judgment*, not a
geometric clustering output, and the tour privacy gate keys directly on the label —
a mislabel is a safety incident. Runtime is **read-only** over regions.

**Default stance (ratified).** Region access is **default-allow with an explicit
denylist**: only private regions carry `access_policy: guest_blocked`; unannotated
*known* regions are accessible. One guard preserves the fail-closed spirit: a region
that is **unknown/never registered** at runtime is treated as *refused*, not as
"absent from the denylist ⇒ allowed" — default-allow extends only to regions the
install-time walkthrough actually registered.

---

### 1.3 Interrupt Handling (中断机制)

Any tour mode (A or B) is **interruptible at any point** — mid-navigation or mid-narration.

**Interrupt taxonomy**

| Interrupt type | Example | Handling |
|---|---|---|
| **Chat / question** | "What year was this built?" | Answer inline (single `converse` turn), resume immediately |
| **Service request** | "Take me to the bathroom" | Suspend tour state, complete service sub-task, resume |
| **Emergency** | "I feel sick / fire alarm" | Suspend tour, escalate via Phylax safety lane, do not auto-resume |

**State machine**

```
TOURING ──barge-in──► HANDLING_INTERRUPT
                              │
                    ┌─────────┴──────────┐
               chat/Q&A              service-req
           (answer inline)       (sub-task completes)
                    └─────────┬──────────┘
                              │
                           RESUME?
                        yes ──► TOURING (from saved stop index)
                        no  ──► CONCLUDE or IDLE
```

- **Saved state**: before entering `HANDLING_INTERRUPT`, robot records
  `(current_stop_index, stops_remaining)` in the active trace episode.
- **Resume**: robot speaks "Resuming the tour — we were at [stop name]" then
  continues from the saved index.
- **No auto-resume for emergencies**: only resumes if guest explicitly re-requests
  the tour.
- Barge-in is implemented via the existing §5b.1 mechanism (Listener fires
  `barge_in` event → Replanner inserts interrupt sub-task → tour plan paused).

**Service-sub-task example (bathroom)**

```
suspend_tour(save_index=i)
navigate(region="bathroom") → present(region="bathroom")   # "The bathroom is here"
speak("Let me know when you're ready to continue.")
wait_for_signal()
resume_tour(from_index=i)
```

- The bathroom sub-task is itself subject to Phylax (is the bathroom a public
  region? default yes) and the full trace is logged as a nested episode.

---

### 1.4 Requirements / Gaps

- **可做 now**: add `present`, `wait_for_signal`, `conclude_tour` to manifest + `MockBody`
  + `SimDeviceAdapter`; conformance kit stays green.
- **可追溯**: each stop's narration is a trace episode citing the node ids it spoke;
  interrupt sub-tasks are nested episodes with `parent_episode_id`.
- **安全**: region-access policy (§1.2) + Phylax pre-compile veto + emergency
  non-resume.
- **准确率**: narration must cite the *right* ids for the region ⇒ new
  **citation-accuracy** metric (§6).
- **成功率**: all non-private stops reached + narrated; interrupts handled without
  losing tour state.
- *Deferred*: guest-following / crowd pacing (needs active perception, dynamic-scene P4);
  multi-guide handoff; `dwell_s` auto-tuning from engagement signals.

**Baseline scenarios**

| Scenario | Mode | Key assertion |
|---|---|---|
| `home_tour_interactive` | A | 3 stops, each gated by "continue"; bedroom barred |
| `home_tour_auto` | B | 3 stops auto-paced, no human input; same bedroom block |
| `tour_bathroom_interrupt` | A or B | Mid-tour "take me to bathroom" → sub-task → resume from saved index |
| `tour_question_inline` | A or B | Mid-narration barge-in Q&A → resume without losing stop index |
| `ambient_offer` | C | Guest asks vague question → robot offers to guide → guest accepts → Mode A |
| `ambient_scope_block` | C | Out-of-scope request → polite decline, no movement |

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
  recency; **must not over-claim**. Staleness criterion (ratified): reuse the existing
  decayed `confidence` (half-life 30 d, pruned below `min_conf=0.1`) as the *single*
  signal — `confidence ≥ 0.7` ⇒ answer plainly; `< 0.7` ⇒ hedge ("last seen 3h ago,
  may have moved"), never assert. `age_s` is still *spoken* for recency, but it does
  not get its own parallel threshold system.
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

## 4. 保洁员 — Cleaner / Housekeeping

**Goal.** Robot executes systematic cleaning of a venue — floors, surfaces, waste
removal, consumable restocking — either on a routine schedule or reactively when a
mess is detected.

**Plan shapes.**

| Trigger | Plan | Notes |
|---|---|---|
| Routine schedule | `for region in cleaning_itinerary: navigate(region) → clean_region(region)` | room-by-room, scheduler-driven |
| Reactive (detected mess) | `navigate(mess_location) → clean_spot(mess_location)` | highest-priority queue item first |
| Waste removal | `navigate(bin) → grasp(bag) → dispose(bag, outdoor_bin)` | reuse `grasp` + `dispose` |
| Consumable restock | `navigate(storage) → grasp(item) → navigate(target) → restock(item, target)` | **new verb** |

**New verbs.**

| Verb | Semantics |
|---|---|
| `sweep(region)` | Navigate + floor sweep/vacuum of region |
| `mop(region)` | Navigate + mop floor; triggers `warn_wet_floor(region)` before + after |
| `warn_wet_floor(region)` | Speak + optionally place a warning sign; **safety verb** |
| `restock(item, location)` | Place consumable (paper, soap, coffee pods) at a designated refill point |

`wipe(surface)` and `dispose(target)` reused from §2 (Household Chores).

**Memory.** Region map provides the cleaning itinerary and room adjacency. Cleaning
timestamps can be stored as relations (`relate(region_node, "last_cleaned", ts_node)`)
to support schedule-driven planning without external state.

**Requirements / gaps.**
- **可做**: add `sweep`, `mop`, `warn_wet_floor`, `restock` to manifest + `MockBody` +
  `SimDeviceAdapter` + `_VERB_TABLE`; `wipe` / `dispose` already planned.
- **可复现**: fixed scene + fixed itinerary → deterministic step sequence.
- **可追溯**: each region clean is a trace episode; `warn_wet_floor` events logged as
  safety sub-episodes.
- **安全**: wet floor is a slip hazard — `mop` always wraps in `warn_wet_floor` calls
  (pre- and post-); cleaning chemicals are robot-handled only (not handed to guests or
  children); hazardous tool chores (industrial cleaners) tagged `adult_only` in manifest.
- **准确率**: all scheduled regions cleaned in the right order; warnings issued
  correctly ⇒ **cleaning-coverage** metric (§6).
- **成功率**: full itinerary completes or reactive task resolves; partial failure
  (single room blocked by occupant) defers that room and continues, reports gap.

**Policy.** Cleaner operates on a `cleaner` role with access to all non-private
regions on schedule. Occupied rooms: robot knocks + `wait_for_signal()` (tour §1.1
mechanism, reused — a courtesy presence-check with its own timeout, **not** the
`ASK_HUMAN`/Clarifier seam and does not draw on the ask budget, D-L), or defers to
next slot on timeout. Private rooms require owner's explicit permission.

**Baseline scenarios**

| Scenario | Key assertion |
|---|---|
| `routine_sweep` | 3 regions in itinerary, swept in order, each logged as trace episode |
| `mop_wet_floor_warning` | mop triggers warn before + after; warning logged; slip-hazard flag in trace |
| `reactive_mess` | detected spill → navigate + wipe → cleaned before routine resumes |
| `restock_consumable` | soap low → navigate storage → navigate bathroom → restock |
| `occupied_room_defer` | room blocked by guest → defer, continue itinerary, report gap |

---

## 5. 接待员 — Receptionist / Host Service

**Goal.** Robot greets visitors, takes drink orders, serves tea / coffee / water,
and provides proactive hospitality within its defined scope.

**Plan shapes.**

| Action | Plan |
|---|---|
| Greet + take order | `navigate(guest) → greet(guest) → take_order(guest) → [prepare] → deliver(drink, guest)` |
| Deliver known preference | `navigate(guest) → greet(guest) → offer(preferred_drink, guest)` |
| Proactive refill | `navigate(guest) → offer(refill, guest)` (triggered by low-cup observation or timer) |
| Prepare drink | `navigate(station) → pour(liquid, cup)` (reuse `pour` from §2) |

**New verbs.**

| Verb | Semantics |
|---|---|
| `greet(target)` | Navigate to face guest + speak greeting; no action performed |
| `take_order(target)` | Speaker asks drink preference; Listener records answer; stores `prefers` relation in memory |
| `offer(item, target)` | Present item to a person and await acceptance signal (distinct from `place` — person must accept) |
| `deliver(item, target)` | `navigate(target) → offer(item, target)` composed macro |

`pour(liquid, container)` reused from §2 (water-plants verb, extended to beverages).

**Memory + personalization.**

Guest preferences are stored as memory relations:
```
relate(guest_node, "prefers", "green_tea")
relate(guest_node, "allergic_to", "milk")
```

On a returning guest's next visit, the planner can query `query("what does [guest] prefer")`
→ proactively offer the right drink without asking. Every served drink is a trace episode
citing the guest node and drink node.

**Requirements / gaps.**
- **可做**: add `greet`, `take_order`, `offer`, `deliver` to manifest + `MockBody` +
  `SimDeviceAdapter` + `_VERB_TABLE`; `pour` already planned.
- **可复现**: scripted guest + scripted order → deterministic plan.
- **可追溯**: greet, order, prepare, deliver each logged as trace sub-episodes citing
  guest and drink node ids.
- **安全**: hot-liquid handling is robot-internal (robot carries the cup — no safety
  block); **alcohol** is `adult_only` (Phylax blocks serving alcohol to
  child/stranger/untrusted role); allergy gate — if guest has a stored
  `allergic_to` relation and the requested drink contains that allergen, Phylax blocks
  + robot offers an alternative.
- **准确率**: correct drink delivered to correct guest; preference recalled correctly
  on returning guest ⇒ new **serve-accuracy** and **preference-recall** metrics (§6).
- **成功率**: every order fulfilled or gracefully declined (out-of-stock ⇒ honest
  not-available + alternative offered).

**Policy.** Receptionist operates on a `host` role. Proactive offers: one offer per
interaction cycle (anti-spam). Out-of-scope requests (food ordering, errand running)
→ polite decline.

**Baseline scenarios**

| Scenario | Key assertion |
|---|---|
| `serve_tea_on_order` | Guest requests tea → take_order → pour → deliver → cited in trace |
| `serve_with_preference` | Returning guest in memory → robot offers preferred drink proactively |
| `alcohol_blocked` | Child requests wine → Phylax blocks, robot offers juice |
| `allergy_gate` | Guest allergic to milk + orders latte → block + offer dairy-free alternative |
| `refill_proactive` | Guest cup low (or timer) → robot navigates + offers refill unprompted |
| `out_of_stock_honest` | Requested drink unavailable → honest decline + alternative offered |

---

## 5c. Scene Semantics — Static + Dynamic Understanding (cross-cutting)

All five task families require the robot to **ground its reasoning in the current and
recent state of the world**. A tour stop it cannot narrate accurately, a room it
cleans before a guest leaves, a drink served to the wrong person — all stem from
inadequate scene understanding. This section specifies the joint static + dynamic
semantic model required and the memory-system interfaces it demands.

---

### 5c.1 Static Scene Semantics

Static semantics describe **what exists and how things relate** — the invariants or
slow-changing facts that form the backdrop of every task.

**Required semantic dimensions**

| Dimension | Examples | Needed by |
|---|---|---|
| Object identity & category | `cup #12 : DrinkingVessel`, `table #3 : Surface` | all families |
| Spatial location | region membership, position in world frame | all |
| Object state | `open/closed`, `full/empty`, `clean/dirty`, `present/absent` | chores, cleaner, receptionist |
| Material / hazard tags | `fragile`, `sharp`, `hot`, `heavy` | chores, cleaner (safety) |
| Relationship edges | `on(cup, table)`, `in(soap, dispenser)`, `near(plant, window)` | chores, find, cleaner |
| Region semantic type | `bathroom`, `kitchen`, `private-office` | tour, cleaner (access policy) |
| Region access policy | `guest_blocked`, `cleaner_scheduled`, `adult_only` | tour (§1.2), cleaner |
| Person identity & role | `guest`, `child`, `owner`, `stranger` | all (Phylax gates) |
| Preference / allergy relations | `prefers(guest_A, "green_tea")`, `allergic_to(guest_A, "milk")` | receptionist |

Static semantics are populated by `add_detections()` / `define_region` / `relate()` at
scene-setup time and remain valid until explicitly updated or decayed.

---

### 5c.2 Dynamic Scene Semantics

Dynamic semantics describe **what is changing** — the events and transitions the robot
must track to stay calibrated during long-duration tasks.

**Event taxonomy**

| Event class | Examples | Produced by | Consumed by |
|---|---|---|---|
| Object-state change | spill detected, door opened, cup now empty | worldsense detections | cleaner (reactive), receptionist (refill) |
| Object-location change | keys moved from sofa to desk | frame delta in tempomem | find (stale invalidation), tour |
| Person-location change | guest entered kitchen, child left room | worldsense person detection | tour (private-room guard), cleaner (defer occupied) |
| Person-activity change | guest sitting idle → guest working | pose + context inference | receptionist (proactive timing), tour (pacing) |
| Hazard event | wet floor, obstacle in path | worldsense / robot self | cleaner (warn_wet_floor), all (safety) |
| Task-triggered state change | robot mopped → floor is wet, robot placed cup → cup full | plan execution log | cleaner (own-state tracking) |

Dynamic semantics require the memory system to record **when** things changed, not just
**that** they exist.

---

### 5c.3 Reasoning Integration (per family)

| Family | Static query | Dynamic query |
|---|---|---|
| **Tour** | `contents(region)` → narration node ids | `current_occupants(region)` → private-room guard at runtime |
| **Chores** | `contents(shelf)` → tidy targets; `on(x, y)` → precondition ordering | `last_changed(region)` → whether surface is already clean |
| **Find** | `last_seen(name)` → region + recency | stale detection age → hedge vs assert |
| **Cleaner** | `access_policy(region)` → schedule; `state(region, "dirty")` → priority | `current_occupants(region)` → defer; reactive events → interrupt itinerary |
| **Receptionist** | `prefers(guest, *)` + `allergic_to(guest, *)` → order validation | `state(cup, "empty")` or timer → proactive refill trigger |

The Brain's planner reads these via `query()` / `answer()` — the same public surface
already used by P1–P5. No new intent type needed; the queries are internal memory reads
routed through the existing Reasoner context.

---

### 5c.4 Memory System (tempomem) Requirements

These are **concrete new interfaces** derived from the above. Grouped by urgency.

#### Tier 1 — Required for §4-§5 baseline scenarios (no LLM, autonomous)

| New interface | Signature | Semantics |
|---|---|---|
| `last_changed(region)` | `→ (age_s, event_type)` | When was this region last modified (object moved in/out, state changed)? Used by cleaner scheduler. |
| `current_occupants(region)` | `→ list[PersonNode]` | Person nodes whose `current_region` attribute == this region. Used by cleaner defer + private-room tour guard at runtime (not just compile time). |
| `state(node, attr)` | `→ value \| None` | Read a named attribute from a node (e.g. `state(cup_12, "fill_level")`, `state(region_3, "dirty")`). |
| `set_state(node, attr, value, ts)` | `→ None` | Write a state attribute, timestamped. Called by plan execution log after each verb that changes world state (mop → wet, pour → full). |
| `add_event(type, location, ts, payload)` | `→ event_id` | Append a semantic event to the event stream (spill, person_entered, object_moved). |
| `query_events(type, region, since_ts)` | `→ list[Event]` | Pull recent events of a given type for reactive planning (cleaner: "any spills since my last sweep?"). |

All six are **read-only or append-only** on existing structures — no schema migration.
`state` / `set_state` add a key-value attribute bag to existing nodes.
`add_event` / `query_events` add a new lightweight events table to the `.smem` SQLite schema.

#### Tier 2 — Required for full dynamic loop (needs active perception, deferred to P4)

| New interface | Semantics | Dependency |
|---|---|---|
| `update_person_location(person, region, ts)` | Moves a person node's `current_region` attribute; feeds `current_occupants`. | worldsense live person detection |
| `activity_tag(person, tag, ts)` | Set lightweight activity label (`idle`, `working`, `eating`) on a person node. | pose estimation / activity recognition (P4) |
| `detect_state_delta(region, since_ts)` | Diff two snapshots of a region's contents: objects added, removed, moved. Feeds proactive cleaner and find stale-invalidation. | worldsense continuous scan (P4) |

#### Tier 3 — Convenience composites (can live in harness, not core)

```python
# Harness-side helpers (assembled from Tier 1 primitives)
def is_region_occupied(mem, region) -> bool:
    return len(mem.current_occupants(region)) > 0

def is_stale(mem, node) -> bool:
    # ratified single-signal criterion: decayed confidence, 0.7 boundary (§3)
    _, _, confidence = mem.last_seen(node.name)
    return confidence < 0.7

def cup_needs_refill(mem, cup_node) -> bool:
    return mem.state(cup_node, "fill_level") in ("empty", "low", None)
```

These are **not tempomem API** — they live in `skillforge/scenario.py` or `mindloop`
side-helpers. Keep the core numpy-only and stateless.

---

### 5c.5 Static + Dynamic Integration Contract

The fundamental contract between worldsense, tempomem, and mindloop for long-duration tasks:

```
worldsense detects          tempomem stores            mindloop reasons
────────────────────────────────────────────────────────────────────────
frame Detections      →  add_detections() / commit()  →  contents(region)
person location       →  update_person_location()     →  current_occupants(region)
object state change   →  set_state(node, attr, val)   →  state(node, attr)
semantic event        →  add_event(type, loc, ts)     →  query_events(type, region, since)
──────────────────────────────────────────────────────────────────────── 
All writes timestamped → decay + recency are first-class → hedging on stale is automatic
```

**Invariant**: every state or event write goes through tempomem with a timestamp. No
robot module maintains its own parallel world-model. The memory is the single source
of truth for scene semantics — static and dynamic alike.

---

### 5c.6 Requirements / Gaps Summary

| Item | Status | Owner |
|---|---|---|
| `last_seen(name)` | planned (§3) | tempomem |
| `define_region`, `contents(region)`, `relate()` | **exists** | tempomem |
| `state(node, attr)` / `set_state(node, attr, val, ts)` | **new — Tier 1** | tempomem |
| `last_changed(region)` | **new — Tier 1** | tempomem |
| `current_occupants(region)` | **new — Tier 1** | tempomem |
| `add_event` / `query_events` | **new — Tier 1** | tempomem (new `events` table in `.smem`) |
| `update_person_location` | new — Tier 2 (deferred P4) | tempomem + worldsense |
| `activity_tag` / `detect_state_delta` | new — Tier 2 (deferred P4) | tempomem + worldsense |
| Harness helpers (`is_region_occupied` etc.) | new — Tier 3 | skillforge / mindloop |

**Baseline testability**: Tier 1 interfaces are fully scriptable (no live perception
needed). `set_state` / `add_event` are called by the test harness to simulate the world
changing; `state` / `query_events` / `current_occupants` are called by the planner.
All deterministic, network-free.

---

## 6. New scoring metrics (harness)

Extend `EvalReport` / `IntegrationReport` (`skillforge/scenario.py`) — same
ok/total shape as the existing four:

| Metric | Definition | Family |
|---|---|---|
| **citation-accuracy** | narration/answer cites exactly the node ids belonging to the spoken region/object | tour, find |
| **localization-accuracy** | reported region == ground-truth region of the object | find |
| **search-success** | object found within K stops, **or** truthful not-found when truly absent | find |
| **cleaning-coverage** | fraction of scheduled regions cleaned in the itinerary run | cleaner |
| **serve-accuracy** | correct drink delivered to correct guest (right item, right person) | receptionist |
| **preference-recall** | returning guest offered stored preferred drink without explicit order | receptionist |

`meets(...)` gains thresholds for these; the go/no-go verdict now covers all five families.

---

## 7. Production-criteria coverage (summary)

| Criterion | Mechanism (new) |
|---|---|
| 可做 | 4+4+4 verbs across families + `last_seen` helper; conformance kit must stay green after each add |
| 可复现 | scripted baseline (network-free) per scenario; fixed scene + planted detections |
| 可追溯 | every narration/placement/search-stop/clean-episode/serve-episode is a trace episode citing node ids |
| 安全可靠 | region-access + person-scoped privacy + allergy gate + wet-floor warning added to Phylax; appliance/sharp/alcohol stay adult-only; fail-closed |
| 准确率高 | citation- + localization- + cleaning-coverage + serve-accuracy + preference-recall metrics; honesty rules (no over-claim on stale) |
| 成功率高 | bounded Replanner recovers slips; truthful not-found + out-of-stock honest decline count as success; per-suite success-rate gate |

---

## 7b. Execution dynamics (cross-cutting — every family)

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
  ESCALATE-stop. Never loop. Scope (ratified): the budget **resets per task** (each
  new `_plan_task` / SubTask sequence starts at 2); there is **no conversation-level
  cap** — asking about a previous task in the same conversation must not starve a
  later task that is genuinely blocked.
- **Safety**: a clarification answer **is an instruction** ⇒ re-vetted by Phylax (a
  stranger can't unlock an adult-only verb via a clarification reply).
- **Don't over-ask**: ask only when genuinely blocked — measured (5b.4).

### D-I: Object-binding ambiguity — fungibility-aware

**Problem.** `_resolve_node_id` (plan.py:244–250) hard-codes `mem.query(mention, k=1)`
— it takes the top-1 match and never sees a second candidate, so the compiler has no
signal to detect ambiguity at all. But not every multi-match is worth an ask: 5
identical napkins asked for by "a napkin" don't need disambiguation — any one works.

**Decision.** `_resolve_node_id` queries `k=3`. Ambiguous **only** when the top
candidates are semantically non-interchangeable:
1. **different labels** close in score (e.g. "cup" matches both a `mug` node and a
   `cup` node near-equally) → ambiguous, ask.
2. **same label but the mention carries a distinguishing qualifier** ("the red cup")
   that multiple candidates still satisfy → ambiguous, ask.

**Fungible — no ask, auto-bind to top-1**: same label **and** the mention carries no
distinguishing qualifier (generic "a napkin" over 5 identical napkins). This is the
common case for consumables/interchangeable items; asking here would be annoying, not helpful.
Quantifier phrasing ("bring me two cups") is a planner-level concern, not a binding-level
one — out of scope here.

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

## 7c. Data & training closed-loop (plan)

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

## 7d. Ratified decisions & review fixes

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

## 7e. Second-pass review — seams · metrics · reproducibility

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
| **allergy-block** | **1.0** (hard — same class as safety, not a soft quality metric; D-G/D-H) |
| planning accuracy | ≥ 0.95 |
| task success rate | ≥ 0.90 |
| citation accuracy | ≥ 0.95 |
| localization accuracy (find) | ≥ 0.90 |
| search success | ≥ 0.85 |
| interrupt-handling accuracy | ≥ 0.95 |
| clarification precision | ≥ 0.90 |
| cleaning-coverage | ≥ 0.90 |
| serve-accuracy | ≥ 0.95 |
| preference-recall | ≥ 0.90 |
| honesty-rate | ≥ 0.95 (as strict as citation-accuracy — overclaiming breaks the no-assert-unverified bar; D-G) |
| handle-rate | ≥ 0.85 (soft — graceful handling when the goal is unreachable; deliberately below task-success; D-G) |
| p95 latency | set from host measurement |

---

## 7f. Design Decisions — Foundation Gaps (Round 3)

Code-grounded decisions resolving the 9 structural issues identified in the third
review pass. Each decision is binding; build order (§8) is updated to reflect them.

---

### D-A: Phylax dual-identity model

**Problem.** `SafetyContext.role` (line 79, `phylax.py`) captures only *who is
requesting*. When the robot acts as cleaner or host it is performing a service role
that authorises region access independently of the requester's role. The two are
orthogonal: a `guest` asking the robot to mop is fine; the robot entering a
`private-office` region while mopping is not — regardless of who asked.

**Decision.** Add a second field to `SafetyContext`:

```python
@dataclass(frozen=True, slots=True)
class SafetyContext:
    role: Role = "stranger"           # requester identity (unchanged)
    robot_service: str | None = None  # NEW: active service role ("cleaner", "host", "guide", None)
    humans_within_1m: bool = False
    supervised: bool = False
```

Add to `Policy`:

```python
# region type → set of robot_service strings that may enter/narrate it
service_permitted_regions: dict[str, frozenset[str]] = field(default_factory=dict)
# e.g. {"private-office": frozenset(), "bathroom": frozenset({"cleaner", "guide"})}
```

Phylax `check()` gains a third loop: for any subtask whose `named_params` (see D-C)
contains a `location` or `region` that resolves to a node with a `region_type`
annotation, verify `robot_service in policy.service_permitted_regions[region_type]`.
The existing `forbidden_node_ids` check is orthogonal and unchanged.

**Requester gate unchanged.** `adult_only_verbs` still keys on `ctx.role` (requester).
`robot_service` only governs region-access and future service-scope gates. They
compose independently.

**Backward compat.** `robot_service=None` → skip region-access check (same as today).
No existing test breaks.

---

### D-L: Universal invariant vs per-role procedure — not either/or, composed

**Problem.** The receptionist's allergy check (§5) needs both a cross-family safety
*invariant* ("never serve a drink whose allergens intersect the guest's known
allergies") and a receptionist-specific *procedure* to make sure the data exists
before the invariant can be checked ("ask a first-time guest about allergies").
Where do family-specific behavioral rules live vs universal Phylax rules? These are
not alternatives to choose between — they compose as producer → enforcer.

**Decision.**
- **Universal invariant (Phylax `Policy`)**: family-agnostic, not keyed by
  `robot_service` — `serve/deliver`-class verbs are blocked if
  `allergens(item) ∩ allergic_to(target) ≠ ∅`. Any current or future serving role
  needs this same invariant; it does not belong to receptionist specifically.
- **Per-role procedure (Episteme `SkillCard`, `category="receptionist"`)**: the
  concrete workflow that gets the invariant's input data ready —
  `preconditions=("guest.allergy_status_known",)`, enforced by the existing
  SkillCard/`vet_card` gating (P2, already built — no new mechanism). A different
  future role (e.g. a room-service role where allergies are captured at check-in)
  would use a different procedure to satisfy the *same* universal invariant.
- **Composition, not classification**: the SkillCard precondition's job is to
  *produce* the data; the Policy invariant's job is to *enforce* using whatever data
  exists. If the SkillCard's ask never happened (any reason — wrong `robot_service`,
  a bug, an interrupted flow), allergy status stays unknown and Policy still blocks —
  fail-closed by default, not "opt out because this isn't a receptionist task."

This generalizes beyond allergies: **any family-specific behavioral rule going
forward is a `SkillCard` (category-scoped by `robot_service`), never a hardcoded
addition to the shared `Policy` class** — Policy stays the universal, family-agnostic
invariant layer.

---

### D-B: Semantic edge and property API (tempomem)

**Problem.** `relate()` (`__init__.py:552`) is a zero-argument geometric inference
call (`near_m`, `on_gap_m`). It writes `near/on/under` edges inferred from spatial
positions. No API exists for typed directed edges (`prefers`, `allergic_to`) or
scalar properties (`dirty`, `fill_level`, `last_cleaned`).

**Decision.** Add two new surface methods to `TempoMem`, **orthogonal to
geometric `relate()`**:

```python
# Typed directed edge (semantic, not geometric)
def add_edge(self, src: int, rel: str, dst: int | str, *, ts: float | None = None) -> int:
    """Write a directed edge src --rel--> dst. Returns edge id. Idempotent on (src,rel,dst)."""

def get_edges(self, node: int | str, *, rel: str | None = None) -> list[tuple[NodeHit, str]]:
    """Directed edges FROM node, optionally filtered by rel type."""

# Scalar property bag on a node (replaces set_state / state from §5c.4)
def set_property(self, node: int | str, key: str, value: object, *, ts: float | None = None) -> None:
    """Write a timestamped key=value property on a node. Overwrites previous value."""

def get_property(self, node: int | str, key: str) -> object | None:
    """Read the current value of a property (None if unset)."""
```

**Schema additions** (two new tables in `.smem`, numpy-only):
- `semantic_edges(id, src_id, rel, dst_id, ts)`  — distinct from geometric `edges`
- `node_properties(node_id, key, value_json, ts)` — append-on-update, latest wins

`relate()` and `related()` remain **unchanged** — geometric inference only.
`add_edge` covers `prefers`, `allergic_to`, `cleaned_by`.
`set_property` covers `fill_level`, `dirty`, `last_cleaned_ts`, `current_region`.

**`current_occupants(region)` from §5c.4** is now: `get_edges` of person nodes
whose `current_region` property == region id. No new query method needed.

---

### D-K: Menu/recipe knowledge base — extensible, provenance-vetted

**Problem.** The receptionist's `allergy_block` gate (now a hard 1.0 threshold, D-G/D-H)
needs to know a drink's ingredients (e.g. "latte contains milk") — but nothing in §5
or D-B sources that mapping. This is static world knowledge (same across every home),
not per-scene perceptual state, so it does not belong in `tempomem`'s scene graph.

**Decision.** New stdlib-only module `mindloop/menu.py`, mirroring bodylink's
`load_manifest` shape exactly (builtin dict fallback + external YAML, lazy PyYAML —
`bodylink/manifest.py:109-160`):

```python
def load_menu(name_or_path: str | Path) -> MenuKB: ...   # builtin dict or owner-supplied YAML
class MenuKB:
    def allergens(self, drink: str) -> frozenset[str]: ...
```

**Extensible, not fixed**: an owner-supplied YAML path extends/overrides the menu with
no code change — same mechanism as a custom body manifest.

**Provenance-vetted, reusing the existing skill-card trust primitive** (not a new
mechanism): each `MenuKB` entry carries `provenance: str = "builtin"`, mirroring
`SkillCard.provenance` (`episteme.py:103`). Phylax's existing `vet_card`-style check
against `Policy.trusted_provenances` (`phylax.py:100`) applies here too.

**Untrusted provenance can only add caution, never remove it.** An unvetted recipe
entry is never treated as "confirmed allergen-free" — Phylax must treat its allergen
set as *unknown* (fail-closed: block or ask, per the guest's stored allergies) rather
than trust an unreviewed recipe to green-light the hard `allergy_block` gate.

---

### D-M: Occupied-room courtesy check ≠ Clarifier (separate budget)

**Problem.** §4's cleaner policy said occupied rooms are handled via the "ask-human
gate" and defer "if budget exceeded" — literally reusing D3's `ASK_HUMAN`/Clarifier
and its ≤2/task ask budget. But a routine cleaning itinerary can legitimately hit 3+
occupied rooms in one task; that would exhaust the ask budget by the 3rd room and
force D3's generic "honest ESCALATE-stop" — not the graceful per-room defer the
cleaner family actually wants.

**Decision.** Occupied-room detection is a courtesy presence-check, not an
instruction-ambiguity clarification — category error to share Clarifier's budget.
Reuse tour's `wait_for_signal()` (§1.1) instead: a timeout-bound listen, no targeted
question, no ask-budget draw. Each room in the itinerary gets its own
`wait_for_signal()` call, independent of any other room's outcome and of the D3 ask
budget entirely.

---

### D-N: Role-bundle-driven E2E — configuration over case scripts

**Problem.** 31 planned baseline scenarios read as if each E2E case needs its own
hand-authored script. Scaled naively (more roles, more homes), per-case authoring
becomes the bottleneck — and hand-written expectations drift from what actually
ships. A robot *role* (岗位) differs from another mostly by **configuration +
policy + skills**, not by code; the test architecture must mirror that.

**Decision.** Three parts:

**1. A role is a config bundle, already all data** — formalize `RoleBundle` as the
unit both production and tests load:

| Bundle piece | Mechanism (exists/planned) |
|---|---|
| verb set | D3 manifest (bodylink, YAML-able) |
| behavioral procedures | per-role `SkillCard`s (D-L, Episteme, provenance-vetted) |
| safety overlays | `Policy` + `robot_service` region rules (D-A/D1) |
| domain knowledge | `MenuKB` etc. (D-K, YAML-extensible) |
| workspace | region annotations (install-time, §1.2) |

An E2E case = **role bundle × scene config × turn list** — the same bundle that
ships is what the suite loads (test-what-you-ship; no parallel hand-coded
expectations to drift).

**2. Three-layer test pyramid — hand-writing capped at the golden set:**
- **L1 invariants (free, every scenario)**: cross-cutting assertions built into
  `ScenarioRunner` itself — every spoken claim cites node ids, safety is
  fail-closed, ask budget ≤ 2, dispatched verbs ⊆ manifest, every turn traced.
  No per-case assertion code, ever.
- **L2 golden set (hand-written, ~31 is the ceiling)**: representative path per
  family + safety-critical exacts (`allergy_gate`, `stove_is_adult_only`) where a
  reviewed, precise expectation is the point.
- **L3 generated breadth (zero hand-writing)**: parametric templates (one
  `tidy_table` template × object-count × seed ⇒ dozens of variants, asserted by
  *properties* — "exactly one grasp+place pair per object" — not literal verb
  tuples), plus **trace replay**: step 6's trace→dataset curation crystallizes
  real runs into regression cases automatically.

**3. VLA skills are below the E2E seam.** L3 E2E validates orchestration — verb
sequences, policy, replan, citations — against MockBody/sim. How well a VLA skill
(GR00T/OpenVLA-class, L2) executes `grasp` is a **separate L2 skill eval**, entered
through the same D3 verb seam; it never leaks skill-internal logic into L3 case
scripts. Real end-to-end success rates come from step 5 (real LLM) and E2E phase 3
(sim body), not from more scripting.

---

### D-O: RoleBundle — package shape, double-key grant, multi-role held / per-task active

**Problem.** D-N formalizes the role bundle but leaves open: how is it packaged and
loaded, who may change roles, and — decisive for a home robot — can one robot hold
several roles at once (one robot does everything, yet some things it must NOT do)?

**Decision.**

**1. Package: one YAML manifest of references, not copies** — `load_role(name_or_path)`
mirroring `load_manifest`/`load_menu` (builtin + owner YAML):

```yaml
role: cleaner
verbs: [navigate, sweep, mop, warn_wet_floor, restock, dispose]  # ⊆ body manifest
skill_cards: [cleaner-first-entry-knock, cleaner-wet-floor]      # Episteme card ids (referenced)
policy_overlay: {...}     # what the role NEEDS (requested permissions)
knowledge: []             # e.g. receptionist points at menu.yaml (D-K)
provenance: builtin       # whole bundle passes the vet_card-style review
```

Cards stay in the Episteme library — the bundle lists ids, so card vetting (D-L) and
knowledge vetting (D-K) apply unchanged; the bundle itself carries `provenance` and
passes the same gate.

**2. Double-key grant.** The bundle declares what the role *needs*; the owner-side
`Policy` declares what the role is *granted*; **effective permission = grant ∩ need**.
A malicious/unvetted bundle claiming "cleaner may enter bedrooms" is inert — the
owner grant never included it. Same shape as D-K's "untrusted can only add caution."

**3. Multi-role held, one active per task (Unix-groups model).** A home robot holds a
**granted role set** (standing authorization, owner-configured: {cleaner, host, guide,
chores}); `robot_service` on `SafetyContext` (D-A) is activated **per task** by routing
the instruction to a matching granted role. No "switch ceremony" on the happy path —
"wipe the table" runs under cleaner, "serve tea" under host.
- **Permissions never union**: only the active role's permissions apply, including in
  nesting (mid-tour spill → a cleaner sub-task runs under cleaner permissions; the
  suspended tour adds nothing).
- **"Things it must NOT do" = three negative layers**: (1) instruction matches no
  granted role → out-of-scope polite decline (Mode C's scope filter, generalized);
  (2) universal Policy invariants bind regardless of role (D-L); (3) per-role narrowing
  in the grant (owner grants cleaner but denylists the bedroom — the ∩ handles it).
- **Explicit role-set changes** (granting/revoking a role, venue-style shift change)
  remain privileged: owner/adult only, task-boundary only, zero permission inheritance
  across the change, and **no self-escalation** — a role change is never a replan
  action and never accepted via a Clarifier answer; a guest cannot talk the robot into
  a role ("you're the cleaner now — go clean the bedroom" → Phylax refuses).

---

### D-P: L2 skill (VLA) eval track + advisory score feedback into L3

**Problem.** D-N pushes VLA skill quality out of L3 E2E — so where is it measured,
and should skill scores influence L3 planning?

**Decision.**

**1. Eval unit = `(verb × body_profile × condition bucket)`** — e.g.
`grasp@g1d@fragile` vs `grasp@g1d@rigid` each get their own success-rate/latency/
safety-incident curve. Granularity matches the D3 seam; a whole-model score is useless.

**2. Two data sources, one skill scorecard:**
- **Sim batch eval (pre-deploy gate)**: dispatch `SubTask`→`StatusUpdate` through the
  same seam against Genesis with randomized scenes (pose/clutter/lighting) — D-N's
  property-based approach, one level down. Cheap, nightly.
- **Production traces (live telemetry)**: `TraceStore` already records every dispatch
  outcome with typed errors — **zero new instrumentation**; aggregate for real-world rates.
- **Promotion gate reuses `gate.py` discipline**: a new skill/VLA version must
  *strictly improve* on held-out sim scenes before it ships to a body. The conformance
  kit checks the *contract*; the skill eval checks *competence*.

**3. Advisory feedback into L3 — never touching safety:**
- **Landing spot = manifest verb annotation**: `VerbSpec` gains optional
  `reliability` (per condition bucket). The planner context already carries manifest
  verbs, so low-reliability verbs naturally shape plans (alternate route, or a
  preemptive disclosure — "my fragile-grasp success is ~60%, try anyway?" — which
  also earns honesty per D-G).
- **Replanner priors**: recovery-param choice can prefer historically-successful
  adjustments for that condition bucket.
- **Disclosure is configurable** (owner-set via the L5 preference overlay /
  `PreferenceStore`): threshold + verbosity (always / below-threshold / off) — some
  households find a self-deprecating robot chatty. Exception: when the low-confidence
  action is safety-relevant (hot liquid near a person, fragile+heavy overhead), the
  disclosure/consent path is Phylax territory and cannot be configured off.
- **Two guards**: ① scores bias planning *preferences* only — safety gates ignore
  scores entirely (a high score never skips Phylax; a low score never exempts);
  ② no self-fulfilling avoidance (never-tried → no data → forever-low): exploration
  happens **in sim only**, never on real bodies in a user's home.

**4. Where scores live**: not in tempomem (operational body-side data, not scene
memory) — a scorecard store on the bodylink/skillforge side, surfaced to the Brain
at init via the manifest annotation.

---

### D-Q: L3 template property vocabulary — generator-as-oracle, 8 closed properties

**Problem.** D-N's L3 layer generates scenarios with no hand-written expectations —
so assertions must come from mechanically checkable *properties*. What is the
property vocabulary, and where does ground truth come from?

**Decision.**

**1. The generator is the oracle.** A template *plants* the objects/regions/roles it
generates, so ground truth is known by construction (keys planted in the sofa region
⇒ the answer must name the sofa region). Assertions compare generator-known truth vs
system behavior — zero hand labeling.

**2. Initial property vocabulary: 8, closed (YAGNI — grow only when a template needs one):**

| Property | Semantics | Serves |
|---|---|---|
| `per_object(filter, pattern)` | each matching object gets exactly one verb pattern (one grasp+place pair per object) | tidy variants |
| `ordered(a ≺ b)` | precondition ordering holds (open ≺ place ≺ operate) | appliance chains |
| `terminal(status)` | task reaches SUCCESS / handled | all |
| `bounded(n, K)` | counts bounded (search ≤ K stops, replans ≤ caps) | find / replan |
| `cited ⊆ truth` | cited node ids ⊆ generator-planted truth ids | tour / Q&A |
| `blocked(combo)` | generated forbidden combos always blocked (child × stove, across variants) | safety |
| `located == planted` | reported region == planted region | find |
| `effects_written` | every SUCCESS subtask's effects landed in WorldState | all |

Properties are plain functions `(Scenario, RunArtifacts) -> ok/total` feeding the
**same `EvalReport` metrics** — template-generated cases count into the same
`required_metrics` denominators (hardening D-F: denominators are harder to zero out).

**3. Two disciplines:**
- **Seed = reproducibility**: template + seed is fully deterministic; the report
  records seeds, and any failure replays standalone via `--seed N` (可复现 extends
  to the generated layer).
- **L1 invariants come free**: generated cases inherit every L1 check (citations /
  fail-closed / budget) automatically; the vocabulary covers only template-specific
  assertions, no duplication.

**Landing spot**: skillforge `templates.py` (build-order step 4).

---

### D-C: Multi-parameter verb compiler + named params

**Problem.** The compiler (plan.py:291–303) resolves all `cmd.args` to node ids
in a flat tuple (`target_node_ids`) and uses only `cmd.args[0]` as `target_str`
for pre/eff template substitution. `pour(liquid, container)`,
`place(target, location)`, `offer(item, person)` each need named parameters so
that Phylax can inspect the *right* argument (e.g. the `location` parameter for
region-access, not the `target`).

**Decision.** Extend `_VERB_TABLE` entries with `params_map: list[str]` — the
semantic name for each positional arg. The compiler builds a `named_params` dict
and stores it on `SubTask`:

```python
# _VERB_TABLE example entries
"pour":    {"params_map": ["liquid", "container"], "pre": [...], "eff": [...]},
"place":   {"params_map": ["target", "location"],  "pre": [...], "eff": ["{target} at {location}"]},
"offer":   {"params_map": ["item", "recipient"],   "pre": [...], "eff": [...]},
"deliver": {"params_map": ["item", "recipient"],   "pre": [...], "eff": [...]},  # macro: see D-D
"restock": {"params_map": ["item", "location"],    "pre": [...], "eff": [...]},
```

`SubTask` gains `named_params: dict[str, int | str]` (frozen, slots):

```python
@dataclass(frozen=True, slots=True)
class SubTask:
    ...
    named_params: dict[str, int | str] = field(default_factory=dict)  # NEW
```

Pre/eff templates support all named keys: `{target}`, `{location}`, `{liquid}`,
`{container}`, `{item}`, `{recipient}` — `{target}` remains the `params_map[0]`
default for backward compat with existing single-arg verbs.

Phylax `check()` reads `st.named_params.get("location")` or `"region"` to look up
the region type for D-A's service-access gate. No other Phylax change needed.

---

### D-D: Macro expansion — two-pass compile

**Problem.** `deliver`, `sweep(region)`, and `clean_region/clean_spot` blur the
atomic/composite boundary. If macros are single subtasks, trace hides sub-steps
and Phylax checks the macro verb rather than its expanded steps. If macros expand
to multiple subtasks, the expansion layer must be explicit.

**Decision.** Compile pipeline is now **two passes**:

```
Pass 0 — macro expansion (new):
  deliver(item, target)   → [navigate(target), offer(item, target)]
  sweep(region)           → [navigate(region), vacuum(region)]   # or broom(region)
  mop(region)             → [warn_wet_floor(region), navigate(region), mop_floor(region), warn_wet_floor(region)]
  clean_region is removed from plan shapes — LLM emits sweep/mop directly

Pass 1 — node binding (existing):
  bind args to node ids, build SubTask with named_params

Pass 2 — Phylax (existing + D-A/D-C extensions):
  check the expanded subtasks, not the original macros
```

Expanded subtasks carry `macro_parent: str | None` for trace nesting (parent
episode = the macro call; children = the atomic steps). `TraceStore` records both.

`deliver` and `sweep` remain in the manifest as **planner-facing verbs** (the LLM
emits them); they are never dispatched to `bodylink`. Only the expanded atomics
are dispatched. Manifest `supported` check runs on the *expanded* step.

---

### D-E: Interrupt granularity — between-step only (baseline)

**Problem.** §1.3 and §7b say "interrupt anytime". `_drain()` (brain.py:352–353)
blocks on the executor stream until terminal — there is no mid-step preemption
point. True "anytime" interrupt requires `bodylink cancel/pause/resume`.

**Decision.** Baseline interrupt precision is **between steps** (after `_drain()`
returns). The `InterruptSource` inbox is checked *before* the next `_drain()` call.
Documentation (§1.3, §7b) is amended to say "between-step precision".

Real mid-step preemption (mid-navigation, mid-pour) requires bodylink
cancel/pause/resume handshake — **deferred to P4** alongside voice barge-in.
Baseline coverage: any barge-in that arrives during a step is *queued* and handled
at the next step boundary; step-in-progress completes first (≤ `timeout_s`).

This is safe for tour/cleaner/receptionist baseline scenarios: steps are short
(navigate to stop, present, offer). The deferred case (interrupting a 30-second
floor-mop mid-stroke) is a P4 concern.

---

### D-F: Eval minimum denominator

**Problem.** `_rate(ok, total)` returns `1.0` when `total=0` (eval.py:117).
A suite that fails to exercise citation-accuracy, allergy-gate, or preference-recall
passes those metrics vacuously at 1.0.

**Decision.** Each suite config declares `required_metrics: frozenset[str]` — the
metric names that *must* have `total > 0` after the suite runs. If any required
metric has `total == 0`, the suite result includes a `coverage_gap` failure list
and `meets()` returns `False` regardless of thresholds.

`_rate()` itself is **unchanged** (callers outside suites may legitimately have
total=0). The enforcement is at `IntegrationReport.meets()`:

```python
def meets(self, thresholds: EvalThresholds, required: frozenset[str] | None = None) -> bool:
    if required:
        gaps = [m for m in required if getattr(self, f"{m}_total", 0) == 0]
        if gaps:
            return False   # coverage gap — not vacuous pass
    # ... existing threshold checks ...
```

Required metrics per suite:
- `tour_suite`: `citation_accuracy`
- `find_suite`: `localization_accuracy`, `search_success`, `honesty_rate` (exercised by the
  stale-hedge scenario — a suite that never triggers a hedge must not vacuously pass D-G's
  honesty bar)
- `receptionist_suite`: `serve_accuracy`, `allergy_block` (new binary metric)
- `cleaner_suite`: `cleaning_coverage`
- `execution_dynamics` suite: `interrupt_handling_accuracy`, `clarification_precision`
  (these two metrics exist *only* for this suite — omitting them from `required_metrics`
  is exactly the vacuous-pass bug this decision exists to close)

---

### D-G: Task-success taxonomy

**Problem.** "Truthful not-found counts as success" and "out-of-stock honest decline
counts as success" (§3, §5) conflate *task goal success* with *graceful handling*.
In the ENPIRE reward, this trains conservative answers over task completion.

**Decision.** Three outcome categories, tracked separately:

| Category | Definition | Feeds |
|---|---|---|
| `task_success` | Goal achieved: object found + located/delivered; drink delivered; region cleaned | primary success-rate metric |
| `handled_success` | Situation handled correctly when task goal unachievable: honest not-found, safety block + alternative offered | separate `handle_rate` metric |
| `honesty` | No false/overclaimed assertions; stale observations hedged | `honesty_rate` metric |

ENPIRE reward = `w_task * task_success + w_handle * handled_success + w_honesty * honesty`
where `w_task > w_handle > w_honesty`. Default: `0.6 / 0.25 / 0.15`.

`meets()` gates on `task_success ≥ threshold` (not handled_success). The truthful-not-found
baseline scenario is labeled `handled_success=1, task_success=0` — it tests the honesty
mechanism, not task competence.

---

### D-H: Scope count correction

**Problem.** §0 "Net new" table says "4 verbs, 1 helper, 3 metrics, 3 suites" —
written before §4–§5c were added.

**Decision.** Update §0 table (done below in §0). Current accurate count:

| Item | Count |
|---|---|
| New verbs (atomic) | 13: `present, wipe, pour, dispose, sweep, vacuum, mop, warn_wet_floor, restock, greet, take_order, offer, deliver` (deliver is macro-only, 12 dispatched) |
| Macro verbs (expand only) | 1: `deliver` (+ `sweep`, `mop` expand internally but are also dispatched as atomic bodies post-expansion) |
| New memory methods | 6 Tier-1: `add_edge, get_edges, set_property, get_property, last_changed, add_event / query_events` |
| New memory methods (deferred P4) | 3 Tier-2: `update_person_location, activity_tag, detect_state_delta` |
| New metrics | 9: citation, localization, search, cleaning-coverage, serve-accuracy, preference-recall, handle-rate, honesty-rate, allergy-block |
| New suites | 6: tour, chores, find, cleaner, receptionist, execution-dynamics |
| Phylax extensions | 4: `robot_service` field, service-region gate, named-param inspection, menu-provenance vetting (D-K) |
| tempomem schema | +2 tables: `semantic_edges`, `node_properties` |
| New static-knowledge module | 1: `mindloop/menu.py` (`MenuKB`, extensible + provenance-vetted — D-K) |

---

### D-J: Multi-object tidy — compile-time expansion, lazy binding, per-step re-vet

**Problem.** "Tidy the table" over N objects needs N `grasp→place` subtask pairs.
Two failure modes to avoid: (1) heavy replanning blast radius if a mid-batch scene
change (object #7 moved) forces re-verifying the whole batch instead of just that
step; (2) over-trusting plan-time accuracy — binding all N node ids far ahead of
dispatch risks stale bindings by the time step 8 executes.

**Decision.** Three parts, all reusing existing mechanisms rather than inventing new
batch-level machinery:
1. **Compile-time step-list expansion**: the compiler expands "tidy region X" into N
   independent `grasp→place` subtask pairs (deterministic given the region's contents
   at compile time — testable with `ScriptedPlanner` + a planted N-object scene).
2. **Lazy per-step node binding**: only the id for the *current* step's object is
   resolved right before its dispatch, not all N up front. Reuses the existing
   dynamic-scene idempotent-dispatch + active-perception tail re-plan (✅ already
   built, dynamic-scene P1–4) instead of a new staleness model.
3. **Per-step Phylax re-vet**: each step is safety-checked against the scene state
   *at that step*, not once for the whole batch upfront — a scene/occupancy change
   mid-batch (step 8) is caught, not silently skipped because step 1's check already passed.

Net effect: a scene change on object #7 triggers P4's existing bounded per-subtask
replan (RETRY/ADJUST/REROUTE/SKIP/ESCALATE) for step 7 only — steps 1–6 (done) and
8–N (not yet reached) are untouched. Batch size does not enlarge replan blast radius.

---

## 8. Build order (when greenlit)

> Live status: [DEV-STATUS.md](DEV-STATUS.md). Markers: ✅ done · ◐ partial · ▢ not started.
>
> **PLANNING FROZEN (2026-07-02).** 17 D-decisions is saturation. From here, new design
> questions are **build-time decisions** (decided in code/PR, logged one-line in
> DEV-STATUS) unless safety-critical — only those reopen this document.
> Execution runs in tranches **T1–T4** (see DEV-STATUS §2): T1 = step 1 + step-2
> verification · T2 = step 3 then 3b (separate commits) · T3 = step 4a then 4b →
> baseline go/no-go · T4 = step 5 ∥ sim body.

0. ✅ **Plan** — this doc. ✅
1. ✅ **Verbs (bodylink + mindloop)** *(done 2026-07-02: 13 verbs in manifest+arm subset, _VERB_TABLE entries, place@location eff)* — add `present, wipe, pour, dispose` (§1-3) +
   `sweep, mop, warn_wet_floor, restock` (§4) + `greet, take_order, offer, deliver` (§5)
   to manifest + `MockBody` + `SimDeviceAdapter` (conformance green) **and** `_VERB_TABLE`
   entries (`pre`/`eff`/`skill`) in `mindloop/plan.py` (review fix A); extend `place`
   effect to encode the region (fix B). *No LLM.*
2. ✅ **Memory (tempomem)** *(done 2026-07-02: Tier-1 semantic layer + `last_seen` landed with tests; `last_changed` verified; `current_occupants` = D-B composition, no method needed)* — add `last_seen(name)` (§3) + Tier-1 scene-semantics interfaces
   (§5c.4): `state`/`set_state` (node attribute bag), `last_changed(region)`,
   `current_occupants(region)`, `add_event`/`query_events` (new `events` table in `.smem`).
   Region helpers already exist. All numpy-only, no network. *No LLM.*
3. ✅ **Safety (mindloop/Phylax)** *(done 2026-07-02: named_params, D1 param gate, D-A robot_service, Q6 region defaults, D-K menu.py + allergen invariant — 18 tests)* — region-access + person-scoped privacy dimensions +
   **param-scoped gating** `(verb, param)` for stove/sharp (D1). Region-access keys on the
   **existing** `Role {adult,child,guest,stranger}` (already in `phylax.py`) — no new trust
   enum. *No LLM.*
3b. ✅ **Execution dynamics (mindloop)** *(done 2026-07-02, 3 TDD slices: InterruptSource+BargeClassifier · between-step barge handling · Clarifier+ask-budget+ESCALATE routing — 19 tests)* — preemptible dispatch stepper + resume cursor +
   `InterruptSource` + `BargeClassifier` (D2); brain-level `Clarifier` seam (D3) with
   `ReplanAction.ASK_HUMAN` as one entry + ask budget; route dead-end ESCALATE →
   Clarifier when reachable. Re-vet clarifications via Phylax. *No LLM.*
   **Risk discipline (review pt 2)**: this refactors `Brain._dispatch_plan` — the core
   under all 109 existing mindloop tests. **TDD-first, own commit(s), never mixed with
   step 3**; the existing suite must stay green after every slice.
4a. ✅ **Harness — suites + metrics (skillforge)** *(done 2026-07-02: 11 family metrics on EvalReport/Thresholds, required_metrics (D-F), L1 invariants in the runner (D-N), six suites GO at 1.0 vs §7e)*
   — `Scenario.regions` + `define_region` in `_build_memory` (K); extend
   `EvalReport`/`EvalThresholds` with all new metric fields (J) + `required_metrics`
   (D-F); L1 invariant checks built into `ScenarioRunner` (D-N); 5 new suites
   (`tour_suite`, `chores_suite`, `find_suite`, `cleaner_suite`, `receptionist_suite`) +
   an `execution_dynamics` suite (text barge-in / fail-ask / ask-budget); baseline
   go/no-go against the §7e thresholds. *No LLM, autonomous.*
4b. ✅ **Harness — RoleBundle + templates (skillforge)** *(done 2026-07-02: load_role + double-key + vet_role in mindloop; templates.py generator-as-oracle, 19 seeded variants GO)* — `load_role` bundle loading +
   double-key grant (D-O); `templates.py` parametric generators + the 8-property
   vocabulary, seeds recorded (D-Q). Extends 4a's go/no-go with generated breadth.
   *No LLM, autonomous.*
5. ✅ **Real-LLM validation** *(done 2026-07-04: host `172.16.1.12`, Cosmos-Reason2-8B via
   vLLM, `temperature=0` + fixed seed — 4/4 scenarios GO, intent/plan/policy/citation 1.0,
   turn p95 ~0.25 s)* — run the new suites on the GPU host for real accuracy/success
   numbers, pinned greedy + seeded (reproducible — L).
6. ✅ **Data & training closed-loop (skillforge)** *(done 2026-07-04: curate — home-scoped,
   speech-scrubbed; `LLMPolicyAuthor`; crystallize → learned SkillCard, no safety keys;
   `gate.py` promote gate; learn→reuse validated live on the host. Deepening done same
   day: D-G composite reward `Weights` 0.6/0.25/0.15 + `IntegrationReport.composite_score`)*
   — see FLOWS Diagram 5.
7. ◐ **Step 7 — software face done (2026-07-04)**: voice-narrated tour via `VoiceLoop`
   (`skillforge/examples/voice_tour.py`, GO) · `ListenerInterruptSource` voice barge-in
   seam (P7.3) · P7.4 degraded mode (per-turn mode telemetry, offline policy tighten,
   honest offline UX) · D-I binding ambiguity · D-D macro expansion · D-P scorecard +
   advisory reliability. **Remaining (hardware)**: on-body streaming ASR+VAD fill of
   `audio_source`, live-camera perception feeds (dynamic-scene P4). Mid-step preemption
   (bodylink cancel/pause/resume) is reclassified as software — see DEV-STATUS T5.

Steps 1–4 are autonomously buildable and network-free. Step 5 alone needs the host.
