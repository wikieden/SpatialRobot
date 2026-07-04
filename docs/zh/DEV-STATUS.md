# DEV-STATUS — 统一开发计划（路由页）

> **汇总自** [TASK-FAMILIES.md](../en/TASK-FAMILIES.md) §8 × [INTEGRATION-E2E.md](../en/INTEGRATION-E2E.md) §6
> × [mindloop DEV-PLAN](../../mindloop/docs/zh/devplan/DEV-PLAN.md)。各原文档仍是各自领域的
> 单一事实源；本页只是路由/状态视图。更新于 **2026-07-02**。

## 1. 成员 × 状态

| 成员 | 已完成 | 进行中 | 下一步 |
|---|---|---|---|
| **tempomem** | 核心（融合/持久/查询/序列化）、区域、衰减、viz；**语义 Tier-1 已落**（edges/properties/events，migration 002）；**`last_seen` 已落**（步骤 2 ✅） | — | 动态场景 P4 供数（推迟） |
| **worldsense** | RGB(-D)→世界系 Detection，CLIP 在 extra 后 | — | 动态场景 P4 实时感知（推迟） |
| **mindloop** | P0–P5 ✅；P6 ◐（eval+真LLM已验；Thor 待硬件）；P7 ◐（7.1 failover + 7.2 语音接缝 ✅）；动态场景 1–4 ✅；**TempoMem 改名已落**；**步骤 1 `_VERB_TABLE` + place@location 已落** | — | 步骤 3（Phylax 扩展）、3b（执行动态） |
| **bodylink** | D3 manifest 框架、MockBody、Genesis sim、一致性套件、4 内置身体；**步骤 1 动词已落**（13 通用 + arm 子集） | — | D-P 技能记分卡（随步骤 6） |
| **voicelink** | EndpointListener/Speaker（Qwen3-ASR/TTS） | — | 步骤 7：真语音打断（流式 ASR+VAD，推迟） |
| **skillforge** | ENPIRE 骨架、4 场景基线 GO ✅、**evolve 接受门已落**（held-out 严格改进） | 步骤 4 部分（scenario 结构） | 步骤 4 全量：6 族套件 + 新指标 + regions |

## 2. 统一执行顺序（依赖链）

> **规划已冻结（2026-07-02）**——17 项 D-决策已饱和。新设计问题一律建时决策（此处记一行）；
> 仅安全关键项可重开 TASK-FAMILIES。

```
T1 ──────────────────────────────────────────────────────────── 机械、低风险
  0 ✅ WIP 落地（TempoMem 改名 + 语义层 + gate）                [2026-07-02 完成]
  1 ✅ 动词       2026-07-02 完成 —— 13 动词（manifest+arm 子集）· _VERB_TABLE · place@location eff
  2 ✅ 记忆       2026-07-02 完成 —— Tier-1 已核验 · last_seen 落地（+5 测试）·
                  current_occupants = D-B 组合查询（无需新方法）
T2 ──────────────────────────────────────────────────────────── 最高风险批
  3 ✅ 安全       2026-07-02 完成 —— named_params · D1 参数门 · D-A 服务区域 · Q6 默认 · D-K 菜单/过敏（fail-closed）
  3b ✅ 动态      2026-07-02 完成 —— 3 个 TDD 切片逐个绿提交：收件箱+分类器 ·
                  步间打断（中止/恢复/取代/纠正，Phylax 复审）·
                  Clarifier + 每任务问询预算 + ESCALATE 路由（共 150 测试）
T3 ──────────────────────────────────────────────────────────── 收口批
  4a ✅ 评测台    2026-07-02 完成 —— 11 族指标 + required_metrics(D-F) · runner 内 L1
                  不变式(D-N) · 六套件（导览/家务/寻物/保洁/接待/执行动态）基线 GO，
                  已练指标全 1.0
  4b ✅ 评测台    2026-07-02 完成 —— load_role/effective_verbs/vet_role(D-O) · templates.py
                  （tidy/privacy/find 生成器，seed 确定，19 变体 GO —— D-Q）
T4 ──────────────────────────────────────────────────────────── 验证批
  5 ✅ 真 LLM     2026-07-04 完成 —— 主机 172.16.1.12（新 IP），Cosmos-Reason2-8B 经 vLLM，
                  temp=0+seed：4/4 GO（意图/规划/策略/引用全 1.0），单轮 p95 约 0.25 秒
      ∥ E2E phase 3 ✅ sim 身体（Genesis）：21/21 物理场景 GO（约 48 秒，2026-07-04）
──────────────────────────────────────────────────────────────
  6 ✅ 数据闭环   2026-07-04 完成 —— curate（按户隔离、语音脱敏、拒跨户合并）· LLMPolicyAuthor
                  （BYO Verbalizer）· crystallize（learned 卡、零 safety 键 —— D-L）· gate.py
                  提升门；学→用已闭环（learning_loop.py）。余下深化：D-G 复合奖励塑形
  7 ▢  推迟       语音导览/真语音打断（P7.3–7.4）· 主动感知（动态场景 P4）
```

T1–T3 可自主、无网络；每批以测试全绿+提交收尾。仅步骤 5 需主机。

## 3. Review 发现（2026-07-02 整理轮）

1. **执行顺序偏离 §8 编号**（2 先于 1）——无害（1/2/3 互相独立），但步骤 4 套件在 1+3+3b 落地前只能是空壳。
2. **改名是跨仓协调变更**——`SpatialMemory → TempoMem` 硬切（无别名）。已一次性落遍 6 成员 + root 文档；
   扫尾核验（`grep SpatialMemory` → 代码引用 0）。
3. **skillforge `gate.py` 归属步骤 6** 而非步骤 4——是 SkillOpt 借用的 evolution 循环 held-out 接受门
   （见 skillforge/docs/en/skillopt-borrow-decision.md），属提前落地。
4. **文档状态漂移已修**——INTEGRATION-E2E phase 1 拆为 1a（4 场景基线，GO ✅）/ 1b（6 族套件，进行中）；
   TASK-FAMILIES §8 已加状态标记。
5. **规划/代码比警报 → 规划冻结（2026-07-02）**——约 2600 行规划、17 项 D-决策、任务族代码 0 行。
   已达饱和：此后设计问题一律建时决策（此处记一行）；执行按 T1–T4 批次（§2）；步骤 3b 带显式
   TDD/隔离纪律；步骤 4 拆 4a/4b。

## 4. 跟踪中未决（防散失）

| 项 | 状态 | 归属 |
|---|---|---|
| Phylax FMEA（按失效模式分析出策略） | open | mindloop DEV-PLAN §8 |
| D2：L4 trace → tempomem core 合并 | deferred | mindloop DEV-PLAN §8 |
| `negation_constraints` SubTask 字段 | 未加（B2R 对齐项） | mindloop DEV-PLAN §8 |
| 云 → Thor 切换（P6 出口） | 待硬件 | mindloop DEV-PLAN P6 |
| P7.3–7.4 边缘栈 + 降级遥测 | deferred | mindloop DEV-PLAN P7 |
| D3 真机身体轨（BT/反射层） | pending | bodylink 设计文档 |
| 屋主访问控制规范（运行时区域策略覆写） | flagged | TASK-FAMILIES §1.2 |
