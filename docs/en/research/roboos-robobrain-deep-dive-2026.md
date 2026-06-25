> 🌐 **English** · [中文](../../zh/research/roboos-robobrain-deep-dive-2026.md)

# RoboOS & RoboBrain (BAAI/FlagOpen) · Dedicated Deep-Dive (2026-06-10)

> Two parallel research agents (web + GitHub + code reading of both RoboOS branches), follow-up
> verification of the two monitoring triggers left by the Round-2 gaps probe
> ([embodied-brain-gaps-probe-2026.md](embodied-brain-gaps-probe-2026.md) §2.4).
> All claims carry source URLs; per-claim caveats are stated inline.

---

## 0. Executive summary

1. **Both monitoring triggers from the gaps probe were re-checked on 2026-06-10 and remain green
   (no action needed): the "complementary, not covered" verdict holds.**
   - **RoboOS-NeXT / STEM code is still not open-sourced** (issue [#73](https://github.com/FlagOpen/RoboOS/issues/73)
     open, no team response).
   - **RoboOS shared memory is still Redis in-memory** — worse: the shipped 2.0 config has
     `clear: true` → **`FLUSHDB` on every master start**. No move to persistent storage.
2. **The paper–code gap is the defining fact about RoboOS.** The paper describes a hierarchical
   dynamic scene graph (SAM+CLIP, RGB-D, incremental update, RAG retrieval, TB-scale memory engine);
   the shipped code is a **flat Redis hash `{name: {type, contains:[str]}}`** with no coordinates,
   no frames, no timestamps, no confidence, no persistence. Community issue
   [#76 "About Scene Graph"](https://github.com/FlagOpen/RoboOS/issues/76) asking where the scene
   graph is remains unanswered — **unmet demand for exactly what `.smem` is**.
3. **RoboOS is decaying; RoboBrain is thriving.** RoboOS: 571★, zero releases/tags/CI/tests, last
   push 2025-12-18, full 2.0 SaaS never open-sourced. RoboBrain: 2.5-8B (2026-01) and 2.5-4B
   (2026-03) on Qwen3-VL arch, active through 2026-03, 1,094★. BAAI's effort visibly moved into
   the model.
4. **RoboBrain 2.x is a near-zero-cost candidate reasoner for `mindloop`** — stock
   Qwen2.5-VL / Qwen3-VL checkpoints, `vllm serve` gives the same OpenAI-compatible endpoint
   `CosmosReasonVerbalizer` already targets; swap = `base_url` + model name. Best play is
   **complement, not replace**: keep Cosmos-Reason2 for QA/verbalization, add RoboBrain 2.5 as a
   *spatial-output head* (pointing, free-space placement, 3D traces, metric clearance, GRM progress
   reward).
5. **BAAI's own production architecture validates ours**: external scene-graph store + serialize
   into every prompt + stateless VLM. RoboBrain "scene-graph updating" is a *text-generation task*
   (model emits/revises scene-graph JSON), not built-in storage — persistence is explicitly
   delegated to the OS layer.
6. **Watch item: BAAI Conference 2026 is June 12–13** (embodied forum June 13; topics include world
   model ORCA, "robot universal brain", self-evolution). New RoboBrain/RoboOS announcements are
   plausible days after this report — re-check the triggers after the conference.
   > ⚠️ **Overdue as of 2026-06-25**: the conference has passed; the post-conference trigger sweep
   > (RoboBrain 2.5-32B release, RoboOS-NeXT code, any new memory/scene-graph capability) has **not
   > yet been run**. Treat every "as of 2026-06-10" claim below as ~2 weeks stale until refreshed.

---

## 1. RoboOS

### 1.1 Positioning, versions, maturity

"Universal Embodied Operating System for Cross-Embodied and Multi-Robot Collaboration" — BAAI +
Peking University. Brain–Cerebellum hierarchy: cloud MLLM brain (RoboBrain) + on-robot MCP skill
"cerebellum" + Redis shared memory. Apache-2.0.

| Version | Date | Artifact | Status |
|---|---|---|---|
| RoboOS 1.0 | 2025-04 | `main` branch; [arXiv 2505.03673](https://arxiv.org/abs/2505.03673) | Released; YAML profiles + Redis + Gradio |
| RoboOS 2.0 | announced 2025-06 (BAAI Conf, "Wujie" series) | only lightweight single-machine variant public ([`stand-alone` branch](https://github.com/FlagOpen/RoboOS/tree/stand-alone)) | Full SaaS version **never open-sourced**; [#77](https://github.com/FlagOpen/RoboOS/issues/77) unanswered |
| RoboOS-NeXT | paper 2025-10: [arXiv 2510.26536](https://arxiv.org/abs/2510.26536) | STEM unified memory | **Code unreleased**; [#73](https://github.com/FlagOpen/RoboOS/issues/73) open, no response |

Maturity (via `gh api`, 2026-06-10): **571★ / 85 forks, zero releases, zero tags, no CI, no
tests**, last push 2025-12-18, ~2.6k LOC Python, 12 issues lifetime, community issues/PRs mostly
unanswered since fall 2025. Docker route broken
([#75](https://github.com/FlagOpen/RoboOS/issues/75): Aliyun image 404, pinned FlagScale commit
gone).

### 1.2 Architecture (code-verified, 2.0 `stand-alone`)

```
User → Flask master :5000 → GlobalTaskPlanner: ONE prompt to RoboBrain2.0-7B
       (OpenAI SDK, vllm @ localhost:4567/v1)
       prompt = robot names + tool lists + ENTIRE ENVIRONMENT_INFO Redis hash + task
     → JSON {subtask_list:[{robot_name, subtask, subtask_order}]}
     → same-order subtasks dispatch in parallel waves (Redis pub/sub "roboos_to_{robot}")
     → master blocks on AGENT_BUSY polling (0.5 s) between waves
Robot slaver: register (TTL 60 s + heartbeat 30 s)
     → ToolMatcher (semantic embeddings, max 3 tools) filters MCP tools per subtask
     → ReAct loop: LLM → 1 MCP tool call/step
     → after EVERY tool call: extra LLM call classifies side-effect
       {add_object | remove_object | position} → SceneMemory.apply_action → Redis
```

- Skills are **MCP servers** (stdio local or streamable-HTTP remote), discovered via
  `list_tools()`.
- Communication is entirely Redis, via `Collaborator` from
  [FlagScale](https://github.com/FlagOpen/FlagScale/blob/main/flagscale/agent/collaboration/collaborator.py).
- Planner supports `OpenAI` and `AzureOpenAI` clients → any OpenAI-compatible endpoint works.
- **No master-level re-planning** — `master/agents/agent.py:103` has the literal
  `# TODO: Task result should be refered to the next step determination.` Recovery exists only in
  the slaver's ReAct loop.
- Paper claims (RAG decomposition, subtask graph object, "TB-level memory engine", "<0.001 s
  latency") have **no counterpart in code**: one flat prompt, integer `subtask_order`, busy-flag
  polling.

### 1.3 Memory subsystem — three different "RoboOS memories"

**(a) Shipped code (trivial).** Flat Redis hash `ENVIRONMENT_INFO`: field = location name,
value = `{type, contains:[names]}`, seeded from a YAML scene profile. One-level containment is the
only relation; **no coordinates, frames, timestamps, confidence**. Query interface =
`HGET`/`HGETALL`; the planner does `HGETALL` and **inlines the whole dict into the prompt** — that
is the entire brain↔memory interface. Updates: after every tool call an **extra LLM round-trip**
classifies the side-effect 3-ways; errors are `print()`-ed and swallowed. A single shared
`"robot"` key means **multiple robots clobber each other's position/holding**. `clear: true` →
`FLUSHDB` on master start; no persistence. External PR
[#70](https://github.com/FlagOpen/RoboOS/pull/70) (community `MemoryManager` with short/long-term
split + persistence) left unmerged.

**(b) Paper 1.0/2.0 (aspirational).** "Real-Time Shared Memory" = Spatial (hierarchical
floor/room/object scene graph, position/affordance/label nodes, SAM+CLIP from multi-view RGB-D,
incremental updates) + Temporal (execution history, tool logs) + Robotic (joint states, battery).
**None of this exists in either branch.**

**(c) RoboOS-NeXT STEM (the serious design — unreleased).** `ℳ(t) = (𝒮, 𝒯, ℰ)`:
- **Spatial 𝒮**: Scene Tree (root = 3D recon + 2D SLAM map → region → **carrier** nodes) +
  per-carrier Object Relation Graphs; nodes carry pose/properties/state; edges use **7 predicates
  `{on,in,left,right,front,back,near}`**; Add/Remove/Move trigger **local** relation re-evaluation
  via geometric predicate functions; init via image→3D→SLAM PnP alignment.
- **Temporal 𝒯**: append-only time-ordered log of state deltas + task context + tool traces;
  doubles as the cross-robot sync substrate.
- **Embodiment ℰ**: per-robot heartbeat profiles (localization, skills, battery, availability).
- Ablations: removing spatial memory blows steps 11.6 → 58.1; removing embodiment memory → **SR
  0%**. Stated failure modes include **"noise accumulation in long-horizon memory operations"
  (30.2%)** — exactly the problem a fusion arbiter addresses.

### 1.4 Deployment & demos

Released 2.0 = single machine: one box runs Redis + vLLM (RoboBrain2.0-7B at `:4567/v1`) + master
+ N slavers; robots attach as remote MCP servers. Demos: Unitree G1, Agilex dual-arm, Realman
arm; restaurant/household/supermarket scenarios (~4 receptacles, ~12 objects).

---

## 2. RoboBrain

### 2.1 Lineage (all Apache-2.0)

| Model | Released | Arch / size | Notes |
|---|---|---|---|
| RoboBrain 1.0 | 2025-02 (CVPR 2025) | SigLIP + Qwen2.5-7B (LLaVA-style) | planning ckpt + A-LoRA (affordance) + T-LoRA (trajectory); [arXiv 2502.21257](https://arxiv.org/abs/2502.21257) |
| RoboBrain 2.0 | 2025-06/07 | **Qwen2.5-VL** 3B/7B/32B (+7B-FP8) | [arXiv 2507.02029](https://arxiv.org/abs/2507.02029); repo renamed → [RoboBrain2.5](https://github.com/FlagOpen/RoboBrain2.5) |
| RoboBrain 2.5 | 8B 2026-01, 4B 2026-03 | **Qwen3-VL** | "Depth in Sight, Time in Mind", [arXiv 2601.14352](https://arxiv.org/abs/2601.14352); 32B on TODO, unreleased |
| RoboBrain-X0 | 2025-09 (CoRL) | VLA on 2.0-3B | SE(3) end-effector, unified action vocabulary |
| RoboBrain-Dex / METIS | 2025-12 | VLA | bimanual dexterous; [arXiv 2511.17366](https://arxiv.org/abs/2511.17366) |

No RoboBrain 3.0 as of 2026-06-10. HF download counts are modest (hundreds/30d); repos gated
"auto".

### 2.2 Capabilities

- **2.0**: pointing / spatial referring (pixel coords, incl. **free-space pointing**), affordance
  bbox, trajectory (2D keypoints), grounding, navigation pointing, long-horizon + multi-robot
  planning (subtask DAGs for RoboOS), ego-video temporal reasoning, **scene-graph
  construction/updating as a generated-text task**, thinking mode (`{thinking, answer}`).
- **2.5 upgrades**: `(u,v,depth)` keypoints → 3D via intrinsics; **absolute metric reasoning**
  ("hovering 1–5 cm above"); collision-aware ordered **3D traces**; **GRM dense temporal value
  estimation** (task-progress in [-1,1], success/failure estimation — a real-time reward signal
  for VLA RL).

### 2.3 Training (condensed)

1.0: ShareRobot (1.03M planning QA / 6.5K affordance / 6.9K trajectory from 23 OXE datasets).
2.0: 4.8M foundational → 224K embodied (multi-view, 3D affordance, **scene graphs**) → 195K CoT
SFT → **45K RFT via GRPO** (Reason-RFT). 2.5: ~12.4M total; temporal ~3.5M ≈60% real robot data;
two stages with 15% replay; trained cross-accelerator (NVIDIA + Moore Threads, FlagScale).

### 2.4 Benchmarks (BAAI-run, FlagEvalMM; caveats below)

| Model | BLINK | CV-Bench | EmbSpatial | RoboSpatial | Where2Place | ShareRobot-Afford | Traj-DFD↓ |
|---|---|---|---|---|---|---|---|
| RoboBrain2.0-32B | 83.6 | 83.9 | 78.6 | **72.4** | **73.6** | **35.3** | **0.237** |
| RoboBrain2.0-7B | **84.0** | **85.8** | 76.3 | 54.2 | 63.6 | 28.1 | 0.551 |
| Gemini-2.5-Pro | 81.8 | 84.6 | **78.7** | 59.9 | 42.4 | 10.3 | 0.767 |
| GPT-4o | 77.9 | 78.6 | 71.9 | 44.4 | 20.4 | 6.0 | 0.685 |
| Cosmos-Reason1-7B | 68.6 | 74.7 | 65.2 | 38.8 | 5.5 | 10.0 | 0.852 |

Planning: Multi-Robot-Plan 81.5 (7B) / 80.3 (32B) vs GPT-4o 74.5, Cosmos-Reason1 33.7. 2.5:
2D-spatial avg 75.8 (Gemini 66.1), TraceSpatial 44% (Qwen3-VL 6%).

**Caveats:** all numbers vendor-run; the Cosmos column is **Cosmos-Reason1-7B, not Reason2-8B** —
no public head-to-head with Reason2 exists anywhere as of this date.

### 2.5 Serving

Stock Qwen-VL family → **vLLM/SGLang out of the box**, OpenAI-compatible. BAAI's own eval uses
`vllm --limit-mm-per-prompt image=18 --max-model-len 32768`. VRAM (BF16 ≈ 2×params): 2.5-8B ≈
18–20 GB, 2.0-32B ≈ 70 GB — both fit RTX PRO 6000 96 GB. 3B billed as edge-targeted, FP8 7B
exists, **but no official Jetson/Thor deployment guide anywhere** — Cosmos-Reason2 has first-party
NVIDIA support on Thor, a real ecosystem advantage on our target robot compute.

### 2.6 Statefulness (definitive)

**RoboBrain is stateless per query.** "Scene-graph updating" = the model can *emit/revise
scene-graph JSON in output text* when fed observations (trained task). Persistence lives outside,
in RoboOS Redis; the scene graph is re-serialized into the prompt (`Ms ⊕ Mt ⊕ Sr ⊕ Mr ⊕ T`) on
every brain call. **BAAI's production architecture = external scene-graph store +
serialize-into-prompt + stateless VLM — exactly ours.**

---

## 3. Implications for the Chronotope stack

### 3.1 Where we win outright (vs shipped RoboOS code)

1. **Representation**: world-frame typed nodes/edges + SQLite persistence vs name-string + 1-level
   `contains` in volatile Redis.
2. **Fusion**: detection-level fuse-before-persist arbiter (no LLM in loop) vs one extra LLM call
   per tool execution doing 3-way side-effect classification with swallowed errors. STEM's own
   failure analysis (30.2% = memory noise accumulation) validates the arbiter as the right
   investment.
3. **Query**: layered relational → intent → semantic routing + `#id` citation serialization vs
   `HGETALL`-dump-into-prompt (won't scale past toy scenes).
4. **Perception grounding**: real camera→world lift vs YAML-seeded symbolic world that never
   touches RGB-D in code.

### 3.2 Worth stealing (priority order)

1. **Embodiment memory ℰ** — heartbeat robot profiles (skills/battery/availability) as a
   first-class memory partition; STEM ablation: removing it → 0% SR. Needed the day Brain2Robot
   schedules >1 effector.
2. **Temporal event log** — append-only scene-delta journal in `.smem`; buys lifelong/replay +
   replan context cheaply; also what RoboBrain-class models are trained to consume (`Mt`).
3. **Carrier-scoped relation re-evaluation** — recompute relations locally per carrier, not
   globally; adopt the **7-predicate vocabulary `{on,in,left,right,front,back,near}`** as a
   compatibility target (RoboBrain models are trained against it).
4. **`tempomem` as MCP server** — expose query/answer/commit as MCP tools; drop-in for
   RoboOS-style orchestrators; issues #76/#73 are live demand for an open scene-graph memory
   component.
5. Wave scheduling (`subtask_order` + busy-wait) — trivial to reimplement if fleets ever matter.

### 3.3 Reasoner choice: RoboBrain vs Cosmos-Reason2

- Integration cost ≈ zero (same OpenAI-compatible endpoint; swap = `base_url` + model name in
  `CosmosReasonVerbalizer` config).
- Profiles differ: RoboBrain = **output-grounded** (points/bboxes/3D traces/metric checks/progress
  values); Cosmos-Reason = **CoT-judgment-grounded** (plausibility, QA, planning critique).
- For `Brain.ask` over a serialized scene graph either works; for actionable spatial outputs
  RoboBrain is the only one trained for it; on Thor, Cosmos has first-party support, RoboBrain has
  none documented.
- **Recommendation: complement, not replace.** Second vLLM endpoint + thin adapter = RoboBrain 2.5
  as spatial-output head (pointing, placement, traces, metric clearance, GRM progress) alongside
  Cosmos QA. Also the natural A/B pair for the eval suite.
- **Reconcile with the landscape report:** the landscape doc flags that the *Cosmos-Reason2 repo is
  already unmaintained, superseded by Cosmos 3* — that is about the **repo's update cadence**, not
  the model's usability. The integrated `Cosmos-Reason2-8B` weights still serve QA fine, so "keep
  Cosmos-Reason2" stands; but **do not expect upstream repo updates** — track Cosmos 3 (and
  RoboBrain 2.5) as the successors the eval suite should start A/B-ing against.

### 3.4 Interface guidance extracted from their stack

1. Serialize a **context bundle** (scene ⊕ recent action feedback ⊕ robot state), not scene-only —
   matches what RoboBrain-class models are trained to consume.
2. RoboBrain returns **pixel/camera-frame coordinates** ((x,y); (u,v,d)+intrinsics in 2.5) — keep
   frame/intrinsics metadata with observations so model outputs can be lifted back into
   world-frame nodes.
3. 2.5's absolute-metric reasoning rewards serializing **metric geometry** (world positions,
   sizes, support heights), not just topology.
4. Free-space pointing works from single raw images — the memory layer's differentiated value is
   **occluded/out-of-view space and cross-time facts**, which a single-frame model cannot know.

### 3.5 Monitoring triggers (updated 2026-06-10)

| Trigger | Status | Next check |
|---|---|---|
| RoboOS-NeXT STEM code release ([#73](https://github.com/FlagOpen/RoboOS/issues/73)) | 🟢 still unreleased | after BAAI Conf (2026-06-12/13); then quarterly |
| RoboOS 2.0 Redis → persistent storage | 🟢 unchanged (still `FLUSHDB` on start) | same |
| NEW: BAAI Conf 2026 embodied forum (06-13: ORCA world model, "robot universal brain") | ⏳ days away | re-run both checks after announcements |
| NEW: RoboBrain 2.5-32B release (repo TODO) | unreleased | opportunistic |

---

## 4. Sources

RoboOS: [repo](https://github.com/FlagOpen/RoboOS) · [`stand-alone` branch](https://github.com/FlagOpen/RoboOS/tree/stand-alone) · [arXiv 2505.03673](https://arxiv.org/html/2505.03673v2) · [RoboOS-NeXT 2510.26536](https://arxiv.org/html/2510.26536v1) · [FlagScale Collaborator](https://github.com/FlagOpen/FlagScale/blob/main/flagscale/agent/collaboration/collaborator.py) · issues [#73](https://github.com/FlagOpen/RoboOS/issues/73)/[#75](https://github.com/FlagOpen/RoboOS/issues/75)/[#76](https://github.com/FlagOpen/RoboOS/issues/76)/[#77](https://github.com/FlagOpen/RoboOS/issues/77)/[PR #70](https://github.com/FlagOpen/RoboOS/pull/70)
RoboBrain: [RoboBrain2.5 repo](https://github.com/FlagOpen/RoboBrain2.5) (incl. archived `rb_v2.0/README.md`) · [RoboBrain 1.0](https://github.com/FlagOpen/RoboBrain) · [arXiv 2507.02029](https://arxiv.org/abs/2507.02029) · [arXiv 2601.14352](https://arxiv.org/abs/2601.14352) · [arXiv 2502.21257](https://arxiv.org/abs/2502.21257) · [ShareRobot](https://github.com/FlagOpen/ShareRobot) · [RoboBrain-X0](https://github.com/FlagOpen/RoboBrain-X0) · [project page](https://superrobobrain.github.io/) · [HF BAAI](https://huggingface.co/BAAI/RoboBrain2.0-7B) · [BAAI Conf 2026 agenda](https://hub.baai.ac.cn/view/55074)
