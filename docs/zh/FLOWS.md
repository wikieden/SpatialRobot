# 流程图 — 场景 · 全流程 · 关键组件 · 数据/训练闭环

> Chronotope 具身大脑栈服务我们家庭机器人场景的规范流程图。Mermaid 在 GitHub 渲染。
> 配套 [INTEGRATION-E2E.md](../en/INTEGRATION-E2E.md)（生产终验）与
> [TASK-FAMILIES.md](../en/TASK-FAMILIES.md)（任务族 + 执行动态）。
> 数据/训练闭环（图 5）是下一阶段的规划。
>
> **每张图都作为独立 SVG 提交在 [`../assets/`](../assets/)（GitHub 渲染，亮/暗均可），
> 其可编辑 mermaid 源放在旁边的 `<details>` 块里 —— 改图时 mermaid 与 SVG 两者都要更新。**

---

## 1. 组件图（谁管什么 · 数据方向）

![组件图](../assets/flow-component-map.svg)

<details><summary>mermaid 源 —— 编辑后请同步更新 SVG</summary>

```mermaid
flowchart LR
  CAM([RGB-D 相机]) --> WS
  MIC([麦克风]) --> VL
  subgraph 感知
    WS[worldsense<br/>眼: RGB-D 到世界系 Detection]
  end
  subgraph 记忆
    TM[tempomem<br/>.smem 场景图: 融合 到 持久 到 查询<br/>区域 · history/ts · 衰减]
  end
  subgraph 大脑
    ML[mindloop<br/>路由 到 规划 到 编译 到 安全 到 调度 到 重规划 到 trace]
  end
  subgraph 接缝
    BL[bodylink<br/>执行: MockBody/Sim/真机 · D3 manifest]
    VL[voicelink<br/>ASR 耳 + TTS 嘴]
  end
  subgraph 实验室
    SF[skillforge<br/>ENPIRE 自学习 · 导入全部]
  end
  WS -- Detections --> TM
  TM -- 序列化场景 --> ML
  ML -- SubTask --> BL
  ML <-- Listener/Speaker --> VL
  BL -- StatusUpdate --> ML
  ML -- episodes --> TR[(TraceStore)]
  SF -. 驱动 .-> TM & ML & BL & WS
  TR -. rollout/eval .-> SF
```

</details>

依赖方向（绝不反转）：`worldsense→core`、`mindloop→core`、`bodylink→mindloop`、
`voicelink→mindloop`、`skillforge→tempomem+mindloop+bodylink`。核心 `tempomem` 不导入任何其他成员
—— numpy-only 契约。

---

## 2. 请求生命周期（大脑主干，单条话）

![请求生命周期](../assets/flow-request-lifecycle.svg)

<details><summary>mermaid 源 —— 编辑后请同步更新 SVG</summary>

```mermaid
flowchart TD
  U([话语 + 人 + 角色]) --> R{IntentRouter<br/>分类}
  R -- chat --> CH[闲聊回复] --> SPK
  R -- question --> Q[记忆查询<br/>引用节点 id] --> SPK[Speaker: 说]
  R -- task --> P[Planner LLM<br/>紧凑动词序列]
  P --> C[编译: 填 SubTask · 绑物到节点 id B9 · D3 manifest 门]
  C --> L[L5 偏好叠加<br/>manifest 门控]
  L --> PH{Phylax 安全<br/>角色 · 区域访问 · 隐私}
  PH -- 拦截 --> STOP[拒绝: 停 + 说]
  PH -- 放行 --> D[[可抢占调度循环<br/>见图 3]]
  D --> TR[(TraceStore: episodes 引用节点 id)]
  STOP --> TR
  SPK --> TR
```

</details>

两段式规划是不变量：**LLM 出文本动词 → 确定性编译** 把动词绑到记忆节点 id 并按 D3 manifest
逐动词门控。无在线规则规划回落。

---

## 3. 执行动态（调度循环：打断 · 重规划 · 问询人类）

![执行动态状态机](../assets/flow-execution-dynamics.svg)

<details><summary>mermaid 源 —— 编辑后请同步更新 SVG</summary>

```mermaid
stateDiagram-v2
  [*] --> NextStep
  NextStep --> CheckInterrupt: 还有子任务
  NextStep --> Done: plan 用尽

  CheckInterrupt --> Classify: 收件箱有话语
  CheckInterrupt --> Dispatch: 收件箱空
  Classify --> Answer: 闲聊/提问
  Answer --> CheckInterrupt: 恢复(保留游标)
  Classify --> Replan_New: 新指令(取代)
  Replan_New --> NextStep: 旧 ABORTED, 规划新
  Classify --> Aborted: 停止/取消
  Classify --> Replan_Fix: 纠正

  Dispatch --> NextStep: SUCCESS
  Dispatch --> Recover: FAILED(类型化错误)
  Recover --> Dispatch: RETRY / ADJUST / REROUTE
  Recover --> NextStep: SKIP
  Recover --> Ask: 无提示但可达
  Recover --> Escalate: 不可恢复 / 触顶

  Ask --> Resolve: Speaker 问, Listener 答(经 Phylax 复审)
  Resolve --> Dispatch: 答案解决, 预算--
  Resolve --> Escalate: 问询预算耗尽

  Escalate --> Done: 如实 停 + 说
  Aborted --> Done
  Done --> [*]
```

</details>

护栏：不可逆步骤（灶已开）做完或安全中止，绝不动作中途硬杀；取代在当前任务接近完成时确认；
澄清回答经 Phylax 复审（图 2）；问询预算 ≤2/任务。

---

## 4. 任务族流程（紧凑）

![任务族流程](../assets/flow-task-families.svg)

<details><summary>mermaid 源 —— 编辑后请同步更新 SVG</summary>

```mermaid
flowchart LR
  subgraph 导览[导览 / 导游]
    direction TB
    t0([带客人转转]) --> t1[plan: 每区域 navigate→present]
    t1 --> t2{私密区域?}
    t2 -- 是 且 访客 --> t3[跳过 + 说明]
    t2 -- 否 --> t4[present: 讲内容, 引 id]
    t4 --> t1
  end
  subgraph 家务[家务]
    direction TB
    c0([收纳/洗/擦/浇/倒垃圾]) --> c1[plan: 有序多步, 多物]
    c1 --> c2{成人专属动词?}
    c2 -- 孩子 --> c3[拦截]
    c2 -- 可 --> c4[开→放→启 / grasp→place 区域 / wipe / pour / dispose]
  end
  subgraph 寻物[寻找遗失物]
    direction TB
    f0([我钥匙在哪?]) --> f1{last_seen 已知且近?}
    f1 -- 是 --> f2[答 区域+时近, 引 id]
    f1 -- 陈旧 --> f3[含糊: 3h 前见过, 可能挪了]
    f1 -- 未知 --> f4[主动搜索: navigate→detect, 限 K]
    f4 --> f5{找到?}
    f5 -- 是 --> f2
    f5 -- 否 --> f6[如实未找到 = 成功]
  end
```

</details>

横切：每条口述声称都引用节点 id；陌生人问主人物品被隐私拦截；非主人导览跳过私密区域。

---

## 5. 数据与训练闭环（下一阶段规划）

运行期已全程埋点（每个决策都是引用节点 id 的 `TraceStore` episode）。闭环把这份"废气"经
skillforge 变成训练信号。

![数据与训练闭环](../assets/flow-data-training-loop.svg)

<details><summary>mermaid 源 —— 编辑后请同步更新 SVG</summary>

```mermaid
flowchart TD
  subgraph 运行期[运行期 — 生产]
    BR[mindloop 大脑主干<br/>图 2-3] --> EP[(TraceStore<br/>episodes, 带引用)]
  end
  EP --> DS[数据集整理<br/>trace → 标注样本:<br/>意图 · plan · 安全 · 结果 · 澄清]
  subgraph 实验室[skillforge — ENPIRE 实验室]
    DS --> ENV[Environment<br/>场景 + 目标回放]
    AU[PolicyAuthor<br/>现脚本 → 下步 LLM] --> RO
    ENV --> RO[Lab.rollout<br/>RolloutLog · AttemptTree]
    RO --> RW[Reward<br/>成功 · 安全 · 步数 · 诚实]
    RW --> EV[Evolution<br/>EvolutionResult: 最优策略/技能]
    EV --> CR[结晶<br/>技能 → Episteme 库]
    EV -.精炼.-> AU
  end
  CR --> GATE{eval 台<br/>run_eval · IntegrationReport.meets}
  GATE -- 通过 --> PROMOTE[提升 策略/技能<br/>进 Brain planner/overlay]
  GATE -- 不过 --> 实验室
  PROMOTE --> BR
  HOST[(主机 LLM<br/>Cosmos+Qwen)] -. 真 rollout/标注 .-> AU & DS
```

</details>

**闭环阶段 → 真实符号（skillforge）：** `Lab(env, author)` 用 `PolicyAuthor`（今为
`ScriptedAuthor`，下步主机上的 LLM author）驱动 `Environment` 回放 → `RolloutLog` /
`AttemptTree` → `Reward` → `EvolutionResult` → 把技能结晶进 Episteme 库 → `run_eval` /
`IntegrationReport.meets` 门控 → 提升进活的 `Brain`。闭环就是让机器人在我们场景上自我提升的关键；
指标（TASK-FAMILIES §4）就是那道门。

**已建 vs 规划：** 运行期 tracing ✅、eval 台 ✅、ENPIRE 行走骨架（`v0.1.0a0`，无网络，ScriptedAuthor）✅。
规划：从真 trace 整理数据集、主机 LLM PolicyAuthor、Episteme 结晶、提升回灌门。见 TASK-FAMILIES 落地顺序第 7 步。
