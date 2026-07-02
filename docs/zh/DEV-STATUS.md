# DEV-STATUS — 统一开发计划（路由页）

> **汇总自** [TASK-FAMILIES.md](../en/TASK-FAMILIES.md) §8 × [INTEGRATION-E2E.md](../en/INTEGRATION-E2E.md) §6
> × [mindloop DEV-PLAN](../../mindloop/docs/zh/devplan/DEV-PLAN.md)。各原文档仍是各自领域的
> 单一事实源；本页只是路由/状态视图。更新于 **2026-07-02**。

## 1. 成员 × 状态

| 成员 | 已完成 | 进行中 | 下一步 |
|---|---|---|---|
| **tempomem** | 核心（融合/持久/查询/序列化）、区域、衰减、viz；**语义 Tier-1 已落**（edges/properties/events，migration 002） | — | 步骤 2 收尾：核验/补齐 `last_seen`、`last_changed`、`current_occupants` |
| **worldsense** | RGB(-D)→世界系 Detection，CLIP 在 extra 后 | — | 动态场景 P4 实时感知（推迟） |
| **mindloop** | P0–P5 ✅；P6 ◐（eval+真LLM已验；Thor 待硬件）；P7 ◐（7.1 failover + 7.2 语音接缝 ✅）；动态场景 1–4 ✅；**TempoMem 改名已落** | — | 步骤 1（`_VERB_TABLE`）、3（Phylax 扩展）、3b（执行动态） |
| **bodylink** | D3 manifest 框架、MockBody、Genesis sim、一致性套件、4 内置身体 | — | 步骤 1：manifest/mock/sim 加约 12 新动词 |
| **voicelink** | EndpointListener/Speaker（Qwen3-ASR/TTS） | — | 步骤 7：真语音打断（流式 ASR+VAD，推迟） |
| **skillforge** | ENPIRE 骨架、4 场景基线 GO ✅、**evolve 接受门已落**（held-out 严格改进） | 步骤 4 部分（scenario 结构） | 步骤 4 全量：6 族套件 + 新指标 + regions |

## 2. 统一执行顺序（依赖链）

```
0 ✅ WIP 落地（TempoMem 改名 + 语义层 + gate）                  [2026-07-02 完成]
1 ▢  动词        bodylink manifest/mock/sim + mindloop _VERB_TABLE + place 区域 eff
2 ◐  记忆        Tier-1 已落；核验/补齐 last_seen · last_changed · current_occupants
3 ▢  安全        Phylax：D-A robot_service · D1 (verb,param) 门 · Q6 区域默认 · D-K menu.py
3b ▢ 动态        InterruptSource · BargeClassifier(D2) · Clarifier+ASK_HUMAN(D3) · 问询预算
4 ◐  评测台      Scenario.regions · EvalReport/Thresholds 字段 · 6 套件 · required_metrics(D-F)
                 → 按 §7e 门槛基线 go/no-go                    [真断言依赖 1+3+3b]
5 ▢  真 LLM      主机 192.168.31.89，temp=0+固定 seed          [需 GPU 批准]
     ∥ E2E phase 3：sim 身体（Genesis）通跑                     [可自主]
6 ◐  数据闭环    trace→数据集 · LLM PolicyAuthor · Episteme 结晶 · 提升门
                 （gate.py 作为接受门件已提前落）
7 ▢  推迟        语音导览/真语音打断（P7.3–7.4）· 主动感知（动态场景 P4）
```

步骤 1–4 可自主、无网络。仅步骤 5 需主机。步骤 4 的 6 套件须 1+3+3b 就位后断言才是真的。

## 3. Review 发现（2026-07-02 整理轮）

1. **执行顺序偏离 §8 编号**（2 先于 1）——无害（1/2/3 互相独立），但步骤 4 套件在 1+3+3b 落地前只能是空壳。
2. **改名是跨仓协调变更**——`SpatialMemory → TempoMem` 硬切（无别名）。已一次性落遍 6 成员 + root 文档；
   扫尾核验（`grep SpatialMemory` → 代码引用 0）。
3. **skillforge `gate.py` 归属步骤 6** 而非步骤 4——是 SkillOpt 借用的 evolution 循环 held-out 接受门
   （见 skillforge/docs/en/skillopt-borrow-decision.md），属提前落地。
4. **文档状态漂移已修**——INTEGRATION-E2E phase 1 拆为 1a（4 场景基线，GO ✅）/ 1b（6 族套件，进行中）；
   TASK-FAMILIES §8 已加状态标记。

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
