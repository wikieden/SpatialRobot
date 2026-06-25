> 🌐 [English](../../en/research/embodied-brain-gaps-probe-2026.md) · **中文**

# 二轮深挖：空间记忆 GTM 付费意愿 + RoboOS/InternRobotics 场景图记忆（2026）

> 多 agent workflow 深挖 + 对抗验证。回填 VISION 的 OQ-1（首个付费方）、OQ-5（RoboOS 是否覆盖）。数字按 verdict 处理。

---

# Chronotope 二轮深挖报告：商业付费意愿 与 RoboOS/InternRobotics 场景图记忆

> 本报告基于两个经对抗验证（adversarial verification）的深挖数据集撰写。所有数字与推论均忠实标注其 verdict：`confirmed`（已证实）/`updated`（数字证实但推论需修正）/`uncertain`（来源不可靠或不适用）/`refuted`（被推翻，不采用）。被 refuted 的数字一律不作为论据，仅作为"反面教训/认知纠偏"列出。对应 VISION 文档为 `docs/zh/VISION.md`（OQ-1 见 §6.1，OQ-5 见 §7.2）。

---

## 1. 空白A：空间记忆商业付费意愿 / GTM

### 1.1 结论（一句话）

结构化空间记忆 / 3D 场景图记忆**存在真实的企业付费需求，但目前全球尚无一家以"纯软件 SDK 形式"商业化并有公开营收披露的先例**。最可行的商业形态按落地难度排序为：① 硬件捆绑模块（per-device）② RobOps 平台增值订阅（per-robot/月）③ 云服务 API（per-query）④ 纯软件 SDK 企业授权（路径最长、最难验证）。这与 VISION §6.1 "当前没有任何已验证的付费方"的诚实标注完全一致——本次深挖**没有推翻该判断，但补足了可类比的商业模式样本与定价锚点**。

### 1.2 证据：正面信号（付费意愿确有其事）

| 证据 | 关键事实 | verdict / 可信度 | 对我们的含义 |
|---|---|---|---|
| **Slamcore（空间感知 SDK）** | Imperial College 出身，累计融资接近 $25M（CBInsights/Tracxn 记 $26M，含 4 轮）；2022 年 Series A 时 "100+ 公司 onboarded"（多为 POC 阶段）；2024 年 3 月推出 Slamcore Aware 硬件+软件捆绑包（针对仓储叉车/AGV），per-device 销售 | 融资与客户数 **confirmed**；"证明独立商业价值"的推论 **uncertain**——转向硬件捆绑恰恰暗示纯 SDK 模式遇阻。**"被 Oxa 收购"子声明 refuted**（被收购的是 StreetDrone，Slamcore 仍独立） | 空间感知技术企业愿付费 ✅；但纯软件→硬件捆绑的转向是最重要的反向警示 |
| **Mem0（LLM 文本记忆，最强类比）** | YC S24；2025-10 完成 $24M 融资（Basis Set 领投，YC/Peak XV 参投）；定价 Hobby 免费 / Starter $19 月 / Pro $249 月 / Enterprise 定制；API 调用 Q1 2025 3500 万 → Q3 1.86 亿（月增 ~30%）；AWS Strands Agent SDK 选其为唯一记忆提供商 | 数字 **confirmed**（官方 Series A + TechCrunch 一手证实）；**"可直接类比到空间记忆 SDK" 的推论被 updated（部分 refuted）** | "记忆即服务"模式被验证；但**不可直接照搬增速/TAM**（见 §1.5 风险） |
| **Manifold Tech / Odin 1（深圳，HKU MaRS Lab）** | 唯一把"空间记忆"写进产品名的硬件+算法捆绑（LiDAR+相机+IMU+MindSLAM）；完成"近亿元人民币 Pre-A+"（Matrix Partners China + Gobi GBA 联合领投，规模比初报"七位数"更大）；已在 Foxtech 第三方分销上架；2026 北京人形半马支持 Unitree H1 全自主完赛 | 融资规模 **updated（被低估）**；量产有实质进展 **confirmed**；"全球首个" **uncertain（自我声明，无第三方验证）** | per-device 硬件捆绑路线在中国已有融资+量产实证，是最近落地的形态 |
| **机器人运维中间件（InOrbit / Formant / Foxglove）** | InOrbit ~$500/机器人/月（3 台以下免费）；Formant $50–500+/机器人/月（VnRobo 参考 ~$250）；Foxglove Pro $20 起、$45/设备/月，2026-04 主动降价扩采 | 定价区间 **updated（基本成立但采购方错位）**——数据来自非官方聚合站，且面向"机器人运营商"而非"开发商/OEM" | per-robot/月 SaaS 模式被验证 ✅；但**付费主体与我们的买家（开发商/OEM）不同**，不能直接套价 |
| **向量数据库（Pinecone/Weaviate/Qdrant）** | 证明"基础设施即服务"模式可行，consumption-based 定价 + 生态锁定 | 商业化方向 **partially supported**；**但具体营收数字全部 refuted**（见 §1.5） | 仅可作为"基础设施记忆层可商业化"的方向佐证，**不可引用任何具体营收数字** |
| **Tera AI（纯软件空间导航）** | SF，Google X 前 ML 负责人创立；2025-03 隐身融资 $7.8M（Felicis/Inovia/Naval Ravikant）；主张"硬件无关纯软件空间推理，机器人的 iOS"，客户为已有硬件的 OEM | **medium**（无营收，需 2025–2026 验证） | 投资者对"纯软件空间推理 per-robot 授权"有信心，但产品尚未变现 |

### 1.3 证据：反面信号（为何"纯 SDK 付费"仍未被验证）

- **最接近我们定位的空间记忆 OSS 全部免费、零付费案例**：RobotMem（24★）、eMEM/EMOS（Automatika，2★，MIT）均含空间检索（R-tree）+ 语义检索（HNSW）+ 时序检索（SQLite），与我们高度同形，但**无付费层、无商业用户披露**。`evidence_strength: strong`。
- **头部机器人公司全栈自建、不采购**：Figure（Helix）、Tesla Optimus、AgiBot 均视感知/记忆为核心差异化，自研。行业共识："感知/定位/记忆**不是差异化时采购，是差异化时自建**"。
- **NVIDIA Isaac 免费提供竞争性基础工具层**（400+ 团队使用，含几乎所有头部人形公司），压低底层工具的可收费空间。
- **直接证据缺失（核心反面）**：搜索未发现任何公司把"3D 场景图记忆/语义空间记忆图"单独作为 SDK 商品出售并有公开营收。学术系统（DynaMem/ReMEmbR/RoboMemory）均 OSS 无商业计划；Manifold 做了但**捆绑硬件**。`evidence_strength: strong`。
- **中国市场当前付费模式仍是整机**：艾瑞《2025 中国商用具身智能白皮书》+ 东方财富研报：当前以一次性整机销售为主、软件为辅；演进路径 整机 → 整机+软件订阅 → RaaS → 按效果付费。空间记忆目前**作为附属功能打包，尚未单独定价**（`medium`）。

### 1.4 可类比的商业模式（按与我们的相似度排序）

1. **ARBE「机器人感知的高通」模式**（与空间记忆 SDK 最相似）：感知/定位/记忆作为可授权的底层 IP 卖给 OEM。结构最贴合"中立第三方记忆标准"，但需"记忆是差异化但 OEM 不愿自建"的前提成立。
2. **Slamcore Aware：硬件捆绑 per-device**（落地最快）：用硬件锚定提高纯软件转化率——Slamcore 自身从纯 SDK 转向捆绑，是给我们的最大经验。Manifold Odin 1 已在中国跑通融资+量产。
3. **Mem0：云 API per-query "记忆即服务"**（叙事最性感、客户基数最小）：模式可复用，但机器人 OEM 客户数量级远小于 LLM 开发者，增速不可类比。
4. **InOrbit/Formant：per-robot/月 RobOps 订阅**（定价锚点最清晰）：$50–500/机器人/月被验证，但买家是运营商而非开发商——我们若走此路需绑定高频运维痛点。

### 1.5 关键风险点（被对抗验证击中的错误类比 / 数字，禁止再引用）

- **Pinecone「2024 营收 $26.6M」与 Weaviate「$200M ARR」均 refuted**：Pinecone 营收来自 GetLatka（非官方聚合，官方从未披露），且 2025 年已降至 $14M；不同来源 $14M/$120M/$380M 互相矛盾。Weaviate「$200M」实为 Series B **估值**被误标为 ARR，真实营收量级约 $12–21M（GetLatka 记 $12.3M）。**这两组数字不得出现在任何对外材料中。**
- **Mem0 增速「可直接类比」refuted**：Mem0 服务 10 万+ 低门槛开发者、高并发长尾 SaaS；空间记忆 SDK 面向机器人 OEM，集成周期 3–12 个月、采购由工程/采购部门主导。用 Mem0 的 1.86 亿 API/季增速做 TAM 或增速基准会**高估 1–2 个数量级**。
- **「具身软件平台 $18,000–45,000/机器人/年」uncertain**：来自 Research Intelo 付费报告，方法论不透明，无法交叉验证；该区间覆盖整个软件平台（技能管理/OTA/遥测），不代表记忆子层单独定价。一手 RaaS 数据为整包不可拆（Figure RaaS ~$1,000/月、1X NEO $499/月、人形 RaaS $2,500–8,000/月）。
- **InOrbit/Formant 定价「直接套用」需打折**：区间成立但来自非官方估算站，且采购方错位（运营商≠开发商），记忆子层能拿到的价值份额更低。

### 1.6 对我们 GTM 的建议（谁付费 / 什么形态）

**与 VISION §6.1 / §6.2 / §6.4 的时序一致，本次深挖给出更具体的回填：**

- **谁付费（首个 ICP）**：坚持 VISION §6.1 的假设性画像——**不自研 S2、但有长时/多班次空间记忆需求的纯执行器本体厂或开源大脑团队**。本次深挖补充：**Manifold Odin 1 的客户群（已有硬件、缺记忆软件的中小机器人/无人机厂）是最贴近的真实参照样本**；而 Figure/Tesla/AgiBot（自建派）应被明确排除在首批之外。
- **付费形态（按"先做哪个"排序）**：
  1. **P3 起：PoC 咨询 + 企业层 license**（与 VISION §6.2(c) 默认倾向一致）——客户基数小、销售周期长，但 ACV 高，先用咨询打通真实需求。
  2. **若要更快变现，优先考虑"轻硬件捆绑/参考硬件 + .smem"**而非纯 SDK——Slamcore 转向与 Manifold 量产是双重经验：**纯软件转化难，硬件锚定提升采购确定性**。
  3. **托管 API 作收入来源（非护城河）**——可做，但客户基数小，不应作为 P1–P2 主线（与 VISION §6.4 "P1–P2 不做企业销售"一致）。
- **对外口径纪律**：对外谈付费意愿时，**只引用 confirmed 的 Slamcore（融资/客户）、Mem0（融资/定价/调用量）、Manifold（融资/量产）三组事实**；**禁止引用 Pinecone/Weaviate 营收数字、禁止用 Mem0 增速推 TAM、禁止引用 Research Intelo 的 $18K–45K**。

---

## 2. 空白B：RoboOS / InternRobotics 是否自带场景图记忆

### 2.1 结论：互补，不是被覆盖（当前架构下）

国内主要开源"一脑多形"栈目前**均未提供可替代 `.smem` 的独立持久化结构化场景图存储层**。最接近的竞品是 **BAAI RoboOS**：其 Real-Time Shared Memory 确实含层次化动态场景图，但**底层用 Redis 内存存储（重启即失，非磁盘持久化）**，定位是多机器人实时协调中间件，而非可嵌入的单体记忆核心。**两者在当前架构下构成互补接口关系（`.smem` 可作为 RoboOS 的持久化后端），而非替代关系。** `evidence_strength: strong`。

**最大近期风险**：RoboOS-NeXT 的 STEM（Spatio-Temporal-Embodiment Memory）是国内最完整的结构化场景图学术设计，与 `.smem` 概念重叠度高——但**代码截至调研日尚未开源**（GitHub Issue "Release RoboOS-Next" 显示未发布）。一旦发布且采用持久存储，需重新评估定位差异化。

### 2.2 各栈记忆现状对比表

| 栈 / 团队 | 是否有场景图 | 存储层 | 持久化 | 定位 | 与 .smem 关系 | 可信度 |
|---|---|---|---|---|---|---|
| **BAAI RoboOS 1.0**（arXiv:2505.03673，Apache-2.0，561★（截至 2026-05；至 2026-06-10 已增至 571★，见 RoboOS/RoboBrain 深挖报告） | ✅ 动态场景图（floor/room/object 分层，节点含 position/affordance/label，由 RGB-D+SAM+CLIP 构建） | **Redis**（内存 KV，JSON+RAG） | ❌ 逐帧更新、不跨 session | 多机器人实时协调中间件 | **互补**——.smem 可做其持久化后端 | strong |
| **BAAI RoboOS-NeXT / STEM**（arXiv:2510.26536，2025-10） | ✅ 最完整：queue-tree-graph-agent（root/region/carrier 树 + 对象关系图，谓词 ON/IN/LEFT/RIGHT/FRONT/BACK/NEAR） | 论文未明（设计层） | 论文级，**代码未开源** | 学术设计 | **最大潜在重叠**，待代码发布重判 | strong |
| **BAAI RoboBrain 2.0/2.5**（arXiv:2507.02029，3B/7B/32B，Apache-2.0） | 场景图仅作 **LLM 输入 JSON token**，模型**消费**不**存储** | 无（持久化交给 RoboOS Redis） | ❌ | 大脑模型 | 不构成记忆竞品 | strong |
| **InternRobotics（上海 AI Lab，原 OpenRobotLab）** | EmbodiedScan/OST-Bench/InternSR 均为**感知/评测工具**；InternUtopia 的 WKM 仅在仿真内存中 | 无运行时持久记忆模块 | ❌ | 感知/评测工具链 | **无替代竞品**（但 OST-Bench 显示在研此方向） | strong |
| **Horizon 地平线（FSR-VLN / EmbodiedGen）** | FSR-VLN 用分层多模态场景图（HMSG）做导航，存内存；EmbodiedGen 是 3D 世界生成工具 | 内存 | ❌ | 导航/数据生成 | 非持久记忆竞品 | medium |
| **华为 CloudRobo（盘古）** | 商业宣传层提及环境感知/全局规划，技术细节未披露 | 闭源未知 | 未知 | 闭源工业 SaaS | 无开源竞品；潜在标准风险 | medium |
| **穹彻 Noematrix Brain** | 官网声称 long-term/short-term memory，**无技术文档/代码/论文** | 闭源未知 | 未知 | 闭源全栈 SDK | 无法验证（可能仅指任务日志） | weak/uncertain |
| **银河通用 Galbot（AstraBrain）** | 端到端 VLA（GraspVLA/NavFoM 等），**无显式场景图记忆层** | 闭源未知 | ❌（端到端神经网络） | 闭源商业全栈 | 无显式场景图竞品 | medium |

### 2.3 RoboOS 场景图 vs `.smem`：为何"互补"成立（技术细节）

概念层面高度对应（都是层次化节点-边场景图、都支持增量更新与 RAG 查询），但四点关键差异决定互补关系：

1. **存储**：RoboOS = Redis（内存 KV，重启即失）；`.smem` = SQLite（磁盘单文件，跨 session 持久）。
2. **格式**：RoboOS = 传入 LLM 的 JSON token 串；`.smem` = 结构化关系表 + 向量列（sqlite-vec ANN）。
3. **安装门槛**：RoboOS 需 Redis 服务器 + 多机器人网络 + FlagScale 云端 RoboBrain；`.smem` 是 numpy-only `pip install`，无外部依赖。
4. **定位层次**：RoboOS = 多机器人协作调度框架；`.smem` = 单体记忆核心（hippocampus）。**层次不同 → 可叠加而非互斥。**

> **重要纠偏（被验证击中的常见误读）**：RoboBrain 2.0 论文中的 "scene reasoning / scene graph" 既指输入 token 格式也指模型能力，**易被误读为"模型内置了场景图数据库"**。实际上 RoboBrain 只消费 JSON scene graph token，持久化由 RoboOS 的 Redis 负责。**若按误读判断"被覆盖"会得出错误结论。**

### 2.4 对我们集成策略的影响

- **坐实"互补集成"为 P2 默认方向**——VISION §7.2 设的"先探后定"门控，本 spike 给出的结论是：**RoboOS 未自带持久场景图 → 走互补**。可把 `.smem` 定位为"RoboOS 的持久化后端 / 离线 merge 层"。
- **差异化抓手**：① numpy-only / 零外部服务 vs RoboOS 需 Redis+多机网络；② 磁盘持久跨 session vs Redis 重启即失；③ 跨栈中立（任意 OpenAI 兼容 Reasoner / 中美双方栈均可挂载）。
- **必须持续跟踪的两个触发器**：
  1. `https://github.com/FlagOpen/RoboOS/issues` —— **RoboOS-NeXT STEM 代码发布**：若 2026 年发布且采用 SQLite/PostgreSQL 等持久存储，互补关系可能转替代，需立即重评。
  2. RoboOS 2.0 是否将 Redis 切换为持久存储（"by end of this month" 承诺已过期）。
- **InternRobotics 的隐性风险**：更名频繁（OpenRobotLab→InternRobotics，GRUtopia→InternUtopia），OST-Bench（2025-07）显示其在研在线时空推理，**未来可能推出运行时记忆库**，需纳入季度监测。
- **对外引用纪律**：引用 RoboOS"跨机器人空间记忆共享"作为需求信号时，**只能说"与之在离线共享语义上重叠"，不得暗示我们能做实时并发共享**（与 VISION §4.3/§1.3 一致）。

---

## 3. 对 VISION 开放问题的回填

### 3.1 OQ-1（谁是首个付费方）—— 部分回填，核心仍开放

**VISION §6.1 原状态**：完全空白，"当前没有任何已验证的付费方"。

**本次深挖回填的内容**：
- ✅ **明确了"无独立采购先例"是真实市场现状**——全球无一家以纯 SDK 形式卖空间记忆且有公开营收，验证了 VISION 对 OQ-1 的空白判断是准确而非保守。
- ✅ **给假设性 ICP 找到了最贴近的真实参照样本**：Manifold Odin 1 的客户群（已有硬件、缺记忆软件的中小机器人/无人机厂）≈ VISION §6.1 "不自研 S2、有长时记忆需求的纯执行器本体厂"。
- ✅ **明确排除了首批不可能的客户**：Figure/Tesla/AgiBot（自建派）、企业终端用户（买解决方案不买 SDK）。
- ✅ **给出了定价锚点的可信区间与禁用数字**：可参考 per-robot/月 $50–500（打折看待）、per-device 捆绑（Manifold/Slamcore Aware）、per-query（Mem0 $19–249/月模式）；**禁用** Pinecone/Weaviate 营收、Research Intelo $18K–45K。

**仍未关闭的部分（OQ-1 关闭判据未达成）**：
- ❌ **仍无一个"愿为某产品形态付费的真实客户原型"**——VISION §6.1 要求的 1–2 次真实客户访谈尚未发生，本次为桌面深挖，非一手客户验证。
- ❌ **首个商业形态未定**（属 OQ-2）：硬件捆绑 vs 纯 SDK vs 托管 API 的取舍仍需访谈数据支撑。
- **建议**：维持 VISION "OQ-1 关闭前不投重资源做商业化/托管"的纪律；P3 客户访谈优先锁定"已有硬件、缺记忆软件"的中小厂样本（对标 Manifold 客户画像）。

### 3.2 OQ-5（RoboOS / InternRobotics 是否覆盖）—— 基本回填，结论为"互补（暂时）"

**VISION §7.2 原状态**：未验证，决定"互补"还是"被覆盖"，列为 P2 前置门控 spike。

**本次深挖回填的内容（spike 结论）**：
- ✅ **结论 = 互补，不是被覆盖**：RoboOS 用 Redis 内存（非持久化），定位多机器人协调中间件；RoboBrain 只消费 JSON scene graph token 不存储；InternRobotics 全是感知/评测工具，无运行时持久记忆。**满足 VISION §7.2 "若未自带 → P2 坐实互补集成"的分支条件。**
- ✅ **可解除 VISION §1.3 对 RoboOS 引用的降级**：原要求"spike 出结论前降级为待验证信号"，现 spike 已出结论，RoboOS 可重新作为"需求信号 + 互补集成点"引用（但仅限离线共享语义，见 §2.4 纪律）。
- ✅ **P2 方向可坐实**：互补集成（`.smem` 作 RoboOS 持久化后端），差异化打 numpy-only / 持久跨 session / 跨栈中立。

**仍未关闭的部分**：
- ⚠️ **RoboOS-NeXT STEM 代码未开源**——这是 OQ-5 唯一的活跃尾部风险。其学术设计与 `.smem` 重叠度高，**代码一旦发布需立即重评"互补 vs 被覆盖"**。OQ-5 应标注为"暂时关闭，附带监测触发器"而非完全关闭。
- ⚠️ **闭源栈（华为 CloudRobo / 穹彻 Noematrix）无法验证**：声称有 memory 但无技术细节，长期可能形成事实标准（如华为开放 R2C 协议）间接影响 `.smem` 接口设计方向。

### 3.3 整体回填后的 VISION 状态小结

| OQ | 回填前 | 回填后 | 是否关闭 |
|---|---|---|---|
| **OQ-1 首个付费方** | 完全空白 | 市场无先例已证实 + ICP 真实参照（Manifold 客户群）+ 定价锚点 | **未关闭**（缺真实客户访谈，需 P3） |
| **OQ-5 RoboOS 覆盖** | 未验证 | spike 结论=互补；RoboOS 未自带持久场景图 | **暂时关闭**（附 RoboOS-NeXT 代码监测触发器） |

---

## 4. 来源

### 4.1 空白A（付费意愿 / GTM）

**confirmed / updated（可引用）**
- Slamcore：`https://www.slamcore.com/about/`、`https://www.cbinsights.com/company/slamcore/financials`、`https://www.robotics247.com/article/slamcore_raises_series_a_funding_low_cost_spatial_understanding_robots_metaverse`、`https://www.slamcore.com/press-release/slamcore-aware-brings-power-of-vision-to-rtls/`
- Mem0：`https://mem0.ai/series-a`、`https://mem0.ai/pricing`、`https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-agents/`、`https://rywalker.com/research/mem0`
- Manifold Odin 1：`https://kr-asia.com/memory-for-machines-manifold-techs-odin-1-brings-spatial-recall-to-robotics`、`https://www.kr-asia.com/pulses/154463`、`https://www.3dmanifold.com/about/`、`https://store.foxtech.com/odin1-spatial-memory-module-for-robotics-uavs/`
- 机器人中间件定价：`https://cobotfinder.com/guides/robot-fleet-management`、`https://softwarefinder.com/fleet-management-software/formant`、`https://vnrobo.com/en/blog/inorbit-alternatives`、`https://www.inorbit.ai/faq`、`https://docs.foxglove.dev/docs/pricing`
- Tera AI：`https://techcrunch.com/2025/03/19/teraai-comes-out-of-stealth-with-7-8m-to-provide-visual-navigation-for-robots/`
- OSS 空间记忆（反面）：`https://robotmem.com/`、`https://github.com/automatika-robotics/emem`、`https://dynamem.github.io/`、`https://github.com/NVIDIA-AI-IOT/remembr`
- make-vs-buy：`https://roboticsreports.com/arbe-the-qualcomm-of-robotics-perception/`、`https://www.droidbrief.com/resources/ai%E2%80%93robotics-intersection/robot-operating-systems-software-stacks-the-invisible-infrastructure-powering-humanoid-robots.html`
- 中国付费趋势（medium）：`https://www.eet-china.com/mp/a458253.html`、`https://pdf.dfcfw.com/pdf/H3_AP202512031793353788_1.pdf`

**refuted / uncertain（仅作纠偏，禁止引用其数字）**
- Pinecone/Weaviate 营收（refuted）：`https://getlatka.com/companies/pinecone.io`、`https://eboona.com/ai-unicorn/weaviate/`、`https://getlatka.com/companies/weaviate`、`https://theaiengineer.substack.com/p/what-does-pinecone-actually-do`
- 具身软件平台 $18K–45K（uncertain）：`https://researchintelo.com/report/embodied-ai-robot-software-platform-market`

### 4.2 空白B（RoboOS / InternRobotics）

- BAAI RoboOS 1.0：`https://arxiv.org/html/2505.03673v2`、`https://github.com/flagopen/roboos`、`https://flagopen.github.io/RoboOS/`
- RoboOS-NeXT / STEM：`https://arxiv.org/html/2510.26536v1`、`https://huggingface.co/papers/2510.26536`、`https://github.com/FlagOpen/RoboOS/issues`
- RoboBrain 2.0/2.5：`https://arxiv.org/html/2507.02029`、`https://github.com/FlagOpen/RoboBrain2.0`、`https://huggingface.co/BAAI/RoboBrain2.0-3B`
- InternRobotics：`https://github.com/InternRobotics/EmbodiedScan`、`https://github.com/InternRobotics/InternUtopia`、`https://github.com/InternRobotics/OST-Bench`、`https://github.com/InternRobotics/InternSR`、`https://github.com/InternRobotics/RoboInter`
- Horizon：`https://horizonrobotics.github.io/robot_lab/fsr-vln/`、`https://github.com/HorizonRobotics/EmbodiedGen/`
- 华为 CloudRobo：`https://www.huaweicloud.com/eu/news/20250620192415143.html`、`https://en.tmtpost.com/news/7604616`
- 穹彻 Noematrix（weak/uncertain）：`https://www.noematrix.ai/en/noematrix-brain`
- 银河通用 Galbot：`https://www.robotsasia.com/as-fa/Galbot-G1.htm`、`https://news.qq.com/rain/a/20250609A056G400`

### 4.3 本仓库内部依据

- OQ-1 / OQ-5 定义与关闭判据：`docs/zh/VISION.md`（§6.1、§7.2、§8 里程碑表）
- 系统级愿景：`docs/zh/VISION.md`（定稿 v3）
- 既有竞品调研：`docs/zh/research/embodied-brain-landscape-2026.md`
- 单包记忆核愿景与 Open Questions：`tempomem/docs/zh/00-VISION.md`、`tempomem/docs/zh/05-OPEN.md`（B3 Mem0 合作问题与本报告 §1 直接相关）

