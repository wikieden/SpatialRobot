> 🌐 **English** · [中文](../../zh/research/embodied-brain-gaps-probe-2026.md)

# Round 2 Deep Dive: Spatial Memory GTM Willingness-to-Pay + RoboOS/InternRobotics Scene-Graph Memory (2026)

> Multi-agent workflow deep dive + adversarial verification. Backfills VISION's OQ-1 (first paying party) and OQ-5 (whether RoboOS covers it). Numbers handled per verdict.

---

# Chronotope Round 2 Deep-Dive Report: Commercial Willingness-to-Pay and RoboOS/InternRobotics Scene-Graph Memory

> This report is written based on two deep-dive datasets that have undergone adversarial verification. All numbers and inferences are faithfully tagged with their verdict: `confirmed` / `updated` (number confirmed but inference needs correction) / `uncertain` (source unreliable or not applicable) / `refuted` (overturned, not adopted). Refuted numbers are never used as arguments and are listed only as "cautionary lessons / cognitive corrections." The corresponding VISION document is `docs/en/VISION.md` (OQ-1 see §6.1, OQ-5 see §7.2).

---

## 1. Gap A: Spatial Memory Commercial Willingness-to-Pay / GTM

### 1.1 Conclusion (one sentence)

Structured spatial memory / 3D scene-graph memory **has real enterprise willingness-to-pay, but to date there is no precedent globally of a "pure software SDK form" that has been commercialized with publicly disclosed revenue**. The most viable commercial forms, ranked by deployment difficulty, are: ① hardware-bundled module (per-device) ② RobOps platform value-added subscription (per-robot/month) ③ cloud service API (per-query) ④ pure software SDK enterprise licensing (longest path, hardest to validate). This is fully consistent with VISION §6.1's honest tag that "there is currently no validated paying party" — this deep dive **did not overturn that judgment, but supplemented it with comparable business-model samples and pricing anchors**.

### 1.2 Evidence: Positive Signals (willingness-to-pay is real)

| Evidence | Key facts | verdict / credibility | Implication for us |
|---|---|---|---|
| **Slamcore (spatial perception SDK)** | Out of Imperial College, cumulative funding nearly $25M (CBInsights/Tracxn records $26M across 4 rounds); at 2022 Series A "100+ companies onboarded" (mostly at POC stage); March 2024 launched Slamcore Aware hardware+software bundle (targeting warehouse forklifts/AGVs), per-device sales | Funding and customer count **confirmed**; the "proves standalone commercial value" inference **uncertain** — the pivot to hardware bundling precisely hints that the pure-SDK model hit obstacles. **The "acquired by Oxa" sub-claim is refuted** (the one acquired was StreetDrone; Slamcore remains independent) | Spatial-perception tech enterprises are willing to pay ✅; but the pure-software → hardware-bundle pivot is the most important reverse warning |
| **Mem0 (LLM text memory, the strongest analog)** | YC S24; closed $24M funding in 2025-10 (led by Basis Set, with YC/Peak XV participating); pricing Hobby free / Starter $19/mo / Pro $249/mo / Enterprise custom; API calls Q1 2025 35M → Q3 186M (~30% MoM growth); AWS Strands Agent SDK chose it as the sole memory provider | Numbers **confirmed** (official Series A + TechCrunch first-hand confirmation); the **"directly analogous to spatial memory SDK" inference is updated (partly refuted)** | The "memory as a service" model is validated; but **you cannot directly copy the growth rate/TAM** (see §1.5 risks) |
| **Manifold Tech / Odin 1 (Shenzhen, HKU MaRS Lab)** | The only hardware+algorithm bundle to write "spatial memory" into the product name (LiDAR+camera+IMU+MindSLAM); closed "nearly RMB 100M Pre-A+" (jointly led by Matrix Partners China + Gobi GBA, larger than the initial report's "seven figures"); already listed on Foxtech third-party distribution; supported Unitree H1 in fully autonomously finishing the 2026 Beijing humanoid half-marathon | Funding size **updated (was underestimated)**; mass production has substantive progress **confirmed**; "world's first" **uncertain (self-declared, no third-party verification)** | The per-device hardware-bundle route already has funding + mass-production evidence in China, and is the most recently deployed form |
| **Robot ops middleware (InOrbit / Formant / Foxglove)** | InOrbit ~$500/robot/month (free below 3 units); Formant $50–500+/robot/month (VnRobo reference ~$250); Foxglove Pro from $20, $45/device/month, proactively cut prices in 2026-04 to expand adoption | Pricing ranges **updated (basically hold but with buyer mismatch)** — data comes from non-official aggregator sites, and targets "robot operators" rather than "developers/OEMs" | The per-robot/month SaaS model is validated ✅; but **the paying party differs from our buyer (developers/OEMs)**, so the pricing cannot be directly applied |
| **Vector databases (Pinecone/Weaviate/Qdrant)** | Prove the "infrastructure as a service" model is viable, consumption-based pricing + ecosystem lock-in | Commercialization direction **partially supported**; **but all specific revenue numbers are refuted** (see §1.5) | Can only serve as directional corroboration that "the infrastructure memory layer can be commercialized"; **no specific revenue number may be cited** |
| **Tera AI (pure software spatial navigation)** | SF, founded by a former Google X ML lead; emerged from stealth with $7.8M in 2025-03 (Felicis/Inovia/Naval Ravikant); advocates "hardware-agnostic pure-software spatial reasoning, the iOS of robots," customers are OEMs that already have hardware | **medium** (no revenue, needs 2025–2026 validation) | Investors are confident in "pure-software spatial-reasoning per-robot licensing," but the product is not yet monetized |

### 1.3 Evidence: Negative Signals (why "pure SDK willingness-to-pay" is still unvalidated)

- **The spatial-memory OSS closest to our positioning are all free, with zero paying cases**: RobotMem (24★), eMEM/EMOS (Automatika, 2★, MIT) all contain spatial retrieval (R-tree) + semantic retrieval (HNSW) + temporal retrieval (SQLite), highly isomorphic to us, but **have no paid tier and no disclosed commercial users**. `evidence_strength: strong`.
- **Top robotics companies build the full stack in-house and do not procure**: Figure (Helix), Tesla Optimus, AgiBot all treat perception/memory as core differentiation and build it in-house. Industry consensus: "perception/localization/memory **is procured when not differentiating, built in-house when differentiating**."
- **NVIDIA Isaac provides a competitive foundational tooling layer for free** (used by 400+ teams, including almost all top humanoid companies), suppressing the chargeable space for foundational tooling.
- **Lack of direct evidence (core negative)**: searches found no company selling "3D scene-graph memory / semantic spatial memory graph" as a standalone SDK product with public revenue. Academic systems (DynaMem/ReMEmbR/RoboMemory) are all OSS with no commercial plan; Manifold did it but **bundles hardware**. `evidence_strength: strong`.
- **The current paying model in the China market is still the whole machine**: iResearch's "2025 China Commercial Embodied Intelligence White Paper" + East Money research reports: currently dominated by one-time whole-machine sales with software as supplement; the evolution path is whole machine → whole machine + software subscription → RaaS → pay-for-outcome. Spatial memory is currently **bundled as an ancillary feature, not yet priced separately** (`medium`).

### 1.4 Comparable Business Models (ranked by similarity to us)

1. **ARBE "the Qualcomm of robot perception" model** (most similar to a spatial memory SDK): perception/localization/memory licensed as a foundational IP sold to OEMs. The structure fits "neutral third-party memory standard" best, but requires the premise "memory is differentiating yet OEMs are unwilling to build it in-house" to hold.
2. **Slamcore Aware: hardware-bundled per-device** (fastest to deploy): use hardware anchoring to raise pure-software conversion — Slamcore's own pivot from pure SDK to bundling is the biggest lesson for us. Manifold Odin 1 has already validated funding + mass production in China.
3. **Mem0: cloud API per-query "memory as a service"** (sexiest narrative, smallest customer base): the model is reusable, but the robot OEM customer count is orders of magnitude smaller than LLM developers, and the growth rate is not analogous.
4. **InOrbit/Formant: per-robot/month RobOps subscription** (clearest pricing anchor): $50–500/robot/month is validated, but the buyer is the operator, not the developer — if we go this route we must bind to a high-frequency ops pain point.

### 1.5 Key Risk Points (mistaken analogies / numbers struck down by adversarial verification, do not cite again)

- **Pinecone "2024 revenue $26.6M" and Weaviate "$200M ARR" are both refuted**: Pinecone's revenue comes from GetLatka (a non-official aggregator; the company never disclosed it), and by 2025 it had dropped to $14M; different sources contradict each other at $14M/$120M/$380M. Weaviate's "$200M" is actually a Series B **valuation** mislabeled as ARR; the real revenue magnitude is about $12–21M (GetLatka records $12.3M). **These two sets of numbers must not appear in any external materials.**
- **Mem0 growth rate "directly analogous" refuted**: Mem0 serves 100K+ low-barrier developers, a high-concurrency long-tail SaaS; the spatial memory SDK targets robot OEMs, with a 3–12 month integration cycle and procurement driven by engineering/procurement departments. Using Mem0's 186M API/quarter growth rate as a TAM or growth-rate benchmark would **overestimate by 1–2 orders of magnitude**.
- **"Embodied software platform $18,000–45,000/robot/year" uncertain**: from a Research Intelo paid report, with opaque methodology that cannot be cross-validated; that range covers an entire software platform (skill management/OTA/telemetry) and does not represent standalone pricing for the memory sub-layer. First-hand RaaS data is a non-decomposable whole package (Figure RaaS ~$1,000/mo, 1X NEO $499/mo, humanoid RaaS $2,500–8,000/mo).
- **InOrbit/Formant pricing "directly applied" needs a discount**: the range holds but comes from non-official estimation sites, and the paying party is mismatched (operator ≠ developer); the value share the memory sub-layer can capture is lower.

### 1.6 Recommendations for Our GTM (who pays / what form)

**Consistent with the sequencing in VISION §6.1 / §6.2 / §6.4, this deep dive provides a more specific backfill:**

- **Who pays (first ICP)**: stick with the hypothetical profile in VISION §6.1 — **a pure-actuator body maker or open-source brain team that does not build S2 in-house but has long-horizon/multi-shift spatial memory needs**. This deep dive adds: **Manifold Odin 1's customer base (small/mid-sized robot/UAV makers that already have hardware but lack memory software) is the closest real reference sample**; while Figure/Tesla/AgiBot (the build-it-in-house camp) should be explicitly excluded from the first batch.
- **Paying form (ranked by "which to do first")**:
  1. **From P3: PoC consulting + enterprise-tier license** (consistent with VISION §6.2(c)'s default inclination) — small customer base, long sales cycle, but high ACV; first use consulting to break through to real demand.
  2. **For faster monetization, prioritize "light hardware bundle / reference hardware + .smem"** over pure SDK — Slamcore's pivot and Manifold's mass production are dual lessons: **pure-software conversion is hard, hardware anchoring raises procurement certainty**.
  3. **Hosted API as a revenue source (not a moat)** — doable, but the customer base is small, so it should not be the P1–P2 main line (consistent with VISION §6.4 "no enterprise sales in P1–P2").
- **External-messaging discipline**: when discussing willingness-to-pay externally, **only cite the three sets of confirmed facts — Slamcore (funding/customers), Mem0 (funding/pricing/call volume), Manifold (funding/mass production)**; **do not cite Pinecone/Weaviate revenue numbers, do not use Mem0's growth rate to extrapolate TAM, do not cite Research Intelo's $18K–45K**.

---

## 2. Gap B: Whether RoboOS / InternRobotics Comes with Scene-Graph Memory

### 2.1 Conclusion: Complementary, Not Covered (under the current architecture)

The major domestic open-source "one brain, many bodies" stacks currently **all lack a standalone, persistent, structured scene-graph storage layer that could replace `.smem`**. The closest competitor is **BAAI RoboOS**: its Real-Time Shared Memory does include a hierarchical dynamic scene graph, but **the underlying store is Redis in-memory (lost on restart, not disk-persistent)**, and it is positioned as a multi-robot real-time coordination middleware rather than an embeddable monolithic memory core. **Under the current architecture, the two form a complementary interface relationship (`.smem` can serve as RoboOS's persistence backend), not a substitution relationship.** `evidence_strength: strong`.

**Largest near-term risk**: RoboOS-NeXT's STEM (Spatio-Temporal-Embodiment Memory) is the most complete structured scene-graph academic design domestically, with high conceptual overlap with `.smem` — but **the code is not yet open-sourced as of the research date** (the GitHub Issue "Release RoboOS-Next" shows it is unreleased). Once released and adopting persistent storage, the positioning differentiation needs to be re-evaluated.

### 2.2 Memory Status Comparison Across Stacks

| Stack / Team | Has scene graph? | Storage layer | Persistence | Positioning | Relation to .smem | Credibility |
|---|---|---|---|---|---|---|
| **BAAI RoboOS 1.0** (arXiv:2505.03673, Apache-2.0, 561★ as of 2026-05 — grew to 571★ by 2026-06-10, see the RoboOS/RoboBrain deep-dive) | ✅ Dynamic scene graph (floor/room/object layering, nodes contain position/affordance/label, built from RGB-D+SAM+CLIP) | **Redis** (in-memory KV, JSON+RAG) | ❌ frame-by-frame update, not cross-session | Multi-robot real-time coordination middleware | **Complementary** — .smem can be its persistence backend | strong |
| **BAAI RoboOS-NeXT / STEM** (arXiv:2510.26536, 2025-10) | ✅ Most complete: queue-tree-graph-agent (root/region/carrier tree + object relation graph, predicates ON/IN/LEFT/RIGHT/FRONT/BACK/NEAR) | Not specified in paper (design layer) | Paper-level, **code not open-sourced** | Academic design | **Largest potential overlap**, re-judge pending code release | strong |
| **BAAI RoboBrain 2.0/2.5** (arXiv:2507.02029, 3B/7B/32B, Apache-2.0) | Scene graph only as **LLM input JSON token**, the model **consumes** but does not **store** | None (persistence delegated to RoboOS Redis) | ❌ | Brain model | Does not constitute a memory competitor | strong |
| **InternRobotics (Shanghai AI Lab, formerly OpenRobotLab)** | EmbodiedScan/OST-Bench/InternSR are all **perception/evaluation tools**; InternUtopia's WKM is only in-memory within simulation | No runtime persistent memory module | ❌ | Perception/evaluation toolchain | **No substitute competitor** (but OST-Bench shows this direction is under research) | strong |
| **Horizon (FSR-VLN / EmbodiedGen)** | FSR-VLN uses a hierarchical multimodal scene graph (HMSG) for navigation, stored in memory; EmbodiedGen is a 3D world generation tool | In-memory | ❌ | Navigation/data generation | Not a persistent-memory competitor | medium |
| **Huawei CloudRobo (Pangu)** | Commercial marketing layer mentions environment perception/global planning, technical details undisclosed | Closed-source unknown | Unknown | Closed-source industrial SaaS | No open-source competitor; potential standards risk | medium |
| **Noematrix Brain** | Website claims long-term/short-term memory, **no technical docs/code/papers** | Closed-source unknown | Unknown | Closed-source full-stack SDK | Cannot be verified (may refer only to task logs) | weak/uncertain |
| **Galaxy Universal Galbot (AstraBrain)** | End-to-end VLA (GraspVLA/NavFoM, etc.), **no explicit scene-graph memory layer** | Closed-source unknown | ❌ (end-to-end neural network) | Closed-source commercial full-stack | No explicit scene-graph competitor | medium |

### 2.3 RoboOS Scene Graph vs `.smem`: Why "Complementary" Holds (technical details)

At the conceptual level they correspond highly (both are hierarchical node-edge scene graphs, both support incremental update and RAG query), but four key differences determine the complementary relationship:

1. **Storage**: RoboOS = Redis (in-memory KV, lost on restart); `.smem` = SQLite (single disk file, persistent across sessions).
2. **Format**: RoboOS = JSON token strings passed into the LLM; `.smem` = structured relational tables + vector columns (sqlite-vec ANN).
3. **Installation barrier**: RoboOS needs a Redis server + multi-robot network + FlagScale cloud RoboBrain; `.smem` is a numpy-only `pip install` with no external dependencies.
4. **Positioning level**: RoboOS = multi-robot collaboration scheduling framework; `.smem` = monolithic memory core (hippocampus). **Different levels → can be stacked rather than mutually exclusive.**

> **Important correction (a common misreading struck down by verification)**: the "scene reasoning / scene graph" in the RoboBrain 2.0 paper refers to both the input token format and the model capability, and is **easily misread as "the model has a built-in scene-graph database."** In reality RoboBrain only consumes JSON scene-graph tokens; persistence is handled by RoboOS's Redis. **Judging "covered" based on this misreading would lead to the wrong conclusion.**

### 2.4 Impact on Our Integration Strategy

- **Cement "complementary integration" as the P2 default direction** — for the "probe before deciding" gate set in VISION §7.2, the conclusion this spike provides is: **RoboOS does not come with persistent scene graph → go complementary**. We can position `.smem` as "RoboOS's persistence backend / offline merge layer."
- **Differentiation handles**: ① numpy-only / zero external services vs RoboOS needing Redis + multi-machine network; ② disk-persistent across sessions vs Redis lost on restart; ③ cross-stack neutrality (any OpenAI-compatible Reasoner / mountable on both Chinese and US stacks).
- **Two triggers to keep tracking continuously**:
  1. `https://github.com/FlagOpen/RoboOS/issues` — **RoboOS-NeXT STEM code release**: if released in 2026 and adopting persistent storage such as SQLite/PostgreSQL, the complementary relationship may turn into substitution, and re-evaluation is needed immediately.
  2. Whether RoboOS 2.0 switches Redis to persistent storage (the "by end of this month" commitment has expired).
- **InternRobotics's latent risk**: frequent renaming (OpenRobotLab→InternRobotics, GRUtopia→InternUtopia), and OST-Bench (2025-07) shows it is researching online spatio-temporal reasoning, **may release a runtime memory library in the future**, and must be included in quarterly monitoring.
- **External-citation discipline**: when citing RoboOS's "cross-robot spatial memory sharing" as a demand signal, **we can only say "it overlaps with us in the offline-sharing sense," and must not imply we can do real-time concurrent sharing** (consistent with VISION §4.3/§1.3).

---

## 3. Backfilling VISION's Open Questions

### 3.1 OQ-1 (who is the first paying party) — partially backfilled, core still open

**VISION §6.1 original status**: completely blank, "there is currently no validated paying party."

**What this deep dive backfills**:
- ✅ **Confirmed that "no standalone procurement precedent" is the real market status quo** — no company globally sells spatial memory as a pure SDK with public revenue, validating that VISION's blank judgment on OQ-1 is accurate rather than conservative.
- ✅ **Found the closest real reference sample for the hypothetical ICP**: Manifold Odin 1's customer base (small/mid-sized robot/UAV makers that already have hardware but lack memory software) ≈ VISION §6.1's "pure-actuator body maker that does not build S2 in-house and has long-horizon memory needs."
- ✅ **Explicitly excluded the impossible first-batch customers**: Figure/Tesla/AgiBot (the build-it-in-house camp), enterprise end users (buy solutions, not SDKs).
- ✅ **Provided a credible range and prohibited numbers for pricing anchors**: can reference per-robot/month $50–500 (treat with a discount), per-device bundle (Manifold/Slamcore Aware), per-query (Mem0 $19–249/month model); **prohibited** Pinecone/Weaviate revenue, Research Intelo $18K–45K.

**The part still not closed (OQ-1 closure criteria not met)**:
- ❌ **Still no "real customer prototype willing to pay for some product form"** — the 1–2 real customer interviews required by VISION §6.1 have not happened; this was a desk deep dive, not first-hand customer validation.
- ❌ **First commercial form undecided** (belongs to OQ-2): the trade-off among hardware bundle vs pure SDK vs hosted API still needs interview data to support.
- **Recommendation**: maintain VISION's discipline of "do not invest heavy resources in commercialization/hosting before OQ-1 closes"; P3 customer interviews should prioritize locking in the "already has hardware, lacks memory software" small/mid-sized maker sample (benchmarking the Manifold customer profile).

### 3.2 OQ-5 (whether RoboOS / InternRobotics covers it) — basically backfilled, conclusion is "complementary (for now)"

**VISION §7.2 original status**: unverified, deciding "complementary" or "covered," listed as a P2 pre-gate spike.

**What this deep dive backfills (spike conclusion)**:
- ✅ **Conclusion = complementary, not covered**: RoboOS uses Redis in-memory (non-persistent), positioned as multi-robot coordination middleware; RoboBrain only consumes JSON scene-graph tokens, does not store; InternRobotics is all perception/evaluation tools, with no runtime persistent memory. **Satisfies VISION §7.2's branch condition "if not built-in → P2 cement complementary integration."**
- ✅ **Can lift the downgrade on RoboOS citation in VISION §1.3** — the original requirement was "downgrade to a to-be-verified signal until the spike concludes"; now that the spike has concluded, RoboOS can again be cited as "demand signal + complementary integration point" (but limited to offline-sharing semantics, see §2.4 discipline).
- ✅ **P2 direction can be cemented**: complementary integration (`.smem` as RoboOS's persistence backend), with differentiation on numpy-only / persistent cross-session / cross-stack neutral.

**The part still not closed**:
- ⚠️ **RoboOS-NeXT STEM code is not open-sourced** — this is the only active tail risk of OQ-5. Its academic design has high overlap with `.smem`, and **once the code is released, the "complementary vs covered" must be re-evaluated immediately**. OQ-5 should be tagged as "temporarily closed, with a monitoring trigger attached" rather than fully closed.
- ⚠️ **Closed-source stacks (Huawei CloudRobo / Noematrix) cannot be verified**: they claim to have memory but with no technical details, and may form a de facto standard in the long run (e.g., Huawei opening the R2C protocol) that indirectly influences the direction of `.smem` interface design.

### 3.3 Summary of VISION Status After Overall Backfill

| OQ | Before backfill | After backfill | Closed? |
|---|---|---|---|
| **OQ-1 first paying party** | completely blank | market has no precedent (confirmed) + ICP real reference (Manifold customer base) + pricing anchors | **not closed** (lacks real customer interviews, needs P3) |
| **OQ-5 RoboOS coverage** | unverified | spike conclusion = complementary; RoboOS does not come with persistent scene graph | **temporarily closed** (with RoboOS-NeXT code monitoring trigger) |

---

## 4. Sources

### 4.1 Gap A (willingness-to-pay / GTM)

**confirmed / updated (citable)**
- Slamcore: `https://www.slamcore.com/about/`, `https://www.cbinsights.com/company/slamcore/financials`, `https://www.robotics247.com/article/slamcore_raises_series_a_funding_low_cost_spatial_understanding_robots_metaverse`, `https://www.slamcore.com/press-release/slamcore-aware-brings-power-of-vision-to-rtls/`
- Mem0: `https://mem0.ai/series-a`, `https://mem0.ai/pricing`, `https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-agents/`, `https://rywalker.com/research/mem0`
- Manifold Odin 1: `https://kr-asia.com/memory-for-machines-manifold-techs-odin-1-brings-spatial-recall-to-robotics`, `https://www.kr-asia.com/pulses/154463`, `https://www.3dmanifold.com/about/`, `https://store.foxtech.com/odin1-spatial-memory-module-for-robotics-uavs/`
- Robot middleware pricing: `https://cobotfinder.com/guides/robot-fleet-management`, `https://softwarefinder.com/fleet-management-software/formant`, `https://vnrobo.com/en/blog/inorbit-alternatives`, `https://www.inorbit.ai/faq`, `https://docs.foxglove.dev/docs/pricing`
- Tera AI: `https://techcrunch.com/2025/03/19/teraai-comes-out-of-stealth-with-7-8m-to-provide-visual-navigation-for-robots/`
- OSS spatial memory (negative): `https://robotmem.com/`, `https://github.com/automatika-robotics/emem`, `https://dynamem.github.io/`, `https://github.com/NVIDIA-AI-IOT/remembr`
- make-vs-buy: `https://roboticsreports.com/arbe-the-qualcomm-of-robotics-perception/`, `https://www.droidbrief.com/resources/ai%E2%80%93robotics-intersection/robot-operating-systems-software-stacks-the-invisible-infrastructure-powering-humanoid-robots.html`
- China paying trend (medium): `https://www.eet-china.com/mp/a458253.html`, `https://pdf.dfcfw.com/pdf/H3_AP202512031793353788_1.pdf`

**refuted / uncertain (correction only, do not cite their numbers)**
- Pinecone/Weaviate revenue (refuted): `https://getlatka.com/companies/pinecone.io`, `https://eboona.com/ai-unicorn/weaviate/`, `https://getlatka.com/companies/weaviate`, `https://theaiengineer.substack.com/p/what-does-pinecone-actually-do`
- Embodied software platform $18K–45K (uncertain): `https://researchintelo.com/report/embodied-ai-robot-software-platform-market`

### 4.2 Gap B (RoboOS / InternRobotics)

- BAAI RoboOS 1.0: `https://arxiv.org/html/2505.03673v2`, `https://github.com/flagopen/roboos`, `https://flagopen.github.io/RoboOS/`
- RoboOS-NeXT / STEM: `https://arxiv.org/html/2510.26536v1`, `https://huggingface.co/papers/2510.26536`, `https://github.com/FlagOpen/RoboOS/issues`
- RoboBrain 2.0/2.5: `https://arxiv.org/html/2507.02029`, `https://github.com/FlagOpen/RoboBrain2.0`, `https://huggingface.co/BAAI/RoboBrain2.0-3B`
- InternRobotics: `https://github.com/InternRobotics/EmbodiedScan`, `https://github.com/InternRobotics/InternUtopia`, `https://github.com/InternRobotics/OST-Bench`, `https://github.com/InternRobotics/InternSR`, `https://github.com/InternRobotics/RoboInter`
- Horizon: `https://horizonrobotics.github.io/robot_lab/fsr-vln/`, `https://github.com/HorizonRobotics/EmbodiedGen/`
- Huawei CloudRobo: `https://www.huaweicloud.com/eu/news/20250620192415143.html`, `https://en.tmtpost.com/news/7604616`
- Noematrix (weak/uncertain): `https://www.noematrix.ai/en/noematrix-brain`
- Galaxy Universal Galbot: `https://www.robotsasia.com/as-fa/Galbot-G1.htm`, `https://news.qq.com/rain/a/20250609A056G400`

### 4.3 Internal Basis in This Repo

- OQ-1 / OQ-5 definitions and closure criteria: `docs/en/VISION.md` (§6.1, §7.2, §8 milestone table)
- System-level vision: `docs/en/VISION.md` (finalized v3)
- Existing competitor research: `docs/en/research/embodied-brain-landscape-2026.md`
- Single-package memory core vision and Open Questions: `tempomem/docs/en/00-VISION.md`, `tempomem/docs/en/05-OPEN.md` (B3 Mem0 collaboration question is directly related to §1 of this report)
