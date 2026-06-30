# Flows — Scenario · Full Pipeline · Key Components · Data/Training Loop

> Canonical flow diagrams for the Chronotope embodied-brain stack as it serves our
> household-robot scenario. Mermaid renders on GitHub. Companion to
> [INTEGRATION-E2E.md](INTEGRATION-E2E.md) (production capstone) and
> [TASK-FAMILIES.md](TASK-FAMILIES.md) (task families + execution dynamics).
> The data/training closed-loop (Diagram 5) is the plan for the next phase.
>
> **Each diagram is committed as a standalone SVG under [`../assets/`](../assets/)
> (renders on GitHub, light + dark) with its editable mermaid source kept beside it
> in a `<details>` block — when you change a diagram, update BOTH the mermaid and the SVG.**

---

## 1. Component map (who owns what, data direction)

![Component map](../assets/flow-component-map.svg)

<details><summary>mermaid source — update the SVG when you edit this</summary>

```mermaid
flowchart LR
  CAM([RGB-D camera]) --> WS
  MIC([mic]) --> VL
  subgraph PERCEPTION
    WS[worldsense<br/>eyes: RGB-D to world Detections]
  end
  subgraph MEMORY
    TM[tempomem<br/>.smem scene-graph: fuse to persist to query<br/>regions · history/ts · decay]
  end
  subgraph BRAIN
    ML[mindloop<br/>route to plan to compile to safety to dispatch to replan to trace]
  end
  subgraph SEAMS
    BL[bodylink<br/>executor: MockBody/Sim/real · D3 manifest]
    VL[voicelink<br/>ASR ears + TTS mouth]
  end
  subgraph LAB
    SF[skillforge<br/>ENPIRE self-learning · imports all]
  end
  WS -- Detections --> TM
  TM -- serialized scene --> ML
  ML -- SubTask --> BL
  ML <-- Listener/Speaker --> VL
  BL -- StatusUpdate --> ML
  ML -- episodes --> TR[(TraceStore)]
  SF -. drives .-> TM & ML & BL & WS
  TR -. rollouts/eval .-> SF
```

</details>

Dependency direction (never inverted): `worldsense→core`, `mindloop→core`,
`bodylink→mindloop`, `voicelink→mindloop`, `skillforge→tempomem+mindloop+bodylink`.
The core (`tempomem`) imports none of the others — numpy-only contract.

---

## 2. Request lifecycle (the brain spine, one utterance)

![Request lifecycle](../assets/flow-request-lifecycle.svg)

<details><summary>mermaid source — update the SVG when you edit this</summary>

```mermaid
flowchart TD
  U([utterance + person + role]) --> R{IntentRouter<br/>classify}
  R -- chat --> CH[smalltalk reply] --> SPK
  R -- question --> Q[memory query<br/>cite node ids] --> SPK[Speaker: speak]
  R -- task --> P[Planner LLM<br/>compact verb sequence]
  P --> C[compile: fill SubTask · bind objects to node ids B9 · D3 manifest gate]
  C --> L[L5 preference overlay<br/>manifest-gated]
  L --> PH{Phylax safety<br/>role · region-access · privacy}
  PH -- block --> STOP[refuse: stop + speak] 
  PH -- clear --> D[[preemptible dispatch loop<br/>see Diagram 3]]
  D --> TR[(TraceStore: episodes cite node ids)]
  STOP --> TR
  SPK --> TR
```

</details>

Two-stage planning is an invariant: **LLM emits text verbs → deterministic compile**
binds them to memory node ids and gates each verb on the D3 manifest. No online
rule-planning fallback.

---

## 3. Execution dynamics (dispatch loop: barge-in · replan · ask-human)

![Execution dynamics state machine](../assets/flow-execution-dynamics.svg)

<details><summary>mermaid source — update the SVG when you edit this</summary>

```mermaid
stateDiagram-v2
  [*] --> NextStep
  NextStep --> CheckInterrupt: subtasks remain
  NextStep --> Done: plan exhausted

  CheckInterrupt --> Classify: utterance in inbox
  CheckInterrupt --> Dispatch: inbox empty
  Classify --> Answer: chitchat/question
  Answer --> CheckInterrupt: resume (cursor kept)
  Classify --> Replan_New: new instruction (supersede)
  Replan_New --> NextStep: ABORTED old, plan new
  Classify --> Aborted: stop/cancel
  Classify --> Replan_Fix: correction

  Dispatch --> NextStep: SUCCESS
  Dispatch --> Recover: FAILED (typed err)
  Recover --> Dispatch: RETRY / ADJUST / REROUTE
  Recover --> NextStep: SKIP
  Recover --> Ask: no hint but reachable
  Recover --> Escalate: unrecoverable / cap hit

  Ask --> Resolve: Speaker asks, Listener answers (re-vet via Phylax)
  Resolve --> Dispatch: answer resolves, budget--
  Resolve --> Escalate: ask budget exhausted

  Escalate --> Done: honest stop + speak
  Aborted --> Done
  Done --> [*]
```

</details>

Guards: irreversible step (stove on) finishes-or-safe-aborts, never hard-killed
mid-action; supersede confirms when the current task is near-done; clarification
answers are re-vetted by Phylax (Diagram 2); ask budget ≤2/task.

---

## 4. Task-family flows (compact)

![Task-family flows](../assets/flow-task-families.svg)

<details><summary>mermaid source — update the SVG when you edit this</summary>

```mermaid
flowchart LR
  subgraph TOUR[Tour / Guide]
    direction TB
    t0([show guest around]) --> t1[plan: navigate→present per region]
    t1 --> t2{region private?}
    t2 -- yes & guest --> t3[skip + reason]
    t2 -- no --> t4[present: narrate contents, cite ids]
    t4 --> t1
  end
  subgraph CHORES[Household chores]
    direction TB
    c0([tidy / wash / wipe / water / trash]) --> c1[plan: ordered multi-step, multi-object]
    c1 --> c2{adult-only verb?}
    c2 -- child --> c3[block]
    c2 -- ok --> c4[open→place→operate / grasp→place region / wipe / pour / dispose]
  end
  subgraph FIND[Find lost object]
    direction TB
    f0([where are my keys?]) --> f1{last_seen known & recent?}
    f1 -- yes --> f2[answer region+recency, cite id]
    f1 -- stale --> f3[hedge: seen 3h ago, may have moved]
    f1 -- unknown --> f4[active search: navigate→detect, bounded K]
    f4 --> f5{found?}
    f5 -- yes --> f2
    f5 -- no --> f6[truthful not-found = success]
  end
```

</details>

Cross-cutting: every spoken claim cites node ids; stranger asking for owner's items
is privacy-blocked; a non-owner tour skips private regions.

---

## 5. Data & training closed-loop (next-phase plan)

The runtime is already instrumented (every decision is a `TraceStore` episode citing
node ids). The closed loop turns that exhaust into training signal via skillforge.

![Data and training closed loop](../assets/flow-data-training-loop.svg)

<details><summary>mermaid source — update the SVG when you edit this</summary>

```mermaid
flowchart TD
  subgraph RUNTIME[Runtime — production]
    BR[mindloop Brain spine<br/>Diagrams 2-3] --> EP[(TraceStore<br/>episodes, cited)]
  end
  EP --> DS[dataset curation<br/>traces → labeled cases:<br/>intent · plan · safety · outcome · clarifications]
  subgraph SKILLFORGE[skillforge — ENPIRE lab]
    DS --> ENV[Environment<br/>scene + goal replays]
    AU[PolicyAuthor<br/>scripted now → LLM next] --> RO
    ENV --> RO[Lab.rollout<br/>RolloutLog · AttemptTree]
    RO --> RW[Reward<br/>success · safety · steps · honesty]
    RW --> EV[Evolution<br/>EvolutionResult: best policy/skill]
    EV --> CR[crystallize<br/>skill → Episteme store]
    EV -.refine.-> AU
  end
  CR --> GATE{eval harness<br/>run_eval · IntegrationReport.meets}
  GATE -- pass --> PROMOTE[promote policy/skill<br/>into Brain planner/overlay]
  GATE -- fail --> SKILLFORGE
  PROMOTE --> BR
  HOST[(host LLM<br/>Cosmos+Qwen)] -. real rollouts/labels .-> AU & DS
```

</details>

**Loop stages → real symbols (skillforge):** `Lab(env, author)` drives
`Environment` replays with a `PolicyAuthor` (today `ScriptedAuthor`, next an LLM
author on the host) → `RolloutLog` / `AttemptTree` → `Reward` → `EvolutionResult` →
crystallize skill into an Episteme store → `run_eval` / `IntegrationReport.meets`
go/no-go gate → promote into the live `Brain`. Closing the loop is what makes the
robot self-improve on our scenarios; the metrics (§4 of TASK-FAMILIES) are the gate.

**What's built vs planned:** runtime tracing ✅, eval harness ✅, ENPIRE walking
skeleton (`v0.1.0a0`, network-free, ScriptedAuthor) ✅. Planned: dataset curation
from real traces, LLM PolicyAuthor on host, Episteme crystallization, and the
promote-back gate. See TASK-FAMILIES build order step 7.
