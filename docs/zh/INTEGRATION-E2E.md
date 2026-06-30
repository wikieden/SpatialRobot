> 🌐 [English](../en/INTEGRATION-E2E.md) · **中文**

# 生产级端到端整合 —— 规划

**状态：** 规划+建设中（2026-06-29）。L3 大脑软件已功能完整（P0–P5 ✅，P6 真 LLM 已验证）；
这是压轴 —— 证明**整栈作为一个系统**在生产要求下工作。配套：[TECH-DESIGN.md](TECH-DESIGN.md)。

## 1. 目标

一个可运行 harness 驱动**整栈**跑家庭场景：

```
真 LLM 大脑（Cosmos-Reason2 + Qwen3.6，经 FailoverVerbalizer）
   → SceneContextProvider + WorldState（动态上下文）
   → SkillCardPlanner / LLM planner → compile (D3) → Phylax (P3) → dispatch
   → SimDeviceAdapter + GenesisSimBackend（物理身体）  [或 MockBody]
   → 有界 Replanner (P4) + TraceStore (L4)  → Conversation (P5)  → VoiceLoop (P7)
```

…并**度量**：准确率、成功率、安全合规、时延 —— 全程痕迹留存可审计。

## 2. 六项生产要求 → 机制

owner 的标准：**可做·可复现·可追溯·安全可靠·高准确率·高成功率**。每项映射到栈里已有的机制：

| 要求 | 机制（凭什么成立） |
|---|---|
| **可做 / 可运行** | 一个入口 `ScenarioRunner.run(scenarios)`；可运行示例；接 CI |
| **可复现** | 网络隔离基线（ScriptedReasoner）完全确定（seeded RNG + 脚本 plan）；真 LLM pass 钉死模型+记录 config；report 是稳定产物 |
| **可追溯** | `TraceStore` 记每次派发+失败、引用场景 **node id**（B9）；答案引用 node id；report 内嵌逐场景痕迹 + 产生它的 config |
| **安全可靠** | 每个 plan 过 `Phylax` gate（P3）；`FailoverVerbalizer`（远端→本体，断网不崩）；有界 `Replanner`（P4，无死循环）；类型化 `ErrorCode`/`RecoveryHint`（B3）；坏 turn 降级、不中断 harness |
| **准确率** | `run_eval` 指标 —— 规划准确率、引用合规、策略合规 —— 对 `EvalThresholds`（规划 ≥0.9、策略 =1.0）打分 |
| **成功率** | 跨场景聚合任务终态 SUCCESS（含重规划恢复），报成功率 vs 阈值 |

## 3. Harness 架构（`skillforge.scenario`）

skillforge 是 import 全部成员的那个 —— 驱动 mem+brain+body+world 的 lab。整合 harness 住这：

- **`Scenario`** —— 具名多轮脚本：场景（detections）、轮次（指令+person+role+期望）、装配旋钮
  （哪个 body、哪个 reasoner）。复用 `mindloop.EvalCase` 期望。
- **`ScenarioRunner`** —— 建**生产装配的 `Brain`**（全能力：context provider、world-state、
  SkillCardPlanner+LLM 回退、Phylax、Replanner、TraceStore、preferences）于一个 body
  （`MockBody` 或 `SimDeviceAdapter`+Genesis），每轮经 `brain.converse` 跑，收结果+时延。
- **`IntegrationReport`** —— 逐场景通过/失败 + 四项 eval 指标 + 成功率 + 时延分位 + 内嵌痕迹 +
  运行 config（复现）。`meets(thresholds)` 给一个生产 go/no-go。

**两模式、同 harness：**
1. **基线（网络隔离，CI）：** ScriptedReasoner/Planner + MockBody —— 确定、可复现、快；证*回路+安全+重规划+痕迹*逻辑。
2. **真实（验证）：** `FailoverVerbalizer`→主机 Cosmos+Qwen + Genesis 仿真 —— 证*准确率+成功率* vs 生产模型。在 GPU 主机跑。

## 4. 场景集（家庭，对齐 B2R）

小而增长的套件，演练每个能力：

- **问答** —— "厨房有什么？" → 带引用答案。
- **任务/成功** —— "把瓶子拿来" → navigate+grasp → SUCCESS、有痕迹。
- **任务/重规划恢复** —— grasp 失败一次 → 有界重规划 → SUCCESS。
- **任务/安全阻断** —— 小孩要成人级操作 → Phylax 阻断、零派发。
- **多轮对话** —— 追问对前一轮解析。
- **偏好** —— 某人偏好覆盖卡片默认。
- **技能卡** —— 洗衣/烹饪卡 → 多步 plan → SUCCESS。

## 5. 可复现 & 可追溯产物

- runner 取 seed + config 对象；report 记两者。
- 基线模式零网络、零模型下载（CLAUDE.md 测试规则）。
- 每个派发子任务都在 `TraceStore`、可按 node id 查；report 序列化痕迹，使一次运行事后可审计。

## 6. 分期

1. **Harness + 基线**（网络隔离、确定）：`Scenario`、`ScenarioRunner`、`IntegrationReport`、
   场景套件、测试。CI go/no-go。
2. **真 LLM 验证 pass**：换 `FailoverVerbalizer`→主机；在 GPU 主机跑；取准确率+成功率+时延；归档 report。
3. **仿真身体**：套件经 `SimDeviceAdapter`+Genesis（物理步进）跑，补 MockBody。
4. **语音**：可选地经 `VoiceLoop`（voicelink fill）驱动轮次。

---

## 附录 —— 暂缓的软件轨（轻量计划）

> **范围扩展（规划）。** 三个新任务族（导览导游 · 多样家务 · 寻找遗失物）、执行动态
> （打断 · 失败重规划 · 问询人类）、数据/训练闭环，均规划于 [TASK-FAMILIES.md](../en/TASK-FAMILIES.md)；
> 全部流程图（组件 · 主干 · 动态 · 任务族 · 数据闭环）在 [FLOWS.md](../en/FLOWS.md)。
> 它们扩展本压轴的场景集 + 指标 —— 同一套六标准 go/no-go 门。

**轨 2 —— 收尾剩余大脑软件**
- *动态场景第 4 步（主动感知）：* focus 陈旧或 reasoner 请求时，步间重 `observe` → fuse → 重查新
  context → 重规划尾部。钩子已有（`_dispatch_plan`、版本 bump）。脚本感知器网络隔离可测。
- *P7.4（降级+telemetry）：* 离线模式优先技能卡、收紧到保守安全、记每轮哪个模式（在线/离线）服务；
  诚实"我离线了"UX。基于 `FailoverVerbalizer.mode`。

**轨 3 —— skillforge 自学习深化**
- ENPIRE 回路（Environment/Policy/Rollout/Evolution）现是 walking skeleton。深化：更丰富 reward
  shaping、LLM `PolicyAuthor`（替 ScriptedAuthor）、技能结晶回 Episteme 卡（闭 学→用 环）。研究轨。

两者已圈定+停放；整合压轴（上文）是焦点。
