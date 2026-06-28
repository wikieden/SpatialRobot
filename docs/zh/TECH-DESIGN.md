> 🌐 [English](../en/TECH-DESIGN.md) · **中文**

# Chronotope —— 当前技术设计（快照）

已建成栈的**当前状态**综合视图。愿景见 [VISION.md](VISION.md)；本文是工程快照 ——
有什么、怎么拼、哪些是契约、还差什么。详细 spec 交叉链接、不重复。

**日期：** 2026-06-28。**已达里程碑：** M-L3.1 (P1) ✅、M-L3.2 (P2+P3) ✅。

---

## 1. 栈 —— 五个包，一个身体隐喻

```
RGB(-D) ─► worldsense (眼) ─► Detection[] ─┐
                                           ▼
                        tempomem (记忆: fuse → persist → query)   ← 唯一有状态对象
                                           │ serialize 子图
                                           ▼
        mindloop (大脑, S2):  route → plan → compile → POLICY → dispatch
                                           │ SubTask[] (动词 + node id)
                                           ▼
                        bodylink (身体 seam): MockBody / SimDeviceAdapter / 真机
                                           │ (Genesis sim backend)
                                           ▼
        skillforge (研究): ENPIRE 自学习回路，跨 mem+brain+body+world
```

| 包 | 角色 | 状态 |
|---|---|---|
| **tempomem** | 记忆核 —— `.smem` 场景图、fuse-before-persist、分层 query | 稳定核 |
| **worldsense** | 眼 —— RGB(-D) → 世界系 `Detection`（CLIP 在 `[clip]` 后） | 稳定 |
| **mindloop** | 大脑 —— S2 认知回路（P0–P3 完成） | **进行中** |
| **bodylink** | 身体 seam —— 填 `ExecutorAdapter`；多机型 + 仿真 | **进行中** |
| **skillforge** | 自学习实验室（ENPIRE walking skeleton，v0.1.0a0） | 研究 |

依赖方向：`worldsense → tempomem`、`mindloop → tempomem`、`bodylink → mindloop`、
`skillforge → 全部`。核心从不 import 其它 —— 只发它们填充的*协议*（`PerceptionAdapter`、
`Verbalizer`；`mindloop` 发 `ExecutorAdapter`）。

---

## 2. 大脑流水线（mindloop, S2）

`Brain.handle(instruction, safety_context=)` 是脊柱。两个感知入口（`observe`/`ingest`）
喂记忆；`ask` 答问；`handle` 是完整任务回路：

```
instruction
   │  ① IntentRouter.classify          ◀ LLM      task | question | chat
   ├─ question/chat ─► ask: 检索子图 → Reasoner (LLM) → 带引用 Answer
   └─ task
        ② Planner.plan                 ◀ LLM      技能卡 | 通用 LLM → Command[] (文本动词)
        ③ compile_commands             ◀ 规则     Command[] → SubTask[]: 绑 node id (B9)、
                                                   填 skill/pre/eff、丢本体不支持动词 (D3)
        ④ Phylax.check                 ◀ 策略     按 SafetyContext 审 → 阻断(停+说) 或 放行 (P3)
        ⑤ ExecutorAdapter.dispatch     ◀ 身体     SubTask → StatusUpdate[] (RUNNING→终态，回显 id B9)
   ► HandleResult(intent, answer | plan, statuses, violations, blocked)
```

**LLM 之后三段确定性。** 只有 ② 是生成步；③④⑤ 确定性。链单向、绝不回落到规则*规划器*
（见 [规划链](../../mindloop/docs/zh/devplan/specs/P1-intent-planning.md) §1a）：
- **③ compile（D3 gate）：** 本体 `CapabilityManifest` 决定哪些动词可派发；对象绑场景图 node id（B9）。
- **④ policy（P3 gate）：** Phylax 语义层阻断违反声明式 `Policy` 的 plan —— *停+说、不重路由、不重试*；
  单向收紧（下层不可以压过上层想做）。opt-in。
- **⑤ dispatch：** 只到动词级；本体在 L2 以下实现动词。

各阶段已实现：

| 阶段 | 内容 | spec |
|---|---|---|
| **P0** | seam 契约 + 值类型（`execute.py`） | — |
| **P1** ✅ | 意图路由 + 两段式规划（LLM 动词 → 规则编译） | [P1](../../mindloop/docs/zh/devplan/specs/P1-intent-planning.md) |
| **P2** ✅ | Episteme 技能卡库（程序性知识即数据） | [P2](../../mindloop/docs/zh/devplan/specs/P2-episteme-skill-cards.md) |
| **P3** ✅ | Phylax 策略层（语义安全 gate） | [P3](../../mindloop/docs/zh/devplan/specs/P3-phylax-policy.md) |
| **P4** ✅ | L4 痕迹 + 失败驱动重规划（有界；B3 类型化错误） | [P4](../../mindloop/docs/zh/devplan/specs/P4-trace-replanning.md) |
| P5–P6 | 对话+完整回路 · 生产 reasoner+eval | 待做 |
| **P7** | 边缘回退 —— 本体离线 AI 链路（LLM + ASR + TTS） | [P7](../../mindloop/docs/zh/devplan/specs/P7-edge-fallback.md) · 计划中 |

---

## 3. 身体 seam（bodylink）—— 换本体、留大脑

大脑规划**技能动词** + **node id**，从不碰关节角或几何（B8）。机型由**数据 + 薄 adapter**
定义，大脑代码不变（D3）。见[多机型设计](../../bodylink/docs/zh/multi-model-adaptation-design.md)。

- **两层 `CapabilityManifest`** —— `BodyProfile`（硬件：dof、`base_type`
  wheeled/legged/fixed）+ `VerbSpec` 动词层（规划器可出什么）。只有动词层改变大脑规划。
- **目录** —— `load_manifest("g1d"|"h1"|"gr1"|"arm6")`（内置覆盖三种 base_type）或厂商 `*.yaml`。
- **`BaseExecutorAdapter` SDK** —— 设备包只实现 `_execute()`；基类管动词 gate（D3）、
  RUNNING→终态流、node-id 回显（B9）。`MockBody` 与 `SimDeviceAdapter` 是子类。
- **一致性套件** —— `check_executor_adapter()` 证明任何本体守 seam。
- **物理仿真**（`bodylink.sim`，`[sim]` extra）—— `MockSimBackend` + `GenesisSimBackend`
  （真 Genesis 场景，镜像 B2R `GenesisL1`），`make_sim_backend` 选择。在 Linux RTX PRO
  6000 主机**和** macOS Apple Silicon 端到端验证：H1 跑洗衣卡，每 verb 真物理步进。

---

## 4. 契约（已批准决策）

seam 由已批准决策治理 —— 承重不变量：

| Id | 契约 |
|---|---|
| **D1** | 大脑**仅 S2**（审议）；反射/控制在 L2 以下 |
| **D3** | **开放词汇动词** + 两层 `CapabilityManifest` —— 换本体不改大脑 |
| **D4** | 三层 **Phylax** 守护（语义在大脑 ✅、符号-BT 在 bodylink、反射在固件） |
| **B3** | 执行器故障**类型化**（`ErrorCode` + `RecoveryHint`），绝非自由文本 |
| **B8** | 大脑从不碰**关节空间 / 底盘几何** |
| **B9** | 场景图 **node id 过 seam** 并被回显 —— 审计链闭合 |
| **K2** | 技能卡是**扁平步骤 + 规则**（DAG 经 `schema_version` 预留） |

---

## 5. 模型与部署

- **Reasoner**：Cosmos-Reason2-8B（物理-AI VLM）在 RTX PRO 6000（96 GB），OpenAI 兼容服务；
  `CosmosReasonVerbalizer`（stdlib，任意 `/v1/chat`）。
- **Planner / IntentRouter**：强指令遵循模型（Qwen3.6，`extra_body` 关思考）出干净动词序列 ——
  双模型裂解是质量甜点；单 Cosmos 也行（靠 `default_speak` 兜底）。
- **本体（P7 边缘回退）**：**与线上同款 Qwen 对齐双裂解、只是更小** —— Reasoner =
  Cosmos-Reason2（2B/8B），Planner = Qwen3.x-8B，加 Qwen3-ASR / Qwen3-TTS（small）做语音 ——
  断网时经 `FailoverVerbalizer` 接入（大脑零改动）。
- **仿真**：Genesis（CPU backend）主机 + 本地 macOS。
- 测试**无网络**：`ScriptedReasoner`、hash encoder、dict 技能卡、注入 fake-genesis ——
  任何测试不碰 LLM 或模型下载。

---

## 6. 已完成 vs 待做

**已完成：** P0 seam · P1 规划 · P2 技能卡 · P3 安全 gate（M-L3.1、M-L3.2）· P4 L4 痕迹 +
有界重规划 · bodylink 多机型框架（4 内置、SDK、一致性）· Genesis 仿真（主机 + mac）·
planner/reasoner 部署。

**待做：**
- **P5** —— 对话 + 完整 S2 回路。
- **P6** —— 生产 reasoner + eval harness + 云引导。
- **身体** —— 真正的*硬件* adapter（真机传输，非仿真）；并深化粗粒度仿真（逐机器人 IK /
  MJCF 关键帧，如 B2R 的 49-DOF G1）。
- **Phylax** —— D4 的符号-BT（bodylink）+ 反射（固件）两层。
- **P7 边缘回退** —— 本体离线 AI 链路：`FailoverVerbalizer`（遇 `QueryError` 远端→本体
  LLM，复用 `Verbalizer` seam）+ 新 `Listener`（ASR）/ `Speaker`（TTS）seam + 连通性感知
  模式仲裁。断网时机器人仍听到、规划（技能卡或本体 LLM）、过本地安全 gate、动作、说话 ——
  安全与记忆本就本地、永不离线。spec：
  [P7-edge-fallback](../../mindloop/docs/zh/devplan/specs/P7-edge-fallback.md)。
