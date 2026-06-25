> 🌐 [English](../../en/research/roboos-robobrain-deep-dive-2026.md) · **中文**

# RoboOS 与 RoboBrain(BAAI/FlagOpen)· 专项深挖(2026-06-10)

> 两个并行研究 agent(网络 + GitHub + 通读 RoboOS 两个分支源码)，并复核了 Round-2 缺口探针
> ([embodied-brain-gaps-probe-2026.md](embodied-brain-gaps-probe-2026.md) §2.4)留下的两个监控触发器。
> 所有论断均附来源 URL；逐条注明可信度限定。

---

## 0. 执行摘要

1. **缺口探针留下的两个监控触发器于 2026-06-10 复核，均为绿灯(无需行动):"互补、未被覆盖"的结论维持。**
   - **RoboOS-NeXT / STEM 代码仍未开源**(issue [#73](https://github.com/FlagOpen/RoboOS/issues/73)
     持续 open，官方零回应)。
   - **RoboOS 共享记忆仍是 Redis 内存态** —— 更糟:已发布的 2.0 配置 `clear: true` →
     **master 每次启动执行 `FLUSHDB`**。没有任何向持久化存储迁移的迹象。
2. **"论文–代码鸿沟"是 RoboOS 的决定性事实。** 论文描述分层动态场景图(SAM+CLIP、RGB-D、增量更新、
   RAG 检索、TB 级记忆引擎)；实际发布的代码是**扁平 Redis hash `{name: {type, contains:[str]}}`** ——
   无坐标、无参考系、无时间戳、无置信度、无持久化。社区 issue
   [#76 "About Scene Graph"](https://github.com/FlagOpen/RoboOS/issues/76) 追问场景图在哪，至今无人回答 ——
   **这正是 `.smem` 所填补的未被满足的需求**。
3. **RoboOS 在衰减；RoboBrain 在繁荣。** RoboOS:571★，零 release/零 tag/零 CI/零测试，最后 push
   2025-12-18，完整 2.0 SaaS 版从未开源。RoboBrain:2.5-8B(2026-01)、2.5-4B(2026-03),Qwen3-VL
   架构，活跃至 2026-03,1,094★。BAAI 的投入明显转向了模型本身。
4. **RoboBrain 2.x 是 `mindloop` 近零成本的候选 Reasoner** —— 原生 Qwen2.5-VL / Qwen3-VL
   权重，`vllm serve` 即得 `CosmosReasonVerbalizer` 已经对接的同款 OpenAI 兼容端点；切换 =
   改 `base_url` + 模型名。最优打法是**补充而非替换**:Cosmos-Reason2 继续做 QA/语言化，
   RoboBrain 2.5 作为*空间输出头*(指点、空位放置、3D 轨迹、米制间隙校验、GRM 进度奖励)。
5. **BAAI 自家的生产架构验证了我们的架构**:外置场景图存储 + 每次调用序列化进 prompt + 无状态 VLM。
   RoboBrain 的"场景图更新"是一项*文本生成任务*(模型在输出里生成/修订场景图 JSON)，并非内置存储 ——
   持久化被明确下放给 OS 层。
6. **关注项:BAAI 智源大会 2026 于 6 月 12–13 日召开**(具身论坛 6 月 13 日；议题含世界模型 ORCA、
   "机器人通用大脑"、自进化)。本报告发布数日后即可能有 RoboBrain/RoboOS 新发布 —— 会后复查两个触发器。
   > ⚠️ **截至 2026-06-25 已逾期**:大会已结束；会后触发器复查(RoboBrain 2.5-32B 是否发布、
   > RoboOS-NeXT 代码、任何新的记忆/场景图能力)**尚未执行**。在刷新前，下文一切"截至 2026-06-10"的
   > 结论按约 2 周陈旧度对待。

---

## 1. RoboOS

### 1.1 定位、版本、成熟度

"Universal Embodied Operating System for Cross-Embodied and Multi-Robot Collaboration" —— BAAI +
北京大学。大脑–小脑分层:云端 MLLM 大脑(RoboBrain)+ 机上 MCP 技能"小脑" + Redis 共享记忆。
Apache-2.0。

| 版本 | 时间 | 产物 | 状态 |
|---|---|---|---|
| RoboOS 1.0 | 2025-04 | `main` 分支；[arXiv 2505.03673](https://arxiv.org/abs/2505.03673) | 已发布；YAML profile + Redis + Gradio |
| RoboOS 2.0 | 2025-06 智源大会发布("悟界"系列) | 仅轻量单机版公开([`stand-alone` 分支](https://github.com/FlagOpen/RoboOS/tree/stand-alone)) | 完整 SaaS 版**从未开源**;[#77](https://github.com/FlagOpen/RoboOS/issues/77) 无回应 |
| RoboOS-NeXT | 论文 2025-10:[arXiv 2510.26536](https://arxiv.org/abs/2510.26536) | STEM 统一记忆 | **代码未发布**;[#73](https://github.com/FlagOpen/RoboOS/issues/73) open、零回应 |

成熟度(`gh api`,2026-06-10):**571★ / 85 fork，零 release、零 tag、无 CI、无测试**，最后 push
2025-12-18，约 2.6k 行 Python，累计仅 12 个 issue,2025 年秋以后社区 issue/PR 基本无人回应。
Docker 路线已坏([#75](https://github.com/FlagOpen/RoboOS/issues/75):阿里云镜像 404，锁定的
FlagScale commit 已不存在)。

### 1.2 架构(代码核实，2.0 `stand-alone`)

```
用户 → Flask master :5000 → GlobalTaskPlanner:单次 prompt 调 RoboBrain2.0-7B
       (OpenAI SDK,vllm @ localhost:4567/v1)
       prompt = 机器人名 + 工具列表 + 整个 ENVIRONMENT_INFO Redis hash + 任务
     → JSON {subtask_list:[{robot_name, subtask, subtask_order}]}
     → 同 order 子任务按波次并行下发(Redis pub/sub "roboos_to_{robot}")
     → 波次之间 master 阻塞轮询 AGENT_BUSY(0.5 s)
机器人 slaver:注册(TTL 60 s + 心跳 30 s)
     → ToolMatcher(语义向量,每子任务最多 3 个工具)过滤 MCP 工具
     → ReAct 循环:LLM → 每步 1 次 MCP 工具调用
     → 每次工具调用后:额外一次 LLM 调用分类副作用
       {add_object | remove_object | position} → SceneMemory.apply_action → Redis
```

- 技能即 **MCP server**(stdio 本地或 streamable-HTTP 远程)，经 `list_tools()` 发现。
- 通信全走 Redis，经 [FlagScale](https://github.com/FlagOpen/FlagScale/blob/main/flagscale/agent/collaboration/collaborator.py)
  的 `Collaborator`。
- Planner 支持 `OpenAI` 与 `AzureOpenAI` 客户端 → 任意 OpenAI 兼容端点可用。
- **master 层无重规划** —— `master/agents/agent.py:103` 留着字面
  `# TODO: Task result should be refered to the next step determination.`，恢复逻辑只存在于
  slaver 的 ReAct 循环里。
- 论文宣称(RAG 分解、子任务图对象、"TB 级记忆引擎"、"<0.001 s 延迟")**在代码中没有对应物**:
  一条扁平 prompt、整数 `subtask_order`、busy 标志轮询。

### 1.3 记忆子系统 —— 三个不同的"RoboOS 记忆"

**(a) 已发布代码(过于简单)。** 扁平 Redis hash `ENVIRONMENT_INFO`:field = 位置名，
value = `{type, contains:[名字]}`，由 YAML 场景 profile 播种。唯一关系是单层 containment;
**无坐标、无参考系、无时间戳、无置信度**。查询接口 = `HGET`/`HGETALL`;planner 直接 `HGETALL`
**把整个 dict 内联进 prompt** —— 这就是大脑↔记忆接口的全部。更新:每次工具调用后**额外一次 LLM
往返**做三分类；错误一律 `print()` 后吞掉。共享单键 `"robot"` 意味着**多机器人互相覆写对方的
position/holding**。`clear: true` → master 启动即 `FLUSHDB`；无持久化。社区 PR
[#70](https://github.com/FlagOpen/RoboOS/pull/70)(带长短期分层 + 持久化的 `MemoryManager`)
未被合并。

**(b) 论文 1.0/2.0(愿景层)。** "Real-Time Shared Memory" = Spatial(floor/room/object 分层场景图，
节点含 position/affordance/label，多视角 RGB-D 经 SAM+CLIP 构建，增量更新)+ Temporal(执行历史、
工具日志)+ Robotic(关节状态、电量)。**两个分支的代码里均不存在。**

**(c) RoboOS-NeXT STEM(认真的设计 —— 未发布)。** `ℳ(t) = (𝒮, 𝒯, ℰ)`:
- **空间 𝒮**:Scene Tree(根 = 3D 重建 + 2D SLAM 地图 → region → **carrier** 节点)+ 每 carrier
  一张物体关系图；节点带位姿/属性/状态；边用 **7 个谓词 `{on,in,left,right,front,back,near}`**;
  Add/Remove/Move 经几何谓词函数触发**局部**关系重评估；初始化走 image→3D→SLAM 的 PnP 对齐。
- **时间 𝒯**:append-only 时序日志(状态增量 + 任务上下文 + 工具轨迹)；兼作跨机器人同步基底。
- **具身 ℰ**:每机器人心跳档案(定位、技能、电量、可用性)。
- 消融:去掉空间记忆，步数 11.6 → 58.1；去掉具身记忆 → **成功率 0%**。自述失败模式含
  **"长程记忆操作中的噪声累积"(30.2%)** —— 恰是融合仲裁器解决的问题。

### 1.4 部署与演示

已发布的 2.0 = 单机:一台机器跑 Redis + vLLM(RoboBrain2.0-7B @ `:4567/v1`)+ master + N 个
slaver；机器人以远程 MCP server 接入。演示:宇树 G1、松灵双臂、睿尔曼单臂；餐厅/家居/超市场景
(约 4 个容器、约 12 个物体)。

---

## 2. RoboBrain

### 2.1 谱系(全部 Apache-2.0)

| 模型 | 发布 | 架构 / 规模 | 备注 |
|---|---|---|---|
| RoboBrain 1.0 | 2025-02(CVPR 2025) | SigLIP + Qwen2.5-7B(LLaVA 式) | 规划主干 + A-LoRA(affordance)+ T-LoRA(轨迹);[arXiv 2502.21257](https://arxiv.org/abs/2502.21257) |
| RoboBrain 2.0 | 2025-06/07 | **Qwen2.5-VL** 3B/7B/32B(+7B-FP8) | [arXiv 2507.02029](https://arxiv.org/abs/2507.02029);repo 已改名 → [RoboBrain2.5](https://github.com/FlagOpen/RoboBrain2.5) |
| RoboBrain 2.5 | 8B 2026-01,4B 2026-03 | **Qwen3-VL** | "Depth in Sight, Time in Mind",[arXiv 2601.14352](https://arxiv.org/abs/2601.14352);32B 在 TODO，未发布 |
| RoboBrain-X0 | 2025-09(CoRL) | 基于 2.0-3B 的 VLA | SE(3) 末端位姿，统一动作词表 |
| RoboBrain-Dex / METIS | 2025-12 | VLA | 双手灵巧操作；[arXiv 2511.17366](https://arxiv.org/abs/2511.17366) |

截至 2026-06-10 没有 RoboBrain 3.0。HF 下载量不高(数百/30 天)；仓库为 "auto" 门控。

### 2.2 能力集

- **2.0**:指点/空间指代(像素坐标，含**空位指点**)、affordance bbox、轨迹(2D 关键点)、
  grounding、导航指点、长程 + 多机器人规划(为 RoboOS 产出子任务 DAG)、第一视角视频时序推理、
  **以文本生成任务形式做场景图构建/更新**、思考模式(`{thinking, answer}`)。
- **2.5 升级**:`(u,v,depth)` 关键点 → 经内参转 3D;**绝对米制推理**("悬停在上方 1–5 cm");
  避碰有序 **3D 轨迹**;**GRM 稠密时序价值估计**(任务进度 [-1,1]、成败估计 —— 可作 VLA RL
  的实时奖励信号)。

### 2.3 训练(浓缩)

1.0:ShareRobot(23 个 OXE 数据集 → 103 万规划 QA / 6.5K affordance / 6.9K 轨迹)。
2.0:480 万基础 → 22.4 万具身(多视角、3D affordance、**场景图**)→ 19.5 万 CoT SFT →
**4.5 万 GRPO RFT**(Reason-RFT)。2.5:共约 1240 万；时序约 350 万中 ≈60% 真机数据；
两阶段 + 15% 回放；NVIDIA + 摩尔线程跨加速器训练(FlagScale)。

### 2.4 Benchmark(BAAI 自测，FlagEvalMM；限定见下)

| 模型 | BLINK | CV-Bench | EmbSpatial | RoboSpatial | Where2Place | ShareRobot-Afford | Traj-DFD↓ |
|---|---|---|---|---|---|---|---|
| RoboBrain2.0-32B | 83.6 | 83.9 | 78.6 | **72.4** | **73.6** | **35.3** | **0.237** |
| RoboBrain2.0-7B | **84.0** | **85.8** | 76.3 | 54.2 | 63.6 | 28.1 | 0.551 |
| Gemini-2.5-Pro | 81.8 | 84.6 | **78.7** | 59.9 | 42.4 | 10.3 | 0.767 |
| GPT-4o | 77.9 | 78.6 | 71.9 | 44.4 | 20.4 | 6.0 | 0.685 |
| Cosmos-Reason1-7B | 68.6 | 74.7 | 65.2 | 38.8 | 5.5 | 10.0 | 0.852 |

规划:Multi-Robot-Plan 81.5(7B)/ 80.3(32B),GPT-4o 74.5,Cosmos-Reason1 33.7。2.5:
2D 空间均分 75.8(Gemini 66.1),TraceSpatial 44%(Qwen3-VL 6%)。

**限定:** 全部数字为厂商自测；Cosmos 一列是 **Cosmos-Reason1-7B，不是 Reason2-8B** ——
截至本日期，与 Reason2 的公开对测在任何来源中都不存在。

### 2.5 推理服务

原生 Qwen-VL 家族 → **vLLM/SGLang 开箱即用**,OpenAI 兼容。BAAI 自测命令
`vllm --limit-mm-per-prompt image=18 --max-model-len 32768`。显存(BF16 ≈ 2×参数量):2.5-8B ≈
18–20 GB,2.0-32B ≈ 70 GB —— 均可放进 RTX PRO 6000 96 GB。3B 标榜面向边缘，有 FP8 7B,
**但任何渠道都没有官方 Jetson/Thor 部署指南** —— Cosmos-Reason2 在 Thor 上有 NVIDIA 一方支持，
这在我们的目标机载算力上是实打实的生态优势。

### 2.6 状态性(定论)

**RoboBrain 模型本身每次查询无状态。** "场景图更新" = 模型在喂入观测后能*在输出文本中生成/修订
场景图 JSON*(训练任务)。持久化在模型之外，在 RoboOS 的 Redis 里；每次大脑调用都把场景图重新
序列化进 prompt(`Ms ⊕ Mt ⊕ Sr ⊕ Mr ⊕ T`)。**BAAI 的生产架构 = 外置场景图存储 + 序列化进
prompt + 无状态 VLM —— 与我们完全一致。**

---

## 3. 对 Chronotope 栈的启示

### 3.1 我们直接胜出之处(对比 RoboOS 已发布代码)

1. **表示**:世界系带类型节点/边 + SQLite 持久化，对比易失 Redis 里的名字字符串 + 单层 `contains`。
2. **融合**:检测级 fuse-before-persist 仲裁器(循环内无 LLM)，对比每次工具执行追加一次 LLM
   三分类且错误被吞。STEM 自己的失败分析(30.2% = 记忆噪声累积)反向验证仲裁器是正确投资。
3. **查询**:关系 → 意图 → 语义的分层路由 + `#id` 引用序列化，对比 `HGETALL` 整体倾倒进
   prompt(超出玩具场景必然失效)。
4. **感知落地**:真实的相机→世界提升，对比代码中从未接触 RGB-D 的 YAML 播种符号世界。

### 3.2 值得偷学(按优先级)

1. **具身记忆 ℰ** —— 心跳更新的机器人档案(技能/电量/可用性)作为一等记忆分区；STEM 消融:
   去掉它 → 成功率 0%。Brain2Robot 一旦调度 >1 个执行体就需要。
2. **时间事件日志** —— `.smem` 里加 append-only 场景增量日志；低成本买到 lifelong/回放 +
   重规划上下文；也是 RoboBrain 类模型被训练去消费的 `Mt`。
3. **carrier 局部关系重评估** —— 关系按 carrier 局部重算而非全局；采纳 **7 谓词词表
   `{on,in,left,right,front,back,near}`** 作兼容目标(RoboBrain 模型按它训练)。
4. **`tempomem` 做成 MCP server** —— 把 query/answer/commit 暴露为 MCP 工具；即插即用于
   RoboOS 式编排器；issue #76/#73 就是对开源场景图记忆组件的活需求。
5. 波次调度(`subtask_order` + busy 等待)—— 若将来要管机群，可平凡复刻。

### 3.3 Reasoner 选型:RoboBrain vs Cosmos-Reason2

- 集成成本 ≈ 零(同款 OpenAI 兼容端点；切换 = `CosmosReasonVerbalizer` 配置里改 `base_url` +
  模型名)。
- 画像不同:RoboBrain = **输出落地型**(点/bbox/3D 轨迹/米制校验/进度值);Cosmos-Reason =
  **CoT 判断型**(物理合理性、QA、规划批判)。
- 对序列化场景图做 `Brain.ask` 两者皆可；要可执行的空间输出只有 RoboBrain 受过训练；
  在 Thor 上 Cosmos 有一方支持、RoboBrain 无任何文档。
- **建议:补充而非替换。** 第二个 vLLM 端点 + 薄适配器 = RoboBrain 2.5 做空间输出头
  (指点、放置、轨迹、米制间隙、GRM 进度)，与 Cosmos QA 并存。同时是 eval 套件天然的 A/B 对。
- **与景观报告对齐:** 景观报告指出 *Cosmos-Reason2 仓库已无维护、被 Cosmos 3 取代* —— 那讲的是
  **仓库的更新节奏**，不是模型可用性。已集成的 `Cosmos-Reason2-8B` 权重做 QA 仍然好用，故"保留
  Cosmos-Reason2"成立；但**别指望上游仓库更新** —— 把 Cosmos 3(与 RoboBrain 2.5)作为后继，
  eval 套件应开始与之做 A/B。

### 3.4 从他们栈里提炼的接口指引

1. 序列化**上下文包**(场景 ⊕ 近期动作反馈 ⊕ 机器人状态)，而非只有场景 —— 匹配 RoboBrain 类
   模型被训练消费的输入。
2. RoboBrain 返回**像素/相机系坐标**(2.0 是 (x,y);2.5 是 (u,v,d)+内参)—— 观测要保留
   参考系/内参元数据，模型输出才能提升回世界系节点。
3. 2.5 的绝对米制推理奖励序列化**米制几何**(世界系位置、尺寸、支撑面高度)，不止拓扑。
4. 空位指点单帧裸图即可工作 —— 记忆层的差异化价值在**被遮挡/视野外空间与跨时间事实**,
   单帧模型无从知晓。

### 3.5 监控触发器(2026-06-10 更新)

| 触发器 | 状态 | 下次检查 |
|---|---|---|
| RoboOS-NeXT STEM 代码发布([#73](https://github.com/FlagOpen/RoboOS/issues/73)) | 🟢 仍未发布 | 智源大会后(2026-06-12/13)；此后每季度 |
| RoboOS 2.0 Redis → 持久化存储 | 🟢 无变化(启动仍 `FLUSHDB`) | 同上 |
| 新增:智源大会 2026 具身论坛(06-13:ORCA 世界模型、"机器人通用大脑") | ⏳ 数日后 | 会后复跑上两项检查 |
| 新增:RoboBrain 2.5-32B 发布(repo TODO) | 未发布 | 顺带检查 |

---

## 4. 来源

RoboOS:[repo](https://github.com/FlagOpen/RoboOS) · [`stand-alone` 分支](https://github.com/FlagOpen/RoboOS/tree/stand-alone) · [arXiv 2505.03673](https://arxiv.org/html/2505.03673v2) · [RoboOS-NeXT 2510.26536](https://arxiv.org/html/2510.26536v1) · [FlagScale Collaborator](https://github.com/FlagOpen/FlagScale/blob/main/flagscale/agent/collaboration/collaborator.py) · issues [#73](https://github.com/FlagOpen/RoboOS/issues/73)/[#75](https://github.com/FlagOpen/RoboOS/issues/75)/[#76](https://github.com/FlagOpen/RoboOS/issues/76)/[#77](https://github.com/FlagOpen/RoboOS/issues/77)/[PR #70](https://github.com/FlagOpen/RoboOS/pull/70)
RoboBrain:[RoboBrain2.5 repo](https://github.com/FlagOpen/RoboBrain2.5)(含归档 `rb_v2.0/README.md`)· [RoboBrain 1.0](https://github.com/FlagOpen/RoboBrain) · [arXiv 2507.02029](https://arxiv.org/abs/2507.02029) · [arXiv 2601.14352](https://arxiv.org/abs/2601.14352) · [arXiv 2502.21257](https://arxiv.org/abs/2502.21257) · [ShareRobot](https://github.com/FlagOpen/ShareRobot) · [RoboBrain-X0](https://github.com/FlagOpen/RoboBrain-X0) · [项目页](https://superrobobrain.github.io/) · [HF BAAI](https://huggingface.co/BAAI/RoboBrain2.0-7B) · [智源大会 2026 议程](https://hub.baai.ac.cn/view/55074)
