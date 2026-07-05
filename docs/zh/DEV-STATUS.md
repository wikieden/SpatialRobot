# DEV-STATUS — 统一开发计划（路由页）

> **汇总自** [TASK-FAMILIES.md](../en/TASK-FAMILIES.md) §8 × [INTEGRATION-E2E.md](../en/INTEGRATION-E2E.md) §6
> × [mindloop DEV-PLAN](../../mindloop/docs/zh/devplan/DEV-PLAN.md)。各原文档仍是各自领域的
> 单一事实源；本页只是路由/状态视图。更新于 **2026-07-04**。

## 1. 成员 × 状态

| 成员 | 已完成 | 进行中 | 下一步 |
|---|---|---|---|
| **tempomem** | 核心（融合/持久/查询/序列化）、区域、衰减、viz；**语义 Tier-1 已落**（edges/properties/events，migration 002）；**`last_seen` 已落**（步骤 2 ✅） | — | 动态场景 P4 供数（推迟） |
| **worldsense** | RGB(-D)→世界系 Detection，CLIP 在 extra 后；**VLMDetector 已落**（Qwen3-VL grounding → Box3D，主机实测 GO） | — | 真相机喂入（硬件） |
| **mindloop** | P0–P5 ✅；P6 ◐（eval+真LLM已验；Thor 待硬件）；P7 ◐（7.1 failover + 7.2 语音接缝 ✅）；动态场景 1–4 ✅；**TempoMem 改名已落**；**步骤 3/3b 已落**；**第 7 步软件面已落**（D-I 绑定歧义、D-D 宏展开、D-P 可靠度提示、P7.3 ListenerInterruptSource、P7.4 降级模式） | — | 硬件轨：Thor 切换；步内抢占（需 bodylink cancel/pause/resume） |
| **bodylink** | D3 manifest 框架、MockBody、Genesis sim、一致性套件、4 内置身体；**步骤 1 动词已落**（13 通用 + arm 子集） | — | D3 真机轨（BT/反射层）；cancel/pause/resume 握手（步内抢占） |
| **voicelink** | EndpointListener/Speaker（Qwen3-ASR/TTS）；打断 seam 经 mindloop `ListenerInterruptSource` 可达 | — | 本体流式 ASR+VAD 填 `audio_source`（硬件） |
| **skillforge** | ENPIRE 骨架、4 场景基线 GO ✅、**evolve 接受门已落**；六套件 GO；templates（D-Q）；数据闭环（curate/author/crystallize）；**D-G 复合奖励**；**D-P 记分卡**；语音导览示例 | — | 主机 LLM rollout 扩量（可选深化） |

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
                  提升门；学→用已闭环（learning_loop.py）。深化 2026-07-04 完成：
                  D-G 复合奖励（Weights 0.6/0.25/0.15 + composite_score；meets() 仍只按任务成功门控）
  7 ◐  第 7 步     软件面 2026-07-04 完成 —— 语音导览经 VoiceLoop（示例 GO）·
                  ListenerInterruptSource 语音打断 seam（P7.3）· P7.4 降级模式
                  （逐轮模式遥测 · 离线安全收紧 · 诚实离线提示）· D-I 绑定歧义
                  （只问一次、共享预算）· D-D 宏展开（macro_parent 入痕迹）·
                  D-P 记分卡+可靠度提示。余项（硬件）：流式 ASR+VAD 填充 ·
                  真相机感知喂入（动态场景 P4）
──────────────────────────────────────────────────────────────
T5 ✅ 2026-07-04 当日修订当日完成
  8 ✅ 步内抢占 —— BaseExecutorAdapter + SimDeviceAdapter 落 cancel/pause/resume
     握手（一致性套件加可选层）；Brain._drain 在流更新之间轮询收件箱：闲聊步内
     作答，中止/取代/纠正取消在途步；无握手身体保持 D-E 基线。真"随时打断"，
     D-E 彻底关闭。之后 sim 21/21 GO。
  9 ✅ D2 合并 —— tempomem.trace.TraceLog（独立文件或经 TempoMem.trace_log()
     共享 .smem；表 trace_episodes；trace 提交全程守 fuse-before-persist）；
     mindloop.TraceStore 变薄适配层（API 不变）。
  10 ✅ 小件打包 —— SubTask.negation_constraints（Replanner 盖
     not:<动词>:<失败id>，累积）· Phylax FMEA 文档（15 模式 × 防线）+
     conservative_policy() 预设 · Phylax.replace_policy 仅 adult 覆写 +
     访问控制规范（mindloop docs，EN+ZH）
T6 ✅ 2026-07-05 完成
  11 ✅ Qwen3-VL 之眼 —— worldsense.VLMDetector 填 Detector3D（2D grounding
     JSON → 深度反投影 → 相机系 Box3D → 复用 BoxDetectorAdapter 升维+编码）；
     传输注入、stdlib PNG、网络隔离测试。主机实测 GO（:8001，Qwen3-VL-32B-FP8）：
     眼→记忆接地+查回；实测坑已收编（裸对象回复、0-1000 归一化坐标）。
  12 ✅ 研究对 —— run_sim_batch（D-P 数据源 1：动词×回合走生产执行 seam →
     Scorecard；scorecard_nightly.py GO，弱 grasp 0.67 被披露）·
     rollout_scale.py（K 个种子任务过 evolve；基线 12/12；Cosmos 实测 4/4
     pass@1，每任务约 90 tokens）
真硬件阻塞：流式 ASR+VAD 麦克风填充 · 真相机喂入 · Thor 切换 · D3 真机身体轨
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

## 3a. 评审轮（2026-07-04，第 7 步批次）

对 10 个落地提交做独立评审：**0 CRITICAL · 1 HIGH · 3 MEDIUM · 3 LOW**；
无既定语义违规、无安全回归（全部审查点确认走逐轮 gate）。当日修复：HIGH-1
serve_mode 遥测漏入技能记分卡；MEDIUM-1 宏缺参静默降级（现在响亮告警）；
MEDIUM-2 零分并列盲信首位（现在异标签并列判歧义）。LOW 记为有意行为
（只问首个歧义；Weights 不强制和为 1；未答问询照扣预算）。

## 3b. 建时决策（按规划冻结约定逐行记）

- **D-I**："同分接近" = 达到榜首分 0.75 倍以内（无量纲比值）；绑定问询与 escalate 问询共享
  每任务预算；无 clarifier 时按 top-1 继续（留日志）。
- **D-D**：展开表 `deliver→navigate+offer`、`sweep→navigate+vacuum`、`mop→warn+navigate+mop+warn`；
  单遍展开，mop 原子核保留同名；trace 迁移 = 追加 `macro_parent` 列。
- **D-P**：记分卡落 skillforge（实验室侧）；planner 上下文披露线 0.8；从未尝试的桶保持
  `None`（防自证回避）。
- **P7.4**：离线 = `mode_probe() == "fallback"`；离线 Phylax 门为整体换入（只紧不松）；
  披露只追加到任务 `speak`（答案文本保持引用完整，`HandleResult.mode` 供 UX 层读取）。

## 4. 跟踪中未决（防散失）

| 项 | 状态 | 归属 |
|---|---|---|
| Phylax FMEA（按失效模式分析出策略） | ✅ 2026-07-04 完成（T5-10；phylax-fmea.md） | mindloop DEV-PLAN §8 |
| D2：L4 trace → tempomem core 合并 | ✅ 2026-07-04 完成（T5-9） | mindloop DEV-PLAN §8 |
| `negation_constraints` SubTask 字段 | ✅ 2026-07-04 完成（T5-10） | mindloop DEV-PLAN §8 |
| 云 → Thor 切换（P6 出口） | 待硬件 | mindloop DEV-PLAN P6 |
| P7.3–7.4 边缘栈 + 降级遥测 | 软件面 2026-07-04 完成（seam + P7.4）；本体 ASR/TTS/LLM 装机待硬件 | mindloop DEV-PLAN P7 |
| D3 真机身体轨（BT/反射层） | pending | bodylink 设计文档 |
| 屋主访问控制规范（运行时区域策略覆写） | ✅ 2026-07-04 完成（T5-10；access-control.md + replace_policy） | TASK-FAMILIES §1.2 |
