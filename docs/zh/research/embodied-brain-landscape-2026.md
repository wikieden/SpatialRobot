> 🌐 [English](../../en/research/embodied-brain-landscape-2026.md) · **中文**

# 具身大脑系统 · 国内外公司与开源项目深度调研（2026）

> 由多 agent workflow 联网调研（exa）+ 对抗验证生成：8 维度 / 96 findings / 8 维。
> 数字按 verdict 处理：refuted 不采用、updated 用更新值、uncertain 标注待核实。

---

本报告基于 8 个维度、经对抗验证（confirmed / updated / uncertain / refuted）的调研数据，为 SpatialRobot 项目定 vision 与架构提供输入。所有数字均按 verdict 处理：refuted 的不采用、updated 的用更新值、uncertain 的明确标注"待核实"。报告同时结合对本仓库三层（tempomem / worldsense / mindloop）实际代码的核读（关键事实：core 通过 `PerceptionAdapter` / `Verbalizer` / `Reasoner` 三个 Protocol 作为 BYO 接缝；`Brain.ask()` 经 `serialize(format="prompt")` 生成 token 高效、带 `#id` 引用的层级化场景图喂给 Reasoner，再以 `Answer(text, cited_node_ids)` 闭环回可定位节点 id；query 路由分层为 relational → intent → semantic-vec/keyword）。

## 1. 执行摘要

1. **格局判断：中美呈"软件大脑 vs 硬件本体"的镜像分工，但都在向中间收敛。** 美国头部（NVIDIA、Google DeepMind、Physical Intelligence、Figure、Skild、Generalist）以 foundation model / VLA / world model 软件层为锚，硬件多靠合作伙伴；中国头部（宇树、智元、优必选、傅利叶、星动、逐际、银河通用）以量产本体与出货量领跑，大脑层近一年由开源研究院（BAAI RoboBrain、上海 AI Lab InternRobotics、北京人形国地中心）和 VLA 创业（千寻、自变量、穹彻、银河通用）快速补强。**两边都缺一个工程化、可持久化、可查询的结构化空间记忆层——这正是 Chronotope 的稀缺位。**

2. **技术范式已从"端到端 VLA"明确收敛到"分层 dual-system（S2 慢推理 VLM + S1 快执行 policy）"作为 2024–2025 工业事实趋同（注意：研究数据中"PsiBot 最早提出双系统"一项被 refuted，"事实标准"措辞证据偏强，宜表述为"头部公司趋同"）。** Figure Helix、π0.5/Hi Robot、NVIDIA GR00T N1、Gemini Robotics-ER 均是此结构。Chronotope 的三层与之天然对位：brain 层 = S2，控制器（不含）= S1，**memory 层填补了所有这些系统共同缺失的"跨帧持久空间状态"**。

3. **世界模型（World Model）是与空间记忆互补而非竞争的第三极。** Cosmos 3、1X World Model、Wayve GAIA-1、Covariant RFM-1、自变量 WUM 做的是像素级 imagination / 合成数据 / 前向预测；Chronotope 做的是结构化、显式、可查询的 3D 对象关系记忆。二者结合（世界模型生成训练数据 + 场景图提供结构化先验降低搜索空间）是有价值的组合，不是替代关系。

4. **空间记忆 / 3D 场景图已是一个清晰的学术范式，且学术主流的技术选择与 Chronotope 高度一致但更工程化。** ConceptGraphs、Hydra/Clio、HOV-SG、Embodied-RAG、3DLLM-Mem、RoboMemory 都是这一范式的实现；Chronotope 的 numpy-only core + sqlite-vec ANN + PerceptionAdapter 协议 + `#id` 可引用序列化，是把这套学术能力做成可装、可嵌、可商用工程组件的差异化路径。

5. **对我们最关键的启示：Chronotope 不应去和 VLA / 本体 / 大脑大模型正面竞争，而应做"所有 S2 都能挂载的外置空间海马体"。** 几乎每个竞品（π0.7 的 MEM、1X 提到 memory context、FieldAI 无地图导航、DYNA 的在职持续学习、Galbot 货架状态、BAAI RoboOS 的"跨机器人空间记忆共享"）都在事实上需要、但都没有做成独立可复用的持久化空间记忆层。

6. **许可与可复用性上，我们的"numpy-only core + 协议接缝"路线天然适配开源生态。** 可直接 fork/port 的高价值开源组件（LeRobot、openpi、ConceptGraphs、Hydra、SAM 2、GroundingDINO、OpenCLIP、Cosmos-Reason、RoboBrain）多为 Apache-2.0 / MIT / BSD；要避开的陷阱是 ORB-SLAM3（GPLv3 传染）、AgiBot World / RoboCasa 部分数据集（CC BY-NC-SA 非商业）、以及 LLaMA-2 衍生权重（7 亿 MAU 条款）。

7. **数据与仿真基建：建议"不自建大规模采集与通用仿真器，最大化复用"。** OXE / DROID / RoboMIND / AgiBot World 覆盖了预训练语料（注意 AgiBot World 为非商业许可）；Isaac Sim（Apache-2.0 核心）/ MuJoCo / Genesis / ManiSkill3 覆盖仿真；CALVIN / LIBERO / RLBench / SimplerEnv 覆盖评测。我们应自建的只有**针对"空间记忆查询正确性"的评测集**（参照 Embodied-RAG 的 Embodied-Experiences、3DMem-Bench），这是无人占据的空白。

8. **风险提示：本赛道融资与出货数字极易过时且口径混乱。** 多个"全球第一/最高估值/累计交付"声称在验证中被标记为 uncertain 或 refuted（如银河通用 ¥93 亿融资被 refuted、Skild $14B/$30M ARR 待核实、傅利叶 1 万台多为康复外骨骼、宇树 vs 智元"全球第一"口径之争）。定 vision 时应以**技术架构与生态位**为锚，不以这些营销数字为锚。

## 2. 全景格局：国外 vs 国内对比

### 2.1 国外公司（大厂全栈 + 大模型创业）

| 名称 | 定位 | 技术路线 | 开源 | 融资/估值（按 verdict） | 落地 | 来源 |
|---|---|---|---|---|---|---|
| NVIDIA Isaac GR00T + Cosmos | 全栈具身 AI 基础设施 | 双系统 VLA（S2 VLM + S1 DiT）+ World Foundation Model + Isaac 仿真 | 开放权重（N1.7 Apache-2.0；N1/N1.5 为 NVIDIA 非商业许可，**注意权重禁商用**） | 上市公司，未单列具身估值 | GR00T 1.7 Early Access；生态伙伴 Figure/Agility/1X/Unitree | arxiv.org/abs/2503.14734 |
| Google DeepMind Gemini Robotics | LLM 大厂延伸物理世界 | 双模型：VLA + Robotics-ER（具身推理 VLM） | 闭源 API；ER 1.5 已开放 API；部分基准（ERQA）开源 | Alphabet 内部 | ER 1.5 在 15 项学术基准 SOTA（已确认）；合作 Apptronik/BD/Agility | deepmind.google/blog/gemini-robotics-15... |
| Tesla Optimus | 车厂跨界量产人形 | FSD 纯视觉 Transformer + RL 仿真 | 闭源 | 内部消化，无独立估值 | **2025 目标 1 万台（非"数千台"）落空，2026.1 Musk 承认零台有用工作** | electrek.co/2026/04/22/... |
| Figure AI（Helix） | 独立 VLA 创业领跑者 | 端侧双系统 VLA（7B S2 + 80M S1，共享 latent） | 闭源 | **Series C >$10 亿，估值 $39B（≈15× Series B 的 $2.6B，已确认）** | 向 BMW 交付（唯一公开工业客户）；BotQ 量产筹建 | figure.ai/news/series-c |
| Physical Intelligence（π） | 纯软件机器人 foundation model | PaliGemma VLM + flow matching；π0.7 引入 history vision encoder（MEM） | π0/π0-FAST/π0.5 Apache-2.0（openpi）；π0.6+ 闭源 | Series B $600M，估值 $5.6B；Series C 谈判中（约 $11B+，**待核实**） | π0.6 工厂演示（咖啡机 13h/30+ 杯，**第三方博客来源，待核实**）；企业私测 | github.com/Physical-Intelligence/openpi |
| Skild AI | "Omni-bodied Brain" | 仿真+人类视频双引擎，omni-bodied | 闭源 | **Series C $14B 估值有间接证据但融资历程与 $30M ARR/盈利均待核实** | 安防/配送/仓储多场景部署（自报） | nvidia.com/case-studies/skild-ai |
| 1X Technologies | 视频世界模型驱动人形 NEO | 14B 视频生成 WM + IDM；70h 机器人数据 fine-tune（**非严格 zero-shot，需 embodiment fine-tune；推理 11s/5s 动作**） | 闭源 | Series B $100M；传 $1B 轮 $10B 估值 | NEO $20K，2026 消费者交付；订阅 $499/月 | 1x.tech/discover/world-model-self-learning |
| Wayve | 自动驾驶端到端 + 世界模型 | GAIA-1（9B WM）+ E2E mapless AI Driver | 闭源 | **Series D $1.2B，估值 $8.6B（非"Series C $1.05B"）** | Nissan/Stellantis/Uber 均已签约，**Stellantis 落地 2028 北美（非 2027 日本）** | wayve.ai/press/series-c/ |
| Field AI | physics-first 工业野外大脑 | Field Foundation Models，无地图/无 GPS，跨 embodiment | 闭源 | **$405M 两轮（已确认）；"估值 $500M→$2B"无官方来源，待核实** | 数百个工业环境部署 | fieldai.com/news/... |
| Covariant（→Amazon） | 仓储 foundation model | RFM-1（8B Any-to-Any 世界模型） | 闭源（Amazon 非独占许可） | Series C 估值 $625M；2024.8 Amazon reverse acqui-hire | 数百仓储客户 | covariant.ai/...rfm-1... |
| Generalist AI | 人类穿戴数据驱动 | 10B+ Harmonic Reasoning；**GEN-1 仅 1h 机器人数据 fine-tune 达 99%（已确认，公司内测非第三方基准）** | 闭源 | $400M，估值 $2B | 全球 1000+ 数据采集站点 | generalistai.com/blog/gen-1 |
| Dyna Robotics | 先单任务商业化 | 单权重 foundation model，固定双臂，在职持续学习 | 闭源 | Series A $120M | DYNA-1 商业环境 24h 运行 99%+；酒店/餐厅/洗衣 | dyna.co/blog/...series-a |
| RLWRLD | 东亚工业灵巧操作 | MSAT（4D+动捕+触觉/力矩），8.1B | **RLDX-1 开源（GitHub+HF）** | Seed 约 $41M | 韩日大企业 PoC | github.com/RLWRLD/RLDX-1 |
| Sanctuary AI | 人脑子系统架构人形 | Carbon AI 分层 | 闭源 | 总融资约 $140M，**资金压力显著，出售 Apptronik 股权套现** | Magna 工厂合作 | thelogic.co/...sanctuary-ai... |
| Boston Dynamics Atlas（+TRI LBM） | 运动控制全球最强 | LBM（450M DiT）+ MPC 底层；拒绝纯端到端 | 闭源 | Hyundai 子公司 | **2026.1 CES 产品版，2026 部署名额已"fully committed"给 Hyundai/DeepMind** | bostondynamics.com/blog/...new-atlas... |
| Agility / Apptronik / Amazon / Microsoft / Meta FAIR | 仓储双足 / DeepMind 硬件伙伴 / 最大部署方 / 平台使能 / 开源触觉研究 | Digit / Apollo / Covariant 整合 / Magma(MIT)+Rho-alpha / Sparsh+Digit 360 | 多闭源；Magma MIT、Meta FAIR 全开源 | Agility Series C $400M/估值 $1.75B（**待核实，匿名来源**） | Agility 约 100 台（待核实）；Apollo Mercedes/GXO | 各官网 |

### 2.2 国内公司（本体全栈 + 大脑大模型）

| 名称 | 定位 | 技术路线 | 开源 | 融资/估值（按 verdict） | 落地 | 来源 |
|---|---|---|---|---|---|---|
| 宇树 Unitree | 出货量领跑 | RL 运动控制 + Isaac Sim + GR00T 生态 | 闭源 | 科创板 IPO 获批，拟募 ¥42 亿，估值约 ¥420 亿 | **2025 人形出货 5500+ 台（已确认）；"全球第一"与智元有口径之争，不宜作确定陈述** | robotscope.net/companies/unitree |
| 智元 AgiBot | 量产规模最大之一 | GO-2/GO-3 VLA + BFM-2 + Genie Sim 3.0 | AGIBOT WORLD 数据集开源（**CC BY-NC-SA 非商业**）；模型闭源 | 估值约 ¥300 亿（C 轮） | **2026.3 第 1 万台"下线"（生产里程碑≠交付，已确认）** | agibot-world.com |
| 优必选 UBTech | 港股工业人形 | Thinker VLM(100B) + BrainNet 2.0 + 热插拔电池 | 闭源 | 港股 9880.HK，市值约 60 亿港元 | **Walker S2 累计签约从 ¥8 亿→¥13 亿（"积压"措辞误导，实为签约额；2025 交付约数百台）** | ubtrobot.com/walker-s2 |
| 傅利叶 Fourier | 最早规模交付 + 开源 N1 | NVIDIA GR00T + 遥操作 + N1 完全开源（硬件+软件） | **N1 完全开源**；GR-1/GR-2 闭源 | 总融资约 ¥8 亿，E 轮 | **"累计交付 1 万台"待核实，且 99%+ 为康复外骨骼非通用人形** | fftai.com/n1 |
| 星动纪元 RobotEra | 清华系全身灵巧 | 自研端到端 LVA + 全模态感知 | 闭源 | Series A，估值 ¥100 亿+ | 200+ 台，海外占 50%+ | robotera.com/star1 |
| 逐际动力 LimX | 大小脑融合 OS + 开源 VLA | COSA Agentic OS + FluxVLA(MIT) + DreamActor | **FluxVLA 开源(MIT)**；COSA 闭源 | B 轮 $2 亿（京东领投，已确认），CoRL 2025 双录 | **Oli 量产就绪+预售已确认（已交付，但出货规模极有限）** | limxdynamics.com/oli |
| 银河通用 Galbot | 轮式双臂务实路线 | GraspVLA/TrackVLA/GroceryVLA(开源) + AstraBrain | GraspVLA/TrackVLA 开源；平台闭源 | **累计约 ¥70 亿量级（"¥93 亿"被 refuted）；估值约 $30 亿（2026.3 行业最高，已被千寻局部追平）** | 北京近 10 店零售部署；宁德时代/博世/丰田产线 | github.com/GalaxyGeneralRobot/GraspVLA |
| 千寻智能 Spirit AI | VLA + 人形双线 | Spirit 系列 VLA + Moz1 力控本体 | **Spirit v1.5 开源(Apache-2.0)；v1.6 部分开源（"开源"定性待核实）** | 3 个月约 ¥50 亿，估值 2026.4 超 ¥200 亿 | **v1.6 登顶 RoboArena（首个登顶的中国具身模型，"开源"定语存疑）；汽车 OEM 产线** | qbitai.com/2026/01/369107.html |
| 自变量 X Square | 物理世界基础模型 | WALL 系列（VLA+WM 融合），WALL-OSS 开源 | **WALL-OSS 开源**；旗舰闭源 | 9 轮累计 >¥30 亿，A++ 轮字节/红杉领投 ¥10 亿 | **WUM 2026.4 发布（已确认，"全球首个"为自我宣称）；外卖/家庭演示** | stcn.com/article/detail/3777754.html |
| 穹彻 Noematrix | 力觉中心大脑 SaaS | 力-位混合 VLA + AnySkill | 闭源 | **多轮"数亿元"（已确认，从未披露具体金额）；阿里战投** | 工业/家庭/物流 | noematrix.ai |
| 智澄英达 Zhicheng | AI 原生物理世界大模型 | "成灵"端到端 + 足式/轮式双本体 | 闭源 | 早期（天使/Pre-A），公开信息有限 | TR4/TR5 京东自营发售 | zhicheng-robot.com |
| 北京人形国地中心 | 国家级共性技术平台 | 慧思开物（VLA+WM+运控）+ XR-1 跨本体 VLA | **大量开源（MIT/Apache）** | 政府主导，非商业公司 | **RoboMIND 下载量"600 万次"待核实**；天工本体 | x-humanoid.com |
| 上海 AI Lab（InternRobotics） | 书生具身全栈引擎 | InternVLA 系列 + Intern·WorldModel，一脑多形 | **全开源(Apache-2.0)** | 非营利研究院 | 适配 10+ 机器人形态 | github.com/InternRobotics |
| 智源 BAAI（RoboBrain） | 开源具身大脑生态 | RoboBrain 2.0/2.5（3B/7B/32B）+ RoboOS 大小脑分层 | **全开源(Apache-2.0)** | 非营利研究院 | **32B 多基准 SOTA（已确认，"大多数基准"口径有选择性，已被 2.5 局部超越）** | github.com/FlagOpen/RoboBrain2.0 |
| 阿里 / 字节 / 华为 | Qwen 大脑+躯体军团 / GR-3+ByteMini / 平台生态 | WorldVLA / GR-3(4B MoT) / 昇腾+盘古+5G-A | Qwen/技术报告公开，具身专项未开源 | 阿里三年 ¥3800 亿算力；字节投自变量；华为哈勃入股千寻 1.43% | 阿里仓储/配送/零售数据飞轮；ByteMini >千台 | guancha.cn/...792646.html |

### 2.3 中美差异点评

- **硬件 vs 软件分工**：美国创业（PI、Skild、Generalist、Field AI、Covariant、Dyna）大量是**纯软件 foundation model 公司**，明确"做机器人界的 Android/大脑供应商"，硬件外包；中国头部是**本体量产领跑**（宇树/智元/优必选/傅利叶出货量与 IPO 进度全球领先），大脑层近一年才由研究院开源（BAAI/上海 AI Lab/国地中心）与 VLA 创业（千寻/自变量/穹彻/银河通用）补强。
- **开源策略差异**：中国"国家队 + 研究院"路线把**大脑模型与数据集大规模开源**（RoboBrain、InternVLA、慧思开物、AGIBOT WORLD、RoboMIND、FluxVLA、WALL-OSS、Spirit v1.5、RLDX-1），形成与美国"NVIDIA 开放权重 + 学界 Apache/MIT"并行的第二条开源供给。美国闭源创业（Figure/PI 商业版/Skild/Generalist）则把最强能力留在私有版本。
- **数据飞轮锚点差异**：美国靠人类穿戴设备（Generalist 50 万小时）、仓储部署（Covariant）、遥操作（PI/ALOHA）；中国靠真实业务场景（阿里仓储/配送/零售、银河通用零售门店、优必选/智元汽车产线）。
- **共同空白**：中美双方的 S2/大脑层都**默认无持久化、可查询的结构化空间记忆**——这是 Chronotope 的中立生态位（可同时服务两边的 OpenAI 兼容 Reasoner）。

## 3. 技术架构范式对比

| 范式 | 代表作 | 核心机制 | 优势 | 劣势 | 趋势取舍 |
|---|---|---|---|---|---|
| **端到端 VLA** | RT-2、OpenVLA(7B)、π0、MolmoAct 2、RDT-1B、GR-3、Spirit | 视觉+语言+动作统一单网络，一次前向出动作 token（离散/扩散/流匹配） | 简单、低延迟、无协调开销；OpenVLA 7B 以编码器选择超 RT-2-X 55B **16.5%（已确认；"省 70% GPU 时间"被 updated 为约 87.5%/8x）** | 难 debug 局部故障、跨机型泛化差、长程任务随步数衰减、**无显式场景记忆/无跨帧持久状态** | 仍是 SOTA 基线，但单体路线在长程任务上触顶，正被双系统吸收 |
| **分层 dual-system（S1+S2）** | Figure Helix、π0.5/Hi Robot、GR00T N1、Gemini Robotics-ER、Fast-in-Slow | S2（7B VLM，7-9Hz，规划）+ S1（80M policy，200Hz，控制），中间用 latent/NL 子指令/action chunk 桥接 | 多时间尺度推理、安全性好、易长程；**2024-25 头部公司趋同（"事实标准"措辞证据偏强；"PsiBot 最早提出"被 refuted）** | 协调延迟、S1/S2 对齐困难、工程复杂；**S2 仍无持久空间记忆** | 工业主流。Fast-in-Slow 用参数共享消协调开销（RLBench 69% vs π0 55%）；三系统加 Critic 提升 OOD |
| **世界模型（World Model）** | Cosmos 3、Genie 2/3、1X WM、Wayve GAIA-1、Covariant RFM-1、自变量 WUM、V-JEPA 2 | 视频生成模型模拟环境动态，在 imagination 中 rollout/规划/生成合成数据 | 缓解数据瓶颈、安全评估、策略改进；**Cosmos 3 统一单系统已确认（"30s 预测"待核实）** | 动作一致性、长程误差累积、实时推理代价大、评估指标不统一 | 快速发展；定位为 learned simulator / 合成数据源，**而非替代感知+记忆层** |
| **空间记忆 / 3D 场景图** | ConceptGraphs、Hydra/Clio、HOV-SG、Embodied-RAG、3DLLM-Mem、RoboMemory、**Chronotope** | RGB-D → 持久化可查询 3D 对象图，为 VLM/LLM 规划器注入结构化空间上下文 | 解决 VLM 无跨帧记忆痛点；轻量、可查询、可引用；3DLLM-Mem 困难任务 **32.1% vs 基线约 5%（已确认）** | 学术为主、少商业产品；稠密 vs 稀疏表示尚未定型；依赖上游感知质量 | 从稀疏对象图→稠密 3D patch、从静态→动态；趋势是与 dual-system 的 S2 集成 |

**取舍结论**：端到端 VLA 与 dual-system 是"动作生成"主线的两代；世界模型是"数据/想象"辅助极；空间记忆是"持久状态/记忆"极。**这三极正交互补**——Chronotope 应明确站在"空间记忆极"，做 dual-system S2 的外挂记忆与 world model 的结构化先验提供方，而不是去做第四个 VLA。本仓库代码已天然落在该位置：`serialize(format="prompt")` 产出带 `#id` 的层级场景图 → Reasoner 推理 → `Answer.cited_node_ids` 回指可定位节点，正是"VLM planner + 结构化空间上下文"范式的工程实现。

## 4. 开源可复用组件清单（按三层归类）

### 4.1 Memory 层（最核心、与我们直接对位）

| 组件 | 许可证 | 成熟度 | 处置建议 |
|---|---|---|---|
| ConceptGraphs | MIT（代码，已确认）/ CC-BY-SA（网站） | ICRA 2024 研究原型，真机已验证（Jackal，已确认）；无 release tag | **可 port**：感知前端（SAM+CLIP+LLaVA→3D 对象图）直接对位我们 perception+memory；对象级场景图设计可借鉴 |
| Hydra | BSD-2-Clause | Science Robotics 2022 / IJRR 2024，研究级成熟，ROS 2 Jazzy | **仅参考/可选 port**：多层场景图（Mesh→对象→场所→房间→楼层）是我们分层结构的最强对标；C++/ROS 2 重，与 numpy-only core 不直接兼容 |
| Clio | 待确认（MIT SPARK 惯例 BSD/MIT） | RA-L 2024 | **仅参考**：任务驱动 Information Bottleneck 聚类直接对位我们 query 的意图路由 |
| HOV-SG | MIT | RSS 2024，**表示体积减 75%、三数据集超基线（已确认）** | **可 port**：三级（楼/房/对象）开放词汇场景图 + Voronoi 跨楼导航，是我们多分辨率 scene-graph 的参照 |
| Embodied-RAG | 学术（多为 MIT，待确认） | arXiv 2024-09，**1km 环境 4.5min/3353 节点，比 Graph-RAG 快 7.38x（已确认）** | **强参考**：语义森林分层 RAG 检索与我们 query 路由高度互补；其 Embodied-Experiences 数据集可作评测床 |
| 3DLLM-Mem | 开源（待确认） | arXiv 2025-05，3DMem-Bench | **强参考**：稠密 3D patch episodic memory 路线，可启发我们加"几何内存层"补充 object-centric 图 |
| RoboMemory | 学术（代码状态待确认） | arXiv 2025-08，EmbodiedBench SOTA | **强参考/最直接竞品**：四类记忆（空间/时间/情景/语义）框架；我们更轻量、更工程化（numpy-only 持久化）是差异点 |

### 4.2 Perception 层

| 组件 | 许可证 | 成熟度 | 处置建议 |
|---|---|---|---|
| SAM 2 | Apache-2.0（代码+权重） | 生产可用，Meta 官方维护 | **可 fork/直接依赖**：实例分割 + streaming memory，是 PerceptionAdapter 的核心 mask 来源；streaming memory 与我们 pending/commit 思路互补 |
| GroundingDINO | Apache-2.0（v1）；1.5/DINO-X 为 API（待确认） | ECCV 2024，10.1k stars，已进 HF Transformers | **可直接依赖**：开放集检测 bbox；与 SAM 2 组成 Grounded-SAM 前端 |
| OpenCLIP | Apache-2.0 | 生产可用，社区活跃 | **已直接依赖**：worldsense `[clip]` extra 即用 open-clip-torch，写入 sqlite-vec ANN |
| KISS-ICP / KISS-SLAM | MIT（ICP）/ 待确认（SLAM） | KISS-ICP 成熟（v1.3.0 2026-04）；KISS-SLAM IROS 2025 | **可直接依赖**：提供 world-frame 位姿（odometry），是 camera→world lift 的前置；MIT 无传染风险 |
| SplaTAM | BSD-3-Clause | CVPR 2024 原型 | **仅参考/可选**：3DGS 稠密 RGB-D 重建可作几何基底，与我们显式场景图互补 |
| ORB-SLAM3 | **GPLv3** | 学术标准基线，维护趋缓 | **仅参考，勿链接进发行包**：GPLv3 传染性对商业不友好；位姿需求优先用 KISS-ICP |

### 4.3 Brain 层

| 组件 | 许可证 | 成熟度 | 处置建议 |
|---|---|---|---|
| Cosmos-Reason（1/2） | NVIDIA Open Model License（商业可用、允许衍生） | 已开源；**Cosmos-Reason2-8B 基于 Qwen3-VL（已确认），发布日实为 2025-12-19（非 2025-09，updated），仓库已停维护，Cosmos 3 取代** | **已对接**：本仓库 CosmosReasonVerbalizer 即调它；本地 RTX PRO 6000 部署符合 OpenAI 兼容 `/v1/chat/completions` 设计。建议跟进 Cosmos 3 |
| LeRobot | Apache-2.0 | 生产就绪、生态主导（v0.5.1，24.8k stars） | **强参考/可对接**：LeRobotDataset v3.0 是喂 PerceptionAdapter 的标准数据源；其 5 个官方 VLA（**Pi0Fast/Pi0.5/GR00T N1.5/SmolVLA/XVLA**，已确认）可作下游 S1 |
| openpi（π0/π0.5/π0-FAST） | Apache-2.0（已确认，PI 自用） | 商业级 | **可对接**：流匹配动作头作为我们 Reasoner 输出后的下游执行器；π0.5 OOD 94%（已确认）依赖场景多样性，正需我们提供持久跨帧上下文 |
| SmolVLA | Apache-2.0 | 2025-06，LeRobot 官方集成 | **可 fork**：450M 轻量、**可跑 CPU/MacBook（已确认）**，异步推理与我们 fuse-before-persist 时序解耦一致 |
| RoboBrain 2.0/2.5 | Apache-2.0 | 国内最强开源具身大脑 | **可对接**：RoboOS"跨机器人空间记忆共享"与我们 .smem 语义高度重叠；可做"外挂空间记忆"集成 |
| InternVLA / XR-1 / FluxVLA / WALL-OSS / RLDX-1 / Spirit v1.5 | Apache-2.0 / MIT | 各有论文/竞赛背书 | **可对接/参考**：均为 OpenAI 兼容或可插拔，作为 Reasoner/下游 policy 候选 |
| OpenVLA | MIT（代码）/ **LLaMA-2 Community License（权重，7 亿 MAU 需授权，已确认）** | ICML 2024 | **可参考，权重慎用**：优选已迁 LLaMA-3.2 的 OpenVLA-mini 规避商业限制 |
| RoboVLMs | Apache-2.0 | 2024-12 框架 | **强参考**："30 行接入任意 VLM"哲学与我们 PerceptionAdapter/Verbalizer 协议同构 |

## 5. 数据 / 仿真 / 评测基建

**总原则：最大化复用，仅在"空间记忆评测"上自建。**

**数据集（用于 perception/memory 预训练验证，不自采）：**
- **OXE / RT-X**（CC BY 4.0，子集保留原始限制）：1M+ 轨迹、22 机体，VLA 预训练事实标配；局限是以短视程 pick-and-place 为主。
- **DROID**（开源宽松许可）：76k 轨迹/564 场景，**相比次优方法分布内 +22%/分布外 +17%（已确认）**；多视角 RGB-D + 相机标定直接喂感知。
- **RoboMIND**（许可未明确，待查）：107k 轨迹/479 任务/4 机体，RSS 2025；**"最大多机体遥操作数据集"仅限"统一平台上"（updated，AgiBot World 体量远超）**。
- **AgiBot World**（**CC BY-NC-SA 4.0 非商业**）：1M+ 轨迹/约 3000h；**"长时序 10x / 场景 100x"中 100x 无一手依据（updated，论文仅称约 10x）**。商业产品**不可用**。

**仿真器（不自建通用仿真器）：**
- **Isaac Sim 5.0 / Isaac Lab**（**核心 Apache-2.0，但 Omniverse Kit SDK 等依赖受额外 NVIDIA 许可**）：工业级 sim2real 主流，GR00T 训练标准。
- **MuJoCo / MJX / Playground**（Apache-2.0）：接触丰富、GPU 加速、轻量，多 benchmark 底层。
- **Genesis**（Apache-2.0）：**43M FPS / 430,000x 仅适用简单场景峰值（updated，"10-80x"为上限）**，多物理统一，快速成长。
- **ManiSkill3 / SAPIEN**（Apache-2.0）：30,000+ FPS，12 任务域含人形/移动操作；SimplerEnv 基于其构建。
- **RoboCasa365**（开源，MIT/Apache 待查）：365 任务/2500+ 厨房，家庭场景是我们 scene-graph 的典型测试床。

**评测（复用通用，自建空间记忆专项）：**
- 复用 **CALVIN**（MIT，语言条件长时程）、**LIBERO**（MIT，终身学习前/后向迁移，与我们 decay/consolidate 直接对应）、**RLBench**（MIT，100+ 任务）、**SimplerEnv**（MIT/Apache，**sim-real 强相关已确认，但定位是"代理"非"替代"，主指标用 MMRV**）。
- **自建项**：参照 Embodied-RAG（Embodied-Experiences）、3DLLM-Mem（3DMem-Bench）做一个**"空间记忆查询正确性 + cited_node_ids 召回率 + 跨 episode 持久性 + decay/forget 正确性"**的评测集。这是当前无人占据、且直接证明我们价值主张的空白，应优先自建。

## 6. 对 SpatialRobot 的 Vision / 架构建议

### 6.1 差异化 wedge：空间记忆层确是稀缺位

证据链清晰：(1) 端到端 VLA 与 dual-system S2 **结构性地无持久跨帧空间状态**（OpenVLA/π0/Helix/GR00T/Gemini-ER 均单帧或短上下文）；(2) 头部公司在事实上需要它——π0.7 才补 history vision encoder（MEM）、1X 明确提"需要 memory context 处理 drift/partial observability"、Field AI 无地图导航的定位/重规划痛点、DYNA 的在职持续学习需要持久环境知识、Galbot 货架状态追踪、BAAI RoboOS 把"跨机器人空间记忆实时共享"写进架构；(3) 学术已成范式但**几乎没有人把它做成独立、可装、可商用、numpy-only 的工程组件**（ConceptGraphs/Hydra/Clio/Embodied-RAG/3DLLM-Mem/RoboMemory 都是研究代码或重 C++/ROS 栈）。本仓库的工程选择（numpy-only core、sqlite-vec ANN、`.smem` 单文件、`PerceptionAdapter`/`Verbalizer`/`Reasoner` 三协议接缝、`#id` 可引用序列化、fuse-before-persist 不变量）恰好把这套学术能力做成了**可嵌入任意 S2 的外置海马体**。**结论：wedge 成立，且是中立生态位（中美双方、任意 OpenAI 兼容 Reasoner 都能挂载）。**

### 6.2 与各范式的关系（明确不做什么）

- **不做端到端 VLA / 不做大脑大模型**：那是 PI/Skild/Generalist/RoboBrain/千寻/自变量的红海，我们去做必败。
- **不做本体**：那是宇树/智元/傅利叶/逐际的资本密集赛道。
- **做 dual-system 的 memory 层**：把 Chronotope 定位为"任何 S2（Cosmos-Reason / RoboBrain / Gemini-ER / π0.5）都能调用的结构化空间记忆 + 查询服务"。`Brain.ask()` 已是这个接口的雏形。
- **做 world model 的结构化先验提供方**：用世界模型生成合成 RGB-D 扩充 perception 训练集；用 `.smem` 场景图为 imagination rollout 提供物体位置/关系先验，降低搜索空间。

### 6.3 分阶段路线建议

- **Phase 1（地基，0–3 月）**：坐实 memory core 与 BYO 接缝。落地首个 `PerceptionAdapter` 具体实现（ConceptGraphs 路线：SAM 2 + GroundingDINO + OpenCLIP，全 Apache/MIT，behind `[perception]` extra）；坐实 Cosmos-Reason2 / RoboBrain 双 Reasoner 后端；自建空间记忆评测集（6.1 的 wedge 必须有数字支撑）。
- **Phase 2（集成验证，3–6 月）**：在 1–2 个开源友好的国内本体上做端到端 demo（傅利叶 N1 全开源、逐际 FluxVLA(MIT)、银河通用零售货架场景是教科书用例）；接入 LeRobot 生态（LeRobotDataset 喂感知、其 5 个官方 VLA 作下游 S1）；对接一个外置 S2（RoboBrain RoboOS 的"空间记忆共享"是最契合的集成点）。
- **Phase 3（生态位锁定，6–12 月）**：把 Chronotope 做成"具身记忆标准接口"——发布稳定的序列化协议（已有 `#id` 可引用 prompt 格式）、跨 episode/跨机器人持久化、decay/consolidate 生命周期；争取被一个开源大脑（RoboBrain / InternRobotics）或一个本体厂作为默认记忆层采用。商业场景优先选**多班次/长时连续作业**（优必选 Walker S2 7×24h、DYNA 24h、仓储多班次）——这些场景下持久空间记忆是刚需而非锦上添花。

### 6.4 要避开的许可陷阱与坑

- **许可陷阱**：ORB-SLAM3（**GPLv3 传染**，勿链接进发行包，位姿用 KISS-ICP/MIT）；AgiBot World / 部分 RoboCasa 数据集（**CC BY-NC-SA 非商业**，仅可研究）；OpenVLA / 任何 LLaMA-2 衍生权重（**7 亿 MAU 条款**，优选 LLaMA-3.2/Qwen 系骨干）；GR00T N1/N1.5 权重（**NVIDIA 非商业许可，禁商用**，商业用 N1.7 Apache-2.0 或 Cosmos Open Model License）。
- **工程坑**：保持 core numpy-only 契约（CLAUDE.md 已明令：给 tempomem/ 加 torch/LLM import 即破契约）；fuse-before-persist 不变量（新增 mutator 必须先 `_flush_pending()`）；测试 network-free（用 ScriptedReasoner / HashEncoder）。
- **战略坑**：不要被"出货量/估值/全球第一"营销数字带节奏定 vision——多个此类声称在本次验证中被 refuted/uncertain；以技术生态位为锚。

## 7. 关键不确定项（验证为 uncertain/refuted 的声明 + 待调研空白）

**被 refuted（不得引用）：**
- 银河通用"累计融资 ¥93 亿、国内第一"——实际约 ¥70 亿量级，估值被误读为融资额。
- Wayve"Series C $1.05B、首款 2027 财年日本量产"——实为 Series D $1.2B/估值 $8.6B，Stellantis 落地 2028 北美。
- "双系统 PsiBot 2024 最早提出"——PsiBot 该文 2025-04，Figure Helix（2025-02）更早，无首创证据；"工业事实标准"措辞证据偏强。
- "3DLLM-Mem 比基线高 6 倍"——论文主口径是绝对 +16.5 个百分点（6 倍仅对应 hard 子集）。

**uncertain（待核实，不可作确定陈述）：**
- Skild $14B 估值 / Series A $1.5B 起点 / $30M ARR 盈利（CDN 拦截，官网无文）。
- π0.6 工厂咖啡机 13h/30+ 杯/>90%（仅第三方博客，PI 官网 404）。
- Field AI 估值 $500M→$2B（官方仅确认 $405M 融资）。
- Agility 约 100 台出货 / $400M / $1.75B（匿名来源，官方拒评）。
- 傅利叶累计 1 万台（多为康复外骨骼，通用人形仅数百台）。
- RoboMIND 下载 600 万次（单一官方自报来源，与"11 万次"口径矛盾）。
- Cosmos 3"30 秒动作条件预测"、Genie 3"2026-01 订阅开放"（一手来源未证）。
- Figure Helix-02"完整 8 小时自主轮班"（官方仅有数据采集量"8h"，无连续轮班公告）。

**需进一步调研的空白：**
- 各开源场景图组件（Clio、3DLLM-Mem、RoboMemory、Embodied-RAG）的**确切许可证**（多为"待确认"），fork/port 前必须逐仓核 LICENSE。
- **空间记忆层的商业付费意愿**：现有证据都是"技术上需要"，但没有一家把它作为独立采购项——需做 1–2 个客户访谈验证 GTM。
- **Cosmos 3 / RoboBrain 2.5 等新一代 S2 是否会内化记忆能力**，从而压缩外置记忆层的空间（π0.7 已开始内化 MEM）——这是 wedge 的最大长期风险，需持续监测。
- 国内"一脑多形"研究院开源栈（RoboOS / InternRobotics）是否已自带场景图记忆，决定我们是"互补"还是"被覆盖"。

## 8. 来源（合并去重）

- arxiv.org/abs/2503.14734（GR00T N1）；developer.nvidia.com/isaac/gr00t；developer.nvidia.com/cosmos；research.nvidia.com/labs/gear/gr00t-n1_6/；huggingface.co/nvidia/GR00T-N1.7-3B
- deepmind.google/blog/gemini-robotics-brings-ai-into-the-physical-world/；deepmind.google/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/；deepmind.google/blog/gemini-robotics-er-1-6/；arxiv.org/html/2503.20020
- electrek.co/2026/04/22/tesla-optimus-production-fremont-model-sx-line/；electrek.co/2025/01/31/...10000-optimus-robots-this-year/
- figure.ai/news/helix；figure.ai/news/series-c；figure.ai/news/helix-logistics
- bostondynamics.com/blog/large-behavior-models-atlas-find-new-footing/；bostondynamics.com/blog/boston-dynamics-unveils-new-atlas-robot...；tri.global/news/...boston-dynamics-and-toyota-research-institute...
- geekwire.com/2025/agility-robotics-reportedly-raising-400m...；apptronik.com/news-collection/apptronik-raises-350-million...；aboutamazon.com/news/company-news/amazon-covariant-ai-robots
- microsoft.com/en-us/research/blog/magma...；ai.meta.com/blog/fair-robotics-open-source/；arxiv.org/pdf/2506.22355
- arxiv.org/html/2410.24164v3（π0）；github.com/physical-intelligence/openpi；pi.website/blog/pi05；therobotreport.com/physical-intelligence-raises-600m...
- skild.ai；nvidia.com/en-us/case-studies/skild-ai/；businesswire.com/...Skild-AI-Raises-1.4B...（403）
- 1x.tech/discover/world-model-self-learning；1x.tech/discover/1x-secures-100m-in-series-b-funding；techcrunch.com/2026/01/13/neo-humanoid-maker-1x-releases-world-model...
- wayve.ai/press/series-c/；wayve.ai/press/series-d/；wayve.ai/thinking/introducing-gaia1/；arxiv.org/abs/2309.17080；media.stellantis.com/...wayve-partner...
- fieldai.com/news/fieldai-announces-over-400m...；cnbc.com/2025/08/20/gates-nvidia-fieldai-robotics.html
- covariant.ai/...rfm-1...；spectrum.ieee.org/covariant-foundation-model；techcrunch.com/2024/08/31/amazon-hires-the-founders-of-robotics-ai-startup-covariant/
- rlwrld.ai/en；github.com/RLWRLD/RLDX-1；generalistai.com/blog/gen-0；generalistai.com/blog/gen-1；siliconangle.com/2026/06/04/generalist-ai-raises-400m...
- dyna.co/blog/dyna-robotics-closes-120m-series-a；prnewswire.com/...dyna-1...；thelogic.co/news/exclusive/sanctuary-ai-humanoid-robot-fundraise-efforts/
- robotscope.net/companies/{unitree,ubtech,agibot,fourier,robotera,limx,booster,galbot,engineai,xiaomi-robotics}；unitree.com/g1/；shop.unitree.com/blogs/news/clarification-regarding-unitrees-2025-sales-data
- agibot-world.com；github.com/OpenDriveLab/AgiBot-World；huggingface.co/datasets/agibot-world/AgiBotWorld-Beta；arxiv.org/abs/2503.06669；prnewswire.com/...Omdia-Ranks-AgiBot-No1...
- ubtrobot.com/walker-s2；finance.sina.com.cn/stock/relnews/2025-11-13/...；fftai.com/n1；en.wikipedia.org/wiki/Fourier_(company)
- robotera.com/star1；limxdynamics.com/oli；cnevpost.com/2026/02/02/...limx-secures-200-million...；boosterrobotics.com/k1；engineai.com.cn/se01
- github.com/GalaxyGeneralRobot/GraspVLA；prnewswire.com/...Galbot-Secures-Over-300-Million...；wallstreetcn.com/articles/3766500；stcn.com/article/detail/3549196.html
- qbitai.com/2026/01/369107.html（千寻）；stcn.com/article/detail/3586134.html；163.com/dy/article/KUGLKN6I0519BQPG.html；scmp.com/tech/article/3355838
- qbitai.com/2026/01/369147.html（自变量）；stcn.com/article/detail/3777754.html；36kr.com/p/3020497031226626；blog.csdn.net/2401_83634908/article/details/151332425
- noematrix.ai；nbd.com.cn/articles/2026-02-10/4256151.html；zhicheng-robot.com；robothub.app/zh/companies/zhicheng-ai
- x-humanoid.com/news-view-227.html（国地中心）；x-humanoid-robomind.github.io/；arxiv.org/abs/2412.13877；huggingface.co/datasets/x-humanoid-robomind/RoboMIND
- shlab.org.cn/news/5444187；github.com/InternRobotics；huggingface.co/InternRobotics
- github.com/FlagOpen/RoboBrain2.0；github.com/FlagOpen/RoboBrain2.5；huggingface.co/BAAI/RoboBrain2.0-32B；arxiv.org/abs/2507.02029；ai-bot.cn/roboos/
- guancha.cn/economy/2025_10_09_792646.shtml（阿里）；hub.baai.ac.cn/view/49934；stcn.com/article/detail/3328546.html（字节 GR-3）；fund.eastmoney.com/a/202505083399729165.html（华为入股千寻）
- github.com/huggingface/lerobot；huggingface.co/blog/lerobot-release-v040；huggingface.co/blog/lerobot-datasets-v3
- github.com/openvla/openvla；openvla.github.io/；github.com/moojink/openvla-oft；arxiv.org/abs/2406.09246；ai.meta.com/llama/license/
- github.com/octo-models/octo；arxiv.org/abs/2405.12213
- github.com/Physical-Intelligence/openpi（LICENSE/README）；pi.website/blog/openpi；arxiv.org/abs/2504.16054
- github.com/thu-ml/RoboticsDiffusionTransformer；huggingface.co/robotics-diffusion-transformer/rdt-1b；arxiv.org/abs/2410.07864
- github.com/tonyzhaozh/act；tonyzhaozh.github.io/aloha/；github.com/MarkFzp/mobile-aloha
- github.com/Nvidia/Isaac-GR00T；huggingface.co/blog/nvidia/gr00t-n1-7；huggingface.co/nvidia/GR00T-N1-2B；huggingface.co/nvidia/GR00T-N1.5-3B
- arxiv.org/abs/2506.01844（SmolVLA）；huggingface.co/blog/smolvla；huggingface.co/lerobot/smolvla_base
- github.com/Robot-VLAs/RoboVLMs；robovlms.github.io/；arxiv.org/abs/2412.14058
- github.com/2toinf/X-VLA；thu-air-dream.github.io/X-VLA/
- robotics-transformer-x.github.io/；arxiv.org/abs/2310.08864（OXE）；droid-dataset.github.io/；arxiv.org/abs/2403.12945
- concept-graphs.github.io/；arxiv.org/pdf/2309.16650；github.com/concept-graphs/concept-graphs
- github.com/MIT-SPARK/Hydra；arxiv.org/pdf/2201.13360；journals.sagepub.com/doi/10.1177/02783649241229725；github.com/MIT-SPARK/Clio；arxiv.org/abs/2404.13696
- arxiv.org/abs/2403.17846（HOV-SG）；github.com/hovsg/HOV-SG；hovsg.github.io/
- ros.org/reps/rep-2000.html；navigation.ros.org/；developer.nvidia.com/isaac/lab；github.com/isaac-sim/IsaacLab；github.com/isaac-sim/IsaacSim
- robocasa.ai/；github.com/robocasa/robocasa；arxiv.org/html/2603.04356v1；arxiv.org/abs/2406.02523
- github.com/facebookresearch/sam2；ai.meta.com/sam2/；arxiv.org/html/2408.00714v2
- github.com/IDEA-Research/GroundingDINO；arxiv.org/pdf/2405.10300；github.com/IDEA-Research/Grounded-SAM-2
- github.com/mlfoundations/open_clip；laion.ai/blog/giant-openclip/；pypi.org/project/open-clip-torch/2.7.0/
- github.com/PRBonn/kiss-icp；github.com/PRBonn/kiss-slam；github.com/UZ-SLAMLab/ORB_SLAM3；arxiv.org/pdf/2007.11898；github.com/spla-tam/SplaTAM；arxiv.org/pdf/2312.02126
- blogs.nvidia.com/blog/cosmos-world-foundation-models/；huggingface.co/nvidia/Cosmos-Reason2-8B；github.com/nvidia-cosmos/cosmos-reason2；research.nvidia.com/labs/cosmos-lab/cosmos-reason1/；arxiv.org/abs/2503.15558；arxiv.org/abs/2606.02800（Cosmos 3）
- deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/；deepmind.google/models/genie/；arxiv.org/pdf/2512.04797（SIMA 2）
- arxiv.org/abs/2409.18313（Embodied-RAG）；quanting-xie.github.io/Embodied-RAG-web/；arxiv.org/abs/2410.23968
- arxiv.org/abs/2508.01415（RoboMemory）；openreview.net/forum?id=HHGzG1Choi
- arxiv.org/html/2505.04769v2；roboticscenter.ai/learn/vla-models-comparison；arxiv.org/pdf/2405.14093；arxiv.org/html/2506.01953v1（Fast-in-Slow）；github.com/CHEN-H01/Fast-in-Slow
- arxiv.org/html/2505.22657v1（3DLLM-Mem）；arxiv.org/html/2502.19417v1（Hi Robot）；lookplangraph.github.io/；arxiv.org/html/2410.02193v1
- github.com/google-deepmind/mujoco；github.com/google-deepmind/mujoco_playground；github.com/google-deepmind/mujoco_warp
- github.com/Genesis-Embodied-AI/genesis-world；the-decoder.com/genesis-speeds-up-ai-robot-training...；genesis-world.readthedocs.io/
- github.com/haosulab/ManiSkill；arxiv.org/abs/2410.00425；simpler-env.github.io/；github.com/simpler-env/SimplerEnv；arxiv.org/html/2405.05941v1
- github.com/mees/calvin；arxiv.org/abs/2112.03227；libero-project.github.io/main.html；roboticscenter.ai/en/benchmarks/rlbench；arxiv.org/html/2411.05821v1
- arxiv.org/pdf/2405.02292（ALOHA）；arxiv.org/pdf/2510.01023（Prometheus）；arxiv.org/abs/2411.11839（RoboGSim）；openreview.net/pdf?id=H4SyKHjd4c（EmbodiedSplat）
