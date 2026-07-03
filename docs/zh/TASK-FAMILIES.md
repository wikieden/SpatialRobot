# 任务族 — 导览导游 · 多样家务 · 寻找遗失物 · 保洁员 · 接待员（规划）

> **状态：仅规划。** 暂无代码。本文扩展生产端到端集成
> ([INTEGRATION-E2E.md](../en/INTEGRATION-E2E.md)) ，新增三个任务族及其对全栈的需求。
> 每个族都按同一套六条生产标准衡量：**可做** · **可复现** · **可追溯** · **安全可靠**
> · **准确率高** · **成功率高**。落地顺序见 §6。

## 0. 现状（事实基线）

| 层 | 现有 | 新任务族复用 |
|---|---|---|
| 动词（D3 manifest，`bodylink/manifest.py`） | `navigate, grasp, place(target,location), detect, open_door, operate_appliance(洗碗机/灶/微波炉/洗衣机), charging` | 导览复用 `navigate`；家务复用 `place/open_door/operate_appliance`；寻物复用 `navigate/detect/grasp` |
| 意图（`mindloop/plan.py`） | `task · question · chat`（封闭 `Literal`） | 三族都映射到这三类 — **无需新增意图字面量** |
| 记忆（`tempomem`） | `define_region` / `contents(region)`；`history(node)→Observation.ts`；`recent(n)`；衰减 | 区域 ⇒ 导览叙述 + 家务摆放；`history`+`ts` ⇒ 寻物的最后出现位置 + 时近度 |
| 安全（`Phylax`/`Policy`） | `adult_only_verbs` 角色门 | 扩展 **区域访问** + **按人隐私**（§3） |
| 评测台（`skillforge/scenario.py`） | 4 指标：规划 · 策略 · 重规划 · 成功率；逐场景 trace 行数 | +3 指标（§4）；+3 套件 |

**净新增**（第三轮评审后更新 —— 精确计数见 §7f）：
约 12 个原子动词 + 1 个宏动词、6 个 Tier-1 记忆接口（+2 张 `.smem` 表）、
3 项 Phylax 扩展（`robot_service`、服务区域门、命名参数检查）、9 个指标、6 套套件。详见下。

---

## 1. 导览导游 — Tour / Guide

**目标。** 机器人带一位或多位访客游览场所/家中，从记忆里逐区域讲解 —— "这是厨房，台面上有水壶和两个杯子 [#7][#9]"。

**核心动词。** `present(target)` = 面向/指向某区域或物体 + 讲一段以记忆为依据的描述。讲话走 `Speaker` 接缝 / `VoiceLoop`（voicelink 已建好）。每条声称都 **引用节点 id**（B2R 引用契约）。讲解内容取自 `contents(区域)`；区域由 `define_region` 定义。

---

### 1.1 导览模式

三种运行模式共享同一路点 plan 结构，区别在于谁控制配速、服务多少访客。

#### 模式 A — 自由导览（互动式）

一对一或小团体，由人控制节奏，用户或讲解员发出每次转场信号。

```
navigate(第i站) → present(第i站) → wait_for_signal()
  → [该站可选问答] → navigate(第i+1站) → …
```

- **触发**：访客/讲解员的显式指令（"继续"、"下一站"，或插话问题视为"这里讲完了"）。
- `wait_for_signal()` 是 **Listener 门控等待**（voicelink `EndpointListener`）：机器人停在该站，随时准备回答问题，直到听到继续信号或超时。
- 该站提问 → 作为子对话处理（一轮 `converse`）；访客发出就绪信号后继续导览。
- **策略门**：若访客询问私密区域，Phylax 拦截；机器人说"那片区域不对外开放"并保持路线。

#### 模式 B — 领队模式（自动带队）

机器人自主推进完整导览，无需人工触发转场。适合团体（博物馆、办公室、展厅）。

```
for 站点 in 行程:
    navigate(站点) → present(站点) → timed_pause(站点.停留秒数)
→ conclude_tour()
```

- 每站 `停留秒数` 来自任务 manifest 或默认值（如 30 秒）。
- 机器人自主掌控时间；访客跟随（动态跟随/人群感知延后至主动感知 P4）。
- 任意时刻仍可被插话打断（§1.3）；机器人插入回答后继续自动推进循环。
- `conclude_tour()` = 导航回初始位置 + 致辞收尾。

#### 模式 C — 自由聊天 / 主动服务（环境服务）

**不在**结构化导览任务中时，机器人进入*自由服务*模式：响应临时请求，在**职责范围**内主动提供帮助。

- 不建模为 `task`；实现为空闲 `VoiceLoop` 迭代：监听 → 意图匹配服务 → 完成；否则自由对话。
- **范围过滤**（Phylax 预检，先于任何移动）：只响应职责范围内的请求（如带去洗手间、回答场地问题、引导至展品）。超范围请求（如"帮我买吃的"）→ 礼貌拒绝。
- **主动提议**：若机器人感知到访客迷路或问题模糊，可主动询问"需要我带您去 X 吗？"—— 只问一次，不重复催问（防骚扰策略）。
- 环境服务模式是无 `task` 激活且 `VoiceLoop` 运行时的**默认回落状态**。

---

### 1.2 区域访问策略（Phylax 扩展）

*访客*是不可信人。私密区域（卧室、书房、机房）在 `define_region` 记录上标注 `access_policy: guest_blocked`。

- 任何会 `navigate` 或 `present` 被封锁区域的 plan 步骤，由 Phylax 在**编译期**（非执行期）否决。
- 环境服务模式下，会进入封锁区域的服务请求同样被拦截，机器人说："那里是私密区域，我无法带您前往。"
- 屋主/可信用户可在运行时重置策略注解（超出本文范围；标记进访问控制规范）。

**区域由谁定义、何时定义（已拍）。** 区域在**安装期一次性**由屋主/安装向导人工标注——
房间名 + bbox 走 `define_region`，不由机器人自主推断。区域语义（"这算不算私密"）是*判断*，
不是几何聚类能自动产出的；导览隐私门直接 key 在标签上，标错即安全事故。运行时对区域**只读**。

**默认立场（已拍）。** 区域访问为**默认放行 + 显式拉黑**：仅私密区域标注
`access_policy: guest_blocked`；未标注的*已知*区域可访问。一条护栏保留 fail-closed 精神：
运行时遇到**未知/从未登记**的区域按*拒绝*处理，不算"不在拉黑表 ⇒ 放行"——默认放行只
延伸到安装期走查实际登记过的区域。

---

### 1.3 中断机制

任意导览模式（A 或 B）**随时可被中断** —— 无论正在导航还是正在讲解。

**中断分类**

| 中断类型 | 示例 | 处理方式 |
|---|---|---|
| **插话 / 提问** | "这是哪年建的？" | 内联回答（一轮 `converse`），立即恢复 |
| **服务请求** | "带我去洗手间" | 挂起导览状态，完成服务子任务，恢复 |
| **紧急情况** | "我不舒服 / 火警" | 挂起导览，走 Phylax 安全通道上报，**不自动恢复** |

**状态机**

```
导览中 ──插话──► 处理中断
                    │
          ┌─────────┴──────────┐
       插话/提问            服务请求
     （内联回答）        （子任务完成后）
          └─────────┬──────────┘
                    │
                 是否恢复？
             是 ──► 导览中（从已保存站点索引继续）
             否 ──► 收尾 或 空闲
```

- **保存状态**：进入`处理中断`前，机器人将 `(当前站点索引, 剩余站点)` 记录到当前 trace 记录。
- **恢复**：机器人说"继续导览 —— 我们刚才在[站点名称]"，然后从保存的索引续行。
- **紧急情况不自动恢复**：只有访客重新请求导览才继续。
- 插话通过现有 §5b.1 机制实现（Listener 触发 `barge_in` 事件 → Replanner 插入中断子任务 → 导览 plan 暂停）。

**服务子任务示例（洗手间）**

```
suspend_tour(save_index=i)
navigate(区域="洗手间") → present(区域="洗手间")   # "洗手间在这里"
speak("准备好了告诉我，我们继续导览。")
wait_for_signal()
resume_tour(from_index=i)
```

- 洗手间子任务同样经过 Phylax 检查（洗手间是否公共区域？默认是），全程 trace 作为嵌套记录写入，带 `parent_episode_id`。

---

### 1.4 需求 / 缺口

- **可做**：manifest + `MockBody` + `SimDeviceAdapter` 加 `present`、`wait_for_signal`、`conclude_tour`；一致性套件保持通过。
- **可追溯**：每站讲解是一条 trace 记录，引用所讲节点 id；中断子任务是带 `parent_episode_id` 的嵌套记录。
- **安全**：区域访问策略（§1.2）+ Phylax 编译期否决 + 紧急情况不自动恢复。
- **准确率**：讲解须引用该区域正确 id ⇒ 新增**引用准确率**指标（§4）。
- **成功率**：所有非私密站点均到达并讲解；中断处理不丢失导览状态。
- *延后*：跟随访客/人群配速（需主动感知，动态场景 P4）；多讲解员交接；基于参与度信号自动调整 `停留秒数`。

**基线场景**

| 场景 | 模式 | 关键断言 |
|---|---|---|
| `home_tour_interactive` | A | 3 站，每站等"继续"信号；卧室被封锁 |
| `home_tour_auto` | B | 3 站自动配速，无人工输入；同样封锁卧室 |
| `tour_bathroom_interrupt` | A 或 B | 导览中途"带我去洗手间" → 子任务 → 从保存索引恢复 |
| `tour_question_inline` | A 或 B | 讲解中插话问答 → 恢复，不丢失站点索引 |
| `ambient_offer` | C | 访客问题模糊 → 机器人提议引导 → 访客接受 → 进入模式 A |
| `ambient_scope_block` | C | 超范围请求 → 礼貌拒绝，不移动 |

---

## 2. 多样家务 — Varied Household Chores

**目标。** 超越取物：收纳归位、擦台面、浇花、用家电、倒垃圾 —— 每个都是多步、常多物的 plan。

**子任务与动词覆盖。**

| 家务 | plan | 动词状态 |
|---|---|---|
| 收纳归位 | `grasp(x) → place(x, 区域)` ×N | 复用 `place` —— 但 `location` 须解析到 **区域锚点**（新绑定） |
| 跑洗碗机/洗衣机/灶 | `open_door → place → operate_appliance` | 三者全复用（顺序要紧） |
| 擦台面 | `wipe(target)` | **新动词** |
| 浇花 | `navigate → pour(target)` | **新动词** `pour` |
| 倒垃圾 | `grasp → dispose(target)` | **新动词** `dispose`（或 `place(x, 垃圾区)` —— 落地时定） |

**需求 / 缺口。**
- **可做**：manifest/body/sim/conformance 加 `wipe`、`pour`、`dispose`。
- **可复现**：多物收纳 = planner 查记忆把一条指令展开成 N 个子任务 ⇒ 固定场景下确定。
- **可追溯**：顺序约束（先开后放、先放后启）须在 trace 体现；违序触发重规划，而非静默失败。
- **安全**：灶/刀/利器类家务保持 `adult_only`；**绝不**因孩子指令开灶（已支持，扩覆盖）。
- **准确率**：正确动词序列 *且* 正确顺序 ⇒ 规划准确率已评元组；再加显式有序前置检查。
- **成功率**：每件家务到达终态成功；失败（抓取打滑）经现有有界 Replanner 恢复。

**基线场景**：`tidy_table`（N× grasp+place 到货架区）、`run_dishwasher`（开→放→启，有序）、`water_plants`（navigate→pour）、`stove_is_adult_only`（孩子被挡、成人放行）。

---

## 3. 寻找遗失物 — Find the Owner's Lost Object

**目标。** "我钥匙在哪？" / "找下我眼镜。" 从记忆给出 **位置 + 时近度 + 置信度**；若未知，跑有界 **主动搜索**。

**两条路径。**
1. **已知**（在记忆、较近） ⇒ `question`：答"在沙发上，8 分钟前见过 [#12]"。可选提议取来（`navigate→grasp`）。
2. **未知 / 陈旧** ⇒ `task`（主动搜索）：在排序后的区域上 `navigate(可能区域) → detect`，限 *K* 站；如实报告找到/未找到。

**新记忆只读助手**（建议，保持 numpy-only、只读）：
`last_seen(name) -> (region, age_s, confidence)` —— 由 `history(node).ts` +
`contents`/区域归属 + 衰减组合。（可作 `tempomem` 查询方法，或在评测台拼装；建议放
`tempomem`，因为是对现有状态的纯只读查询。）

**需求 / 缺口。**
- **可做**：`last_seen` 助手；主动搜索复用 `navigate/detect/grasp`（无新动词）。
- **可复现**：固定记忆 + 搜索路径植入检测 ⇒ 确定。
- **可追溯**：答案引用节点 id；搜索路径逐站 trace。
- **安全 / 隐私**：**陌生人** 问 *主人* 的物品 → 拒绝 —— **按人隐私门**（见下）。定位他人物品属敏感。
- **准确率**：报 *正确* 区域（**定位准确率** 指标）与时近度；**不得过度声称**。陈旧判据
  （已拍）：复用现有衰减 `confidence`（半衰期 30 天，低于 `min_conf=0.1` 剪除）作*唯一*
  信号——`confidence ≥ 0.7` ⇒ 照常作答；`< 0.7` ⇒ 含糊处理（"3 小时前见过，可能挪了"），
  绝不断言。`age_s` 仍*说出来*表达时近度，但不再单开一套平行阈值系统。
- **成功率**：已知路径答对；搜索路径在 K 站内找到，或真物不在时如实报未找到（如实未找到算 *成功*，非失败）。

**基线场景**：`find_known_recent`（答区域+时近度，引 id）、`find_stale_hedges`（旧观测 ⇒ 含糊作答，不过度声称）、`find_by_search`（记忆中缺失 ⇒ navigate+detect 在 K 站内找到）、`find_stranger_refused`（非主人问 ⇒ 隐私拦截）。

### 两个新策略维度（Phylax 扩展）

| 维度 | 规则 | 服务 |
|---|---|---|
| **区域访问** | 角色/人 → 可带去或可告知的区域集合 | 导览（私密房）、寻物 |
| **按人隐私** | 定位/讲述某人物品仅对该主人（或按策略对成人）开放 | 寻物（拒陌生人） |

两者都契合现有基于卡片、默认拒绝的 Phylax（不可信 ⇒ 拒）。

---

## 4. 保洁员 — Cleaner / Housekeeping

**目标。** 机器人对场所进行系统清洁 —— 地面、台面、垃圾清运、耗材补充 —— 按例行计划或在检测到脏污时响应执行。

**Plan 形态。**

| 触发 | plan | 说明 |
|---|---|---|
| 例行计划 | `for 区域 in 清洁行程: navigate(区域) → clean_region(区域)` | 逐房间，调度驱动 |
| 响应式（检测到脏污） | `navigate(脏污位置) → clean_spot(脏污位置)` | 最高优先级队列优先 |
| 清运垃圾 | `navigate(垃圾桶) → grasp(袋) → dispose(袋, 室外桶)` | 复用 `grasp` + `dispose` |
| 耗材补充 | `navigate(储物间) → grasp(物品) → navigate(目标位置) → restock(物品, 目标位置)` | **新动词** |

**新动词。**

| 动词 | 语义 |
|---|---|
| `sweep(region)` | 导航 + 扫/吸地 |
| `mop(region)` | 导航 + 拖地；执行前后各触发 `warn_wet_floor(region)` |
| `warn_wet_floor(region)` | 语音提示 + 可选放置警示牌；**安全动词** |
| `restock(item, location)` | 在指定补充点放置耗材（纸巾、皂液、咖啡胶囊等） |

`wipe(surface)` 和 `dispose(target)` 复用自 §2（多样家务）。

**记忆。** 区域地图提供清洁行程与房间邻接关系。清洁时间戳可存为关系（`relate(区域节点, "last_cleaned", 时间戳节点)`），支持基于计划的调度而无需外部状态。

**需求 / 缺口。**
- **可做**：manifest + `MockBody` + `SimDeviceAdapter` + `_VERB_TABLE` 加 `sweep`、`mop`、`warn_wet_floor`、`restock`；`wipe`/`dispose` 已规划。
- **可复现**：固定场景 + 固定行程 → 确定性步骤序列。
- **可追溯**：每个区域清洁是一条 trace 记录；`warn_wet_floor` 事件作为安全子记录写入。
- **安全**：湿地板是滑倒风险 —— `mop` 始终在前后各调用 `warn_wet_floor`；清洁剂由机器人自行操作（不交给访客或儿童）；危险工具类家务（工业清洁剂）在 manifest 标 `adult_only`。
- **准确率**：所有计划区域按序清洁；警告正确触发 ⇒ 新增 **清洁覆盖率** 指标（§6）。
- **成功率**：完整行程完成或响应任务解决；单房间被占用时延后处理并报告缺口。

**策略。** 保洁员以 `cleaner` 角色操作，按计划访问所有非私密区域。有人占用时：机器人敲门 +
`wait_for_signal()`（复用导览 §1.1 机制——带自身超时的 courtesy 在场检测，**不是**
`ASK_HUMAN`/Clarifier 接缝，不占问询预算，D-L），超时则推迟到下一时段。私密区域需屋主明确授权。

**基线场景**

| 场景 | 关键断言 |
|---|---|
| `routine_sweep` | 3 区域行程，依序扫地，每个记为 trace 记录 |
| `mop_wet_floor_warning` | 拖地前后各触发警告；警告写入 trace；滑倒风险标志留存 |
| `reactive_mess` | 检测到溅污 → 导航 + 擦拭 → 清洁完成后恢复例行 |
| `restock_consumable` | 皂液不足 → 导航储物间 → 导航洗手间 → 补充 |
| `occupied_room_defer` | 房间有人 → 延后，继续行程，报告缺口 |

---

## 5. 接待员 — Receptionist / Host Service

**目标。** 机器人迎接访客、接受饮品订单、送上茶/咖啡/水，在职责范围内提供主动式接待服务。

**Plan 形态。**

| 动作 | plan |
|---|---|
| 迎客 + 接单 | `navigate(客人) → greet(客人) → take_order(客人) → [备饮] → deliver(饮品, 客人)` |
| 按已知偏好送饮 | `navigate(客人) → greet(客人) → offer(偏好饮品, 客人)` |
| 主动续杯 | `navigate(客人) → offer(续杯, 客人)`（由杯量观测或计时器触发） |
| 备饮 | `navigate(饮品台) → pour(液体, 杯)` （复用 §2 的 `pour`） |

**新动词。**

| 动词 | 语义 |
|---|---|
| `greet(target)` | 导航面向客人 + 语音问候；不执行任何操作 |
| `take_order(target)` | Speaker 询问饮品偏好；Listener 记录答案；写入 `prefers` 关系到记忆 |
| `offer(item, target)` | 将物品递给某人并等待接受信号（不同于 `place` —— 需要人主动接收） |
| `deliver(item, target)` | `navigate(target) → offer(item, target)` 的组合宏 |

`pour(liquid, container)` 复用自 §2（浇花动词，语义扩展至饮品）。

**记忆 + 个性化。**

访客偏好以记忆关系存储：
```
relate(客人节点, "prefers", "绿茶")
relate(客人节点, "allergic_to", "牛奶")
```

再次到访时，planner 查询 `query("[客人] 喜欢什么")` → 无需询问直接主动送上偏好饮品。每次服务都是 trace 记录，引用客人节点和饮品节点。

**需求 / 缺口。**
- **可做**：manifest + `MockBody` + `SimDeviceAdapter` + `_VERB_TABLE` 加 `greet`、`take_order`、`offer`、`deliver`；`pour` 已规划。
- **可复现**：脚本化客人 + 脚本化订单 → 确定性 plan。
- **可追溯**：迎客、接单、备饮、送达各自记为 trace 子记录，引用客人节点和饮品节点 id。
- **安全**：热饮由机器人内部操作（机器人端杯，无安全阻断）；**酒精饮品** 为 `adult_only`（Phylax 拦截向儿童/陌生人/不可信角色提供酒精）；过敏门控 —— 若客人有 `allergic_to` 关系且所请饮品含该过敏原，Phylax 拦截并推荐替代选项。
- **准确率**：正确饮品送达正确客人；再访客人偏好正确回调 ⇒ 新增 **送餐准确率** 和 **偏好回调率** 指标（§6）。
- **成功率**：每次订单完成或礼貌拒绝（缺货 ⇒ 如实告知 + 提供替代）。

**策略。** 接待员以 `host` 角色操作。主动提议：每轮互动只提一次（防骚扰）。超范围请求（订外卖、跑腿）→ 礼貌拒绝。

**基线场景**

| 场景 | 关键断言 |
|---|---|
| `serve_tea_on_order` | 客人点茶 → 接单 → 倒水 → 送达 → trace 引用节点 id |
| `serve_with_preference` | 记忆中有偏好 → 机器人主动送偏好饮品，无需询问 |
| `alcohol_blocked` | 儿童要酒 → Phylax 拦截，推荐果汁 |
| `allergy_gate` | 对牛奶过敏的客人点拿铁 → 拦截 + 推荐无乳替代 |
| `refill_proactive` | 杯量不足（或计时器） → 机器人主动导航并提议续杯 |
| `out_of_stock_honest` | 所请饮品缺货 → 如实告知 + 提供替代 |

---

## 5c. 场景语义 —— 静态 + 动态理解（横切）

五个任务族都要求机器人**以当前和近期世界状态为推理基础**。无法准确讲解的导览站、
客人还在时就进去清洁的房间、送错人的饮品 —— 根源都是场景理解不足。
本节规定所需的静态 + 动态联合语义模型，以及它对记忆系统提出的具体接口需求。

---

### 5c.1 静态场景语义

静态语义描述**存在什么、彼此如何关联** —— 构成每个任务背景的不变量或缓变事实。

**所需语义维度**

| 维度 | 示例 | 需要方 |
|---|---|---|
| 物体身份与类别 | `杯子 #12 : DrinkingVessel`、`桌子 #3 : Surface` | 所有族 |
| 空间位置 | 所属区域、世界坐标系位置 | 所有族 |
| 物体状态 | `开/关`、`满/空`、`干净/脏`、`在场/缺失` | 家务、保洁员、接待员 |
| 材质 / 危险标签 | `易碎`、`锋利`、`烫`、`重` | 家务、保洁员（安全） |
| 关系边 | `on(杯, 桌)`、`in(皂液, 皂液器)`、`near(花, 窗)` | 家务、寻物、保洁员 |
| 区域语义类型 | `洗手间`、`厨房`、`私密书房` | 导览、保洁员（访问策略） |
| 区域访问策略 | `guest_blocked`、`cleaner_scheduled`、`adult_only` | 导览（§1.2）、保洁员 |
| 人员身份与角色 | `访客`、`儿童`、`屋主`、`陌生人` | 所有族（Phylax 门） |
| 偏好 / 过敏关系 | `prefers(访客A, "绿茶")`、`allergic_to(访客A, "牛奶")` | 接待员 |

静态语义在场景布置时由 `add_detections()` / `define_region` / `relate()` 填入，
在被显式更新或衰减之前保持有效。

---

### 5c.2 动态场景语义

动态语义描述**正在发生什么变化** —— 机器人在长时间任务中必须持续跟踪的事件和状态转变。

**事件分类**

| 事件类别 | 示例 | 产生方 | 消费方 |
|---|---|---|---|
| 物体状态变化 | 检测到溅污、门被打开、杯子空了 | worldsense 检测 | 保洁员（响应式）、接待员（续杯） |
| 物体位置变化 | 钥匙从沙发移到了书桌 | tempomem 帧差分 | 寻物（陈旧失效）、导览 |
| 人员位置变化 | 访客进入厨房、孩子离开房间 | worldsense 人体检测 | 导览（私密房实时守卫）、保洁员（延后） |
| 人员活动变化 | 访客由闲坐转为工作 | 姿态 + 上下文推理 | 接待员（主动服务时机）、导览（配速） |
| 危险事件 | 湿地板、路径障碍 | worldsense / 机器人自身 | 保洁员（wet_floor 警告）、所有族（安全） |
| 任务触发状态变化 | 机器人拖地 → 地板湿、机器人放好杯 → 杯满 | plan 执行日志 | 保洁员（自身状态追踪） |

动态语义要求记忆系统记录事物**何时**发生变化，而不只是**存在着**什么。

---

### 5c.3 推理整合（按族）

| 族 | 静态查询 | 动态查询 |
|---|---|---|
| **导览** | `contents(region)` → 讲解节点 id | `current_occupants(region)` → 运行时私密房守卫 |
| **家务** | `contents(货架)` → 整理目标；`on(x,y)` → 前置条件排序 | `last_changed(region)` → 台面是否已经干净 |
| **寻物** | `last_seen(name)` → 区域 + 时近度 | 检测时间戳老旧 → 含糊表达 vs 断言 |
| **保洁员** | `access_policy(region)` → 排程；`state(region, "dirty")` → 优先级 | `current_occupants(region)` → 延后；响应式事件 → 打断行程 |
| **接待员** | `prefers(客人, *)` + `allergic_to(客人, *)` → 订单校验 | `state(cup, "empty")` 或计时器 → 主动续杯触发 |

Brain 的 planner 通过 `query()` / `answer()` 读取这些 —— 与 P1–P5 已用的同一公开接口。
无需新意图类型；查询是经由现有 Reasoner 上下文的内部记忆读取。

---

### 5c.4 记忆系统（tempomem）需求

以下是从上述分析推导出的**具体新接口**，按优先级分层。

#### Tier 1 —— §4-§5 基线场景所需（无 LLM，可自主）

| 新接口 | 签名 | 语义 |
|---|---|---|
| `last_changed(region)` | `→ (age_s, event_type)` | 该区域上一次被修改（物体进出、状态变化）是多久前？保洁员调度使用。 |
| `current_occupants(region)` | `→ list[PersonNode]` | `current_region` 属性等于此区域的人员节点列表。保洁员延后 + 导览私密房运行时守卫使用。 |
| `state(node, attr)` | `→ value \| None` | 读取节点的命名属性（如 `state(cup_12, "fill_level")`、`state(region_3, "dirty")`）。 |
| `set_state(node, attr, value, ts)` | `→ None` | 写入带时间戳的状态属性。每个改变世界状态的动词执行后由 plan 执行日志调用（拖地 → 湿、倒水 → 满）。 |
| `add_event(type, location, ts, payload)` | `→ event_id` | 向事件流追加一条语义事件（溅污、人员进入、物体移动）。 |
| `query_events(type, region, since_ts)` | `→ list[Event]` | 拉取近期指定类型事件，用于响应式规划（保洁员："上次扫地后有溅污吗？"）。 |

六个接口均为**只读或只追加**，作用于现有结构，无需 schema 迁移。
`state` / `set_state` 为现有节点添加键值属性包。
`add_event` / `query_events` 在 `.smem` SQLite schema 新增一张轻量 `events` 表。

#### Tier 2 —— 完整动态闭环所需（依赖主动感知，延后至 P4）

| 新接口 | 语义 | 依赖 |
|---|---|---|
| `update_person_location(person, region, ts)` | 更新人员节点的 `current_region` 属性；为 `current_occupants` 提供数据。 | worldsense 实时人体检测 |
| `activity_tag(person, tag, ts)` | 在人员节点上设置轻量活动标签（`idle`、`working`、`eating`）。 | 姿态估计 / 活动识别（P4） |
| `detect_state_delta(region, since_ts)` | 对比区域两个时间点的内容快照：物体新增、移除、位移。供主动保洁员和寻物陈旧失效使用。 | worldsense 持续扫描（P4） |

#### Tier 3 —— 便利组合（可驻留评测台，不进核心）

```python
# 评测台辅助函数（由 Tier 1 原语组合）
def is_region_occupied(mem, region) -> bool:
    return len(mem.current_occupants(region)) > 0

def is_stale(mem, node) -> bool:
    # 已拍单信号判据：衰减 confidence，0.7 分界（§3）
    _, _, confidence = mem.last_seen(node.name)
    return confidence < 0.7

def cup_needs_refill(mem, cup_node) -> bool:
    return mem.state(cup_node, "fill_level") in ("empty", "low", None)
```

这些**不是 tempomem API** —— 驻留在 `skillforge/scenario.py` 或 `mindloop` 辅助模块。
核心保持 numpy-only、无状态。

---

### 5c.5 静态 + 动态整合契约

长时间任务中 worldsense、tempomem、mindloop 三者之间的基本契约：

```
worldsense 检测          tempomem 存储                  mindloop 推理
────────────────────────────────────────────────────────────────────────
帧 Detections      →  add_detections() / commit()    →  contents(region)
人员位置           →  update_person_location()        →  current_occupants(region)
物体状态变化       →  set_state(node, attr, val)      →  state(node, attr)
语义事件           →  add_event(type, loc, ts)        →  query_events(type, region, since)
────────────────────────────────────────────────────────────────────────
所有写入带时间戳 → 衰减 + 时近度是一等公民 → 陈旧时自动触发含糊表达
```

**不变量**：每次状态或事件写入都经过 tempomem 并携带时间戳。
任何机器人模块都不维护自己的并行世界模型。记忆系统是场景语义——无论静态还是动态——的唯一事实来源。

---

### 5c.6 需求 / 缺口汇总

| 条目 | 状态 | 负责方 |
|---|---|---|
| `last_seen(name)` | 已规划（§3） | tempomem |
| `define_region`、`contents(region)`、`relate()` | **已存在** | tempomem |
| `state(node, attr)` / `set_state(node, attr, val, ts)` | **新 — Tier 1** | tempomem |
| `last_changed(region)` | **新 — Tier 1** | tempomem |
| `current_occupants(region)` | **新 — Tier 1** | tempomem |
| `add_event` / `query_events` | **新 — Tier 1**（`.smem` 新增 `events` 表） | tempomem |
| `update_person_location` | 新 — Tier 2（延后 P4） | tempomem + worldsense |
| `activity_tag` / `detect_state_delta` | 新 — Tier 2（延后 P4） | tempomem + worldsense |
| 评测台辅助函数（`is_region_occupied` 等） | 新 — Tier 3 | skillforge / mindloop |

**基线可测性**：Tier 1 接口完全可脚本化（无需实时感知）。
`set_state` / `add_event` 由测试评测台调用以模拟世界变化；
`state` / `query_events` / `current_occupants` 由 planner 调用。
全部确定、无网络。

---

## 6. 新评分指标（评测台）

扩展 `EvalReport` / `IntegrationReport`（`skillforge/scenario.py`）—— 同现有四项的 ok/total 形态：

| 指标 | 定义 | 族 |
|---|---|---|
| **引用准确率** | 讲解/回答恰好引用所讲区域/物体所属的节点 id | 导览、寻物 |
| **定位准确率** | 报告区域 == 物体真值区域 | 寻物 |
| **搜索成功率** | K 站内找到，**或** 真物缺失时如实报未找到 | 寻物 |
| **清洁覆盖率** | 行程中计划区域的实际清洁比例 | 保洁员 |
| **送餐准确率** | 正确饮品送达正确客人（物品 + 人均正确） | 接待员 |
| **偏好回调率** | 再访客人在无需显式订单情况下获得其存储偏好饮品 | 接待员 |

`meets(...)` 增加这些阈值；go/no-go 裁决覆盖五族。

---

## 7. 生产标准覆盖（汇总）

| 标准 | 机制（新增） |
|---|---|
| 可做 | 4+4+4 动词（三组族）+ `last_seen` 助手；每次加完一致性套件须保持通过 |
| 可复现 | 逐场景脚本化基线（无网络）；固定场景 + 植入检测 |
| 可追溯 | 每条讲解/摆放/搜索站/清洁记录/服务记录都是 trace 记录、引用节点 id |
| 安全可靠 | Phylax 加区域访问 + 按人隐私 + 过敏门控 + 湿地板警告；家电/利器/酒精保持成人专属；默认拒绝 |
| 准确率高 | 引用 + 定位 + 清洁覆盖率 + 送餐准确率 + 偏好回调率；诚实规则（陈旧不过度声称） |
| 成功率高 | 有界 Replanner 恢复打滑；如实未找到/缺货如实告知算成功；逐套件成功率门 |

---

## 7b. 执行动态（横切 —— 所有族）

调度循环之上三个相互作用的行为。**当前事实：** `Brain._dispatch_plan` **原子**跑完整个
plan（无抢占点）；P4 `Replanner` 把类型化失败映射为 `RETRY/ADJUST/REROUTE/SKIP/ESCALATE`，
但 **ESCALATE 是死胡同**（stop+speak，不恢复、从不问询）；**没有**打断或问询人类的接缝。
`TaskStatus.ABORTED` 已存在但未用。

### 5b.1 打断 —— 随时聊天/插话 → 重规划

任务执行*中*人开口，机器人须响应，而非闷头做完。

- **机制**：把调度做成**可抢占步进器**，带恢复游标（剩余子任务索引）+ **打断收件箱**
  （新 `InterruptSource`，由 Listener 喂入），每步之间检查 —— 长步骤再加子任务内协作式取消。
- **打断分类** 经专用 `BargeClassifier`（组合现有 `IntentRouter`；`Intent` 字面量保持封闭三类
  —— 打断是*另一个*决策空间，见 §5d D2）：
  - *闲聊 / 提问* → 作答（`Brain.ask`），然后从游标**恢复**剩余 plan（状态保留）。
  - *新指令* → **取代**（后者优先）：当前 plan 置 `ABORTED`，对新目标重规划 —— 但当前任务**接近完成**或**处于不可逆中**时须**确认**。
  - *停止 / 取消* → 中止 → `ABORTED`，语音确认。
  - *纠正*（"不，红的那个"） → 对*同一*目标带修正重规划。
- **安全**：不可逆步骤（灶已开）中被打断 → 做完或安全中止，绝不动作中途硬杀。
- **可追溯**：打断 + 恢复/取代/中止决策是一条 trace 记录。

### 5b.2 失败 → 按情况重规划（扩展 P4）

类型化错误 → 有界恢复的循环已有，两处缺口：

- **ESCALATE 不该总是死胡同。** 当目标*靠更多信息仍可达*时，路由到 **ASK_HUMAN**（5b.3）
  而非放弃。只有真正不可恢复（硬件故障、安全停机）才保留 stop+speak 的 ESCALATE。
- **改变信念的失败**（物体不在预期处） → **重感知再重规划**：retry 前加一条 `detect` 刷新路径 ——
  这正是寻物族（§3）和动态场景 P4 需要的主动搜索钩子。

### 5b.3 必要时问询人类（澄清门）

机器人主动发问，区别于人主动打断。

- **接缝**：新 `ReplanAction.ASK_HUMAN(question)` → 经 `Speaker` 发出*有针对性*的问题，
  经 `Listener` **等待**回复，把答案折回路由/规划，然后恢复。
- **触发**：指代歧义（"那个杯子"但有 3 个）、仅人能解除的前置（"柜子锁了"）、反复无提示失败
  （escalate→ask）、需同意的安全边界。
- **有界**：**问询预算**（每任务 ≤2 次）—— 超出 ⇒ 如实 ESCALATE-停。绝不死循环。
  口径（已拍）：预算**按单个 task 清零**（每次新 `_plan_task`/新 SubTask 序列起始重置为 2）；
  **不设 conversation 级总量**——同一次对话里问过前一件事，不能饿死后面真正卡住的任务。
- **安全**：澄清回答**就是一条指令** ⇒ 经 Phylax 复审（陌生人不能靠澄清回复解锁成人专属动词）。
- **不过度发问**：仅真正受阻时才问 —— 有度量（5b.4）。

### D-I：物体绑定歧义——考虑可替换性

**问题。** `_resolve_node_id`（plan.py:244–250）硬编码 `mem.query(mention, k=1)`——只取
top-1，从没看过第二候选，编译期压根没有信号能判"歧义"。但不是所有多候选都值得问：
"拿张餐巾纸"匹配到 5 张一模一样的餐巾纸，任一张都行，不需消歧。

**决策。** `_resolve_node_id` 改查 `k=3`。**仅当**候选语义不可替换才算歧义：
1. **label 不同**、分数接近（如"杯子"同时贴近 mug 节点和 cup 节点）→ 歧义，问。
2. **label 相同但指令带区分修饰词**（"红色那个杯子"）而多个候选仍都满足该修饰词 → 歧义，问。

**可替换——不问，直接取 top-1**：label 相同 **且** 指令无区分修饰词（"拿张餐巾纸"面对 5 张
同款）。这是消耗品/可互换物件的常见情况；这里问反而是打扰，不是帮助。数量词
（"拿两个杯子"）是 planner 层的事，不属绑定层，此处不管。

### 5b.4 新接缝、指标、场景

| 新接缝 | 用途 |
|---|---|
| `InterruptSource`（Listener 喂入） | 把人话推入运行中的调度（打断） |
| 可抢占步进器 + 恢复游标 + 问询预算 | 使上述成为可能的调度循环重构 |
| `ReplanAction.ASK_HUMAN` + `clarify(q)->answer` | 经 Speaker/Listener 的机器人主动澄清 |
| （复用）`TaskStatus.ABORTED` | 取代 / 停止结果 |

| 新指标 | 定义 |
|---|---|
| **打断处理准确率** | 打断被分类到正确动作（恢复 / 取代 / 中止 / 纠正） |
| **澄清精确率** | 仅真正歧义/受阻时才问（不过度发问） |
| **澄清解决率** | 问 → 人答 → 任务随后成功 |

**基线场景**（脚本化打断 + 脚本化人答 = 确定、无网络）：`barge_in_chitchat_resumes`、
`barge_in_supersedes`、`barge_in_stop`、`fail_then_ask_resolves`、`ambiguous_ref_asks`、`ask_budget_caps`。

**标准。** 可做：步进器重构 + `InterruptSource` + `ASK_HUMAN`，全可基线脚本化。
可复现：脚本化打断 + 脚本化澄清回复。可追溯：每次打断/问询/恢复/中止都 trace。
安全：不可逆步骤护栏、澄清经 Phylax 复审、问询预算上限、接近完成时取代需确认。
准确率：打断处理准确率 + 澄清精确率（不过度发问）。成功率：恢复还原完成；取代完成新目标；如实放弃算已处理。

---

## 7c. 数据与训练闭环（规划）

全栈流程图见 [FLOWS.md](../en/FLOWS.md) —— 组件图、请求生命周期、执行动态状态机、任务族流程、
数据/训练闭环（图 5）。这个闭环正是运行期**全程埋点**的**理由**。

**原则。** 运行期已为每个 路由/规划/安全/调度/重规划/澄清 决策发出一条引用节点 id 的
`TraceStore` episode。那份"废气"*就是*训练语料。skillforge 把它变成自我提升：

```
运行期 trace  →  数据集整理  →  skillforge ENPIRE 实验室  →  eval 门  →  提升回灌
(TraceStore)     (标注样本)      (Lab: Environment +          (run_eval /   (进 Brain
                                  PolicyAuthor → Rollout/      Integration-   planner /
                                  AttemptTree → Reward →       Report.meets)  overlay)
                                  Evolution → 结晶)
```

**奖励信号 = 六条标准数值化：** 成功、安全合规、步效率、**诚实**（陈旧不过度声称、如实未找到、
仅受阻才问询）。eval 门（`IntegrationReport.meets`）就是各族评分用的同一道 go/no-go —— 不通过它，
任何东西都不提升进活的 Brain。

**已建 vs 规划。** 已建：运行期 tracing ✅、eval 台 ✅、ENPIRE 行走骨架（`v0.1.0a0`，无网络，
`ScriptedAuthor`）✅。规划（下方落地第 6 步）：从真 trace 整理数据集、主机 LLM `PolicyAuthor`、
技能→Episteme 结晶、提升回灌门。

**数据需求**（使闭环可复现 + 可追溯）：
- 每条 episode 携带：意图、plan（动词序列 + 绑定节点 id）、安全裁决、结果/状态、重规划路径、
  问询+回答 —— 已是 trace 形态。
- 场景种子 + 场景 + 植入检测固定 → 确定性回放。
- 真 LLM rollout/标注来自主机（Cosmos+Qwen）；离线 trace 不需网络，故整理 + 基线训练可自主。

**两条设计约束（三轮）：**
- **奖励反作弊。** "仅受阻才问"与"诚实"奖励可被钻空子（从不问→歧义任务失败；总含糊→答案没用）。
  各配一个惩罚：歧义却没问、自信却过度含糊。奖励 = 净值，不是单边。
- **语料是敏感 PII。** trace 含家居布局、物品、谁问了啥。整理（步骤 6）须按户隔离 —— 不跨户泄漏、
  脱敏人身标识 —— 使"安全可靠"覆盖数据闭环，而非只覆盖运行期。

---

## 7d. 已拍决策与评审修正

对本规划做了一遍代码级评审，挖出两个正确性缺口 + 三个设计选择。owner 拍板 2026-06-30：

- **D1 —— 灶门控走参数级，不拆动词。** Phylax 按 `(verb, param)` 门控 ——
  `(operate_appliance, appliance_type=stove)` 成人专属，洗衣机/微波炉照常。manifest 的
  `appliance_types` 是程序清单来源；D3 开放词表保持干净（不繁殖 `operate_stove`）。同机制后续覆盖利器 `grasp`。
- **D2 —— 打断用专用 `BargeClassifier`，不加第 4 `Intent` 字面量。**
  主 `IntentRouter` 分*新话属哪类*（task/question/chat）；打断分*对运行中任务做什么*
  （闲聊→答+恢复 / 新指令→取代 / 纠正→replan-fix / 停止→中止）。两个决策空间 —— `Intent` 保持封闭三类，
  `BargeClassifier` 组合它。
- **D3 —— 问询人类是大脑级 `Clarifier` 接缝，规划时与重规划时都可调。** Speaker 问 + Listener 答 +
  Phylax 复审 + 预算 ≤2。规划时歧义（"那个杯子"3 个）与重规划时无提示失败都调它；
  `ReplanAction.ASK_HUMAN` 只是其一入口。

**评审修正（已并入落地顺序）：**
- **A —— 新动词要进 `_VERB_TABLE`，不止加 manifest 一行。** `present, wipe, pour, dispose` 须在
  `mindloop/plan.py` 的 `_VERB_TABLE` 补 `pre`/`eff`/`skill`，否则编译成空开放词表"哑动词" ——
  无有序前置（家务"先开后放"）、无 `WorldState` 回写。并入第 1 步。
- **B —— `place(target, location)` 的 effect 要编码区域。** 现 `place` effect 只用 `{target}`；
  区域相对摆放需把 location 进 effect（如 `robot.placed={target}@{location}`）。并入第 1 步。

---

## 7e. 二轮评审 —— 接缝 · 指标 · 可复现

第二遍代码级评审（接缝、eval 管线、可复现）。结论并入落地顺序；门槛于 2026-06-30 拍定。

- **K —— 评测台必须建区域**（`skillforge/scenario.py`）。`_build_memory` 零区域，但导览讲解、
  区域相对 `place`、寻物定位全需要。→ `Scenario` 加 `regions` 字段 + `_build_memory` 调 `define_region`。并入第 4 步（前置）。
- **H —— 打断需新接缝；`Listener` 是拉式。** `Listener.transcribe(audio)->str` 是请求/响应；打断需话语
  *任务运行中到达*。`InterruptSource` 是新非阻塞接缝；真·**语音**打断还要流式 ASR + VAD（大件）。
  故：**基线/文本打断可自主**（步间注入收件箱）；**真语音打断延后**（第 7 步，随动态场景 P4 / voicelink 深化）。
- **I —— 问询(D3)在现接缝便宜。** Clarifier = 问→等→答 = 同步 Q&A，正好 `Speaker.say` + `Listener.transcribe`。
  **非对称：ask-human 便宜，barge-in 贵** —— 故先做 `Clarifier`；打断基线先行、真语音延后。
- **J —— 新指标扩 `EvalReport` + `EvalThresholds`**，不止 `IntegrationReport`。引用/定位/搜索/打断/澄清
  各加一对 `ok`/`total` + 阈值。并入第 4 步。
- **L —— 真 LLM 验证(第 5 步)须钉 `temperature=0` + 固定 seed**（贪心解码），否则 Cosmos/Qwen 采样
  使准确率/成功率不可复现（违"可复现"）。并入第 5 步。

**已拍生产门槛**（`meets()` 门；安全硬 1.0）：

| 指标 | 门槛 |
|---|---|
| 安全 / 策略合规 | **1.0**（硬 —— 拦截不可让步） |
| **过敏拦截率** | **1.0**（硬 —— 跟安全同级，不是软质量指标；D-G/D-H） |
| 规划准确率 | ≥ 0.95 |
| 任务成功率 | ≥ 0.90 |
| 引用准确率 | ≥ 0.95 |
| 定位准确率(寻物) | ≥ 0.90 |
| 搜索成功率 | ≥ 0.85 |
| 打断处理准确率 | ≥ 0.95 |
| 澄清精确率 | ≥ 0.90 |
| 清洁覆盖率 | ≥ 0.90 |
| 送餐准确率 | ≥ 0.95 |
| 偏好回调率 | ≥ 0.90 |
| 诚实率 | ≥ 0.95（跟引用准确率同严——过度声称直接违反"不断言未证实事项"底线；D-G） |
| 妥善处理率 | ≥ 0.85（软——目标做不到时体面收场；故意比任务成功率松一档；D-G） |
| p95 时延 | 主机实测后定 |

---

## 7f. 设计决策 —— 基础缺口（第三轮）

基于代码的设计决策，解决第三轮评审指出的 9 个结构性问题。各决策具有约束力；落地顺序（§8）据此更新。

---

### D-A：Phylax 双身份模型

**问题。** `SafetyContext.role`（`phylax.py:79`）只捕获*请求者*身份。机器人作为保洁员或接待员行动时，服务身份独立授权区域访问，与请求者角色正交。

**决策。** 新增字段：

```python
@dataclass(frozen=True, slots=True)
class SafetyContext:
    role: Role = "stranger"           # 请求者身份（不变）
    robot_service: str | None = None  # 新：当前服务角色（"cleaner"/"host"/"guide"/None）
    humans_within_1m: bool = False
    supervised: bool = False
```

`Policy` 新增：

```python
# 区域类型 → 允许进入/讲述的 robot_service 集合
service_permitted_regions: dict[str, frozenset[str]] = field(default_factory=dict)
# 示例：{"private-office": frozenset(), "bathroom": frozenset({"cleaner", "guide"})}
```

Phylax `check()` 新增第三条循环：对 `named_params`（见 D-C）含 `location`/`region` 且该节点有 `region_type` 注解的 subtask，验证 `robot_service in policy.service_permitted_regions[region_type]`。

`adult_only_verbs` 仍基于 `ctx.role`（请求者）。`robot_service=None` 跳过区域访问检查，向后兼容。

---

### D-L：通用不变式 vs 分岗位流程——不是二选一，是组合

**问题。** 接待员过敏检查（§5）既需要跨岗位安全**不变式**（"绝不送出过敏原与客人已知过敏原相交的饮品"），
又需要接待员专属**流程**来把不变式所需数据备齐（"首次服务未知客人前先问过敏"）。岗位专属行为规则该放
哪、通用 Phylax 规则该放哪？两者不是二选一，而是生产者→执行者的组合。

**决策。**
- **通用不变式（Phylax `Policy`）**：跟岗位无关，不按 `robot_service` 分岔——`serve/deliver`
  类动词，若 `饮品过敏原 ∩ 客人已知过敏原 ≠ ∅` 则拦截。任何现有或未来的送餐/送饮岗位都要这条
  同一不变式；它不专属于接待员。
- **分岗位流程（Episteme `SkillCard`，`category="receptionist"`）**：把不变式所需数据备齐的具体
  做法——`preconditions=("guest.allergy_status_known",)`，经现有 SkillCard/`vet_card` 复审机制
  执行（P2 已建成，不新造机制）。未来别的岗位（如"客房送餐"，入住登记时已录过敏）会用不同的流程
  去满足**同一条**通用不变式。
- **组合，不是分类**：SkillCard 前置条件的职责是*生产*数据；Policy 不变式的职责是拿现有数据
  （不论从哪来）去*强制执行*。若 SkillCard 那句问询因任何原因没发生（岗位不对、bug、流程被打断），
  过敏状态仍是未知，Policy 照样拦截——默认 fail-closed，不因"这不是接待员任务"就放行。

这个模式可推广到过敏之外：**往后任何岗位专属行为规则都做成 `SkillCard`（按 `robot_service` 打
`category` 标），绝不硬编码进共享 `Policy` 类**——Policy 永远是通用、跨岗位的不变式层。

---

### D-B：语义 edge 与属性 API（tempomem）

**问题。** `relate()`（`__init__.py:552`）是零参数几何推断调用，只写 `near/on/under` 边。不存在有类型的有向边（`prefers`、`allergic_to`）或标量属性（`dirty`、`fill_level`、`last_cleaned`）的 API。

**决策。** `TempoMem` 新增两组方法，**与几何 `relate()` 正交**：

```python
# 有类型有向边（语义，非几何）
def add_edge(self, src: int, rel: str, dst: int | str, *, ts: float | None = None) -> int:
    """写入有向边 src --rel--> dst。幂等。返回 edge id。"""

def get_edges(self, node: int | str, *, rel: str | None = None) -> list[tuple[NodeHit, str]]:
    """从 node 出发的有向边，可按 rel 过滤。"""

# 节点标量属性包
def set_property(self, node: int | str, key: str, value: object, *, ts: float | None = None) -> None:
    """写入带时间戳的键值属性。覆盖旧值。"""

def get_property(self, node: int | str, key: str) -> object | None:
    """读取属性当前值（未设则 None）。"""
```

`.smem` 新增两张表：`semantic_edges(id, src_id, rel, dst_id, ts)` 和 `node_properties(node_id, key, value_json, ts)`。

`relate()` 和 `related()` **保持不变**——仅几何推断。`add_edge` 覆盖 `prefers`、`allergic_to`、`cleaned_by`；`set_property` 覆盖 `fill_level`、`dirty`、`current_region`。

---

### D-K：菜单/配方知识库——可拓展、经审核

**问题。** 接待员的 `allergy_block` 门（现已升为硬 1.0 门槛，D-G/D-H）得知道饮品成分
（如"latte 含牛奶"）——但 §5 和 D-B 都没定义这个映射哪来。这是**静态世界知识**（每个家都一样），
不是逐场景感知状态，不该塞进 `tempomem` 的场景图。

**决策。** 新增 stdlib-only 模块 `mindloop/menu.py`，照抄 bodylink `load_manifest` 的形状
（内置 dict 兜底 + 外部 YAML 可选，lazy PyYAML —— `bodylink/manifest.py:109-160`）：

```python
def load_menu(name_or_path: str | Path) -> MenuKB: ...   # 内置 dict 或 owner 自供 YAML
class MenuKB:
    def allergens(self, drink: str) -> frozenset[str]: ...
```

**可拓展，不固化**：owner 传自定义 YAML 路径即可扩充/覆盖菜单，不改代码——跟自定义身体 manifest 同机制。

**经审核，复用现成技能卡信任原语，不新造机制**：每条 `MenuKB` 记录带 `provenance: str = "builtin"`，
照抄 `SkillCard.provenance`（`episteme.py:103`）。Phylax 现有对 `Policy.trusted_provenances`
（`phylax.py:100`）的 `vet_card` 式复审同样适用于这里。

**不可信来源只能加保守，不能减保守。** 未过审的配方条目从不当作"确认无过敏原"——Phylax 须把
其过敏原集合当作*未知*处理（fail-closed：拦截或问，按客人已存过敏记录判），不能拿一条没审过的
配方给硬 `allergy_block` 门放行。

---

### D-M：占用房 courtesy check ≠ Clarifier（预算独立）

**问题。** §4 保洁员策略写占用房走"ask-human 门控"、超预算就推迟——字面上是复用 D3 的
`ASK_HUMAN`/Clarifier 及其 ≤2/task 问询预算。但一趟例行保洁行程可能合法碰上 3+ 间占用房；
第 3 间就会耗尽预算，逼出 D3 通则的"如实 ESCALATE-停"——不是保洁族真正想要的"逐房温和推迟"。

**决策。** 占用房检测是 courtesy 在场检测，不是指令歧义澄清——共用 Clarifier 预算是范畴错误。
改用导览的 `wait_for_signal()`（§1.1）：带超时的听信号，不发问、不占问询预算。行程里每间房各调
一次 `wait_for_signal()`，跟其他房间结果无关，跟 D3 问询预算完全独立。

---

### D-N：岗位包驱动的 E2E——配置优先于 case 脚本

**问题。** 规划的 31 个基线场景读起来像每个 E2E case 都要手写脚本。朴素扩张（更多岗位、
更多家庭）下逐 case 手写变成瓶颈——且手写期望会与真正上线的东西漂移。机器人*岗位*的差异
本质是**配置 + 策略 + 技能**，不是代码；测试架构必须镜像这一点。

**决策。** 三部分：

**1. 岗位 = 配置包，且已全是数据**——把 `RoleBundle` 形式化为生产与测试共同加载的单元：

| 包件 | 机制（已有/已规划） |
|---|---|
| 动词集 | D3 manifest（bodylink，可 YAML） |
| 行为流程 | 分岗位 `SkillCard`（D-L，Episteme，经溯源复审） |
| 安全叠加 | `Policy` + `robot_service` 区域规则（D-A/D1） |
| 领域知识 | `MenuKB` 等（D-K，YAML 可拓展） |
| 工作空间 | 区域标注（安装期，§1.2） |

一个 E2E case = **岗位包 × 场景配置 × 轮次列表**——套件加载的就是上线的那个包
（test-what-you-ship；没有会漂移的平行手写期望）。

**2. 三层测试金字塔——手写封顶在黄金集：**
- **L1 不变式（免费，全场景）**：横切断言写进 `ScenarioRunner` 本体——每条口述引节点 id、
  安全 fail-closed、问询预算 ≤2、派发动词 ⊆ manifest、每轮有 trace。永不写逐 case 断言代码。
- **L2 黄金集（手写，约 31 个封顶）**：每族代表路径 + 安全关键精确断言（`allergy_gate`、
  `stove_is_adult_only`）——这里"期望是人审过的"正是价值所在。
- **L3 生成广度（零手写）**：参数化模板（一个 `tidy_table` 模板 × 物体数 × 种子 ⇒ 数十变体，
  断言用*性质*——"每物恰一对 grasp+place"——不用字面动词元组）+ **trace 回放**：步骤 6 的
  trace→数据集整理把真实运行自动结晶成回归 case。

**3. VLA 技能在 E2E 接缝之下。** L3 E2E 验证编排——动词序列、策略、重规划、引用——对
MockBody/sim 跑。VLA 技能（GR00T/OpenVLA 级，L2）把 `grasp` 执行得多好是**独立的 L2 技能
评测**，经同一 D3 动词接缝进入；技能内部逻辑永不漏进 L3 case 脚本。真实端到端成功率来自
步骤 5（真 LLM）与 E2E phase 3（sim 身体），不来自更多脚本。

---

### D-O：RoleBundle——包形态、双钥授权、多岗持有/逐任务激活

**问题。** D-N 形式化了岗位包但留了三个口：怎么打包加载、谁能改岗位、以及对家用机器人
最关键的——一台机器人能否同时持有多个岗位（一台机器人什么都要干，但有些事必须不做）？

**决策。**

**1. 包形态：一个 YAML 清单 + 引用，不复制**——`load_role(name_or_path)`，照
`load_manifest`/`load_menu` 形状（内置 + owner YAML）：

```yaml
role: cleaner
verbs: [navigate, sweep, mop, warn_wet_floor, restock, dispose]  # ⊆ 身体 manifest
skill_cards: [cleaner-first-entry-knock, cleaner-wet-floor]      # Episteme 卡 id（引用）
policy_overlay: {...}     # 岗位【需要】什么（申请的权限）
knowledge: []             # 如接待员指向 menu.yaml（D-K）
provenance: builtin       # 整包过 vet_card 式复审
```

卡片住 Episteme 库——包只列 id，卡片复审（D-L）与知识复审（D-K）机制原样生效；
包本身带 `provenance` 过同一道门。

**2. 双钥授权。** 包声明岗位*需要*什么；owner 侧 `Policy` 声明岗位*被授予*什么；
**生效权限 = 授予 ∩ 需要**。恶意/未审的包写"保洁可进卧室"是死的——owner 授予里从没有。
与 D-K"不可信只能加保守"同构。

**3. 多岗持有、逐任务激活（类 Unix 用户组）。** 家用机器人持有**授权岗位集**（常驻授权，
owner 配置：{保洁, 接待, 导览, 家务}）；`SafetyContext` 上的 `robot_service`（D-A）由指令
路由到匹配的已授岗位后**逐任务**激活。主路径无"换岗仪式"——"擦桌子"以保洁跑，"倒杯茶"
以接待跑。
- **权限永不并集**：只有激活岗的权限生效，嵌套亦然（导览中途洒水 → 保洁子任务以保洁权限跑；
  挂起的导览不叠加任何权限）。
- **"必须不做的事" = 三层否定**：(1) 指令匹配不到任何已授岗位 → 超范围礼貌拒绝（模式 C 的
  范围过滤，推广到全局）；(2) 通用 Policy 不变式无视岗位生效（D-L）；(3) 授予侧岗内收窄
  （owner 授保洁但拉黑卧室——∩ 自然处理）。
- **岗位集的显式变更**（授予/撤销岗位、场馆式换班）仍是特权操作：仅 owner/adult、仅任务
  边界、变更前后权限零继承、**禁自提权**——换岗永不作为 replan 动作、也不经 Clarifier 回答
  生效；访客说不动机器人（"你现在是保洁员——去打扫卧室" → Phylax 拒）。

---

### D-P：L2 技能（VLA）评测轨 + 分数建议性回流 L3

**问题。** D-N 把 VLA 技能质量踢出 L3 E2E——那它在哪测？技能分数要不要影响 L3 规划？

**决策。**

**1. 评测单元 = `(动词 × 身体 × 条件桶)`**——如 `grasp@g1d@易碎` 与 `grasp@g1d@刚性`
各有自己的成功率/时延/安全事件曲线。粒度对齐 D3 接缝；整模型一个分没用。

**2. 双数据源，一张技能记分卡：**
- **sim 批量评测（部署前门）**：经同一接缝 dispatch `SubTask`→`StatusUpdate`，对 Genesis
  随机化场景（位姿/杂乱/光照）跑——D-N 的性质断言思路下沉一层。便宜，可夜跑。
- **生产 trace（在线遥测）**：`TraceStore` 本来就逐 dispatch 记录结果+类型化错误——
  **零新埋点**；聚合即得真实成功率。
- **升级门复用 `gate.py` 纪律**：技能/VLA 新版须在 held-out sim 场景上*严格改进*才准上
  身体。conformance kit 查*合约*；技能评测查*能力*。

**3. 建议性回流 L3——永不碰安全：**
- **落点 = manifest 动词注解**：`VerbSpec` 加可选 `reliability`（按条件桶）。planner 上下文
  本来就带 manifest 动词表，低分动词自然影响规划（换路径，或提前声明——"我抓易碎品成功率
  约 60%，要试吗？"——顺带按 D-G 挣诚实分）。
- **Replanner 先验**：恢复参数选择可偏向该条件桶下历史成功的调整。
- **声明可配置**（owner 经 L5 偏好叠加 / `PreferenceStore` 设置）：阈值 + 话痨度
  （总是 / 低于阈值才说 / 关闭）——有的家庭嫌自贬机器人啰嗦。例外：低置信动作涉及安全
  （热液近人、易碎+重物过顶）时，声明/征得同意走 Phylax 管辖，**不可配置关闭**。
- **两条护栏**：① 分数只偏置规划*偏好*——安全门完全无视分数（高分不跳 Phylax，低分不豁免）；
  ② 防自证回避死环（从不试→无数据→永远低）：探索**只在 sim 做**，绝不拿用户家的真身体试。

**4. 分数住哪**：不进 tempomem（是身体侧运维数据，非场景记忆）——记分卡放 bodylink/skillforge
侧，Brain 初始化时经 manifest 注解带入。

---

### D-Q：L3 模板性质词汇表——生成器即真值，8 个封闭性质

**问题。** D-N 的 L3 层生成场景、没有手写期望——断言必须来自可机械检查的*性质*。
性质词汇表是什么？真值从哪来？

**决策。**

**1. 生成器就是真值源。** 模板生成时*植入*了物体/区域/角色，真值天然已知（钥匙埋在沙发区
⇒ 答案须指沙发区）。断言对比"生成器已知真值 vs 系统行为"——零人工标注。

**2. 初始性质词汇表：8 个，封闭起步（YAGNI——模板要新性质才加）：**

| 性质 | 语义 | 服务 |
|---|---|---|
| `per_object(filter, pattern)` | 每个匹配物体恰好一次动词模式（每物恰一对 grasp+place） | tidy 变体 |
| `ordered(a ≺ b)` | 前置顺序成立（open ≺ place ≺ operate） | 家电链 |
| `terminal(status)` | 任务达终态 SUCCESS/handled | 全部 |
| `bounded(n, K)` | 计数有界（搜索 ≤K 站、重规划 ≤上限） | 寻物/重规划 |
| `cited ⊆ truth` | 引用节点 id ⊆ 生成器植入的真值 id 集 | 导览/问答 |
| `blocked(combo)` | 生成的禁配组合必被拦（孩子×灶，随机变体全测） | 安全 |
| `located == planted` | 报告区域 == 植入区域 | 寻物 |
| `effects_written` | 每个 SUCCESS 子任务的 eff 都写进 WorldState | 全部 |

性质 = 普通函数 `(Scenario, RunArtifacts) -> ok/total`，灌进**同一套 `EvalReport` 指标**——
模板生成的 case 计入同一 `required_metrics` 分母（加固 D-F：分母更难为零）。

**3. 两条纪律：**
- **种子即复现**：模板 + seed 完全确定；report 记 seed，任何失败 `--seed N` 单独重放
  （"可复现"延伸到生成层）。
- **L1 不变式白拿**：生成 case 自动继承全部 L1 检查（引 id / fail-closed / 预算）；
  词汇表只管模板特有断言，不重复。

**落点**：skillforge `templates.py`（落地第 4 步）。

---

### D-C：多参数动词编译器 + 命名参数

**问题。** 编译器（`plan.py:291–303`）将所有 `cmd.args` 解析为平坦节点 id 元组，只用 `cmd.args[0]` 作为 pre/eff 模板替换。`pour(liquid, container)`、`place(target, location)`、`offer(item, person)` 各需命名参数，以便 Phylax 检查正确的参数（如 `location` 用于区域访问，而非 `target`）。

**决策。** `_VERB_TABLE` 条目新增 `params_map: list[str]`——每个位置参数的语义名称。编译器构建 `named_params` 字典并存入 `SubTask`：

```python
# _VERB_TABLE 示例
"pour":    {"params_map": ["liquid", "container"], ...},
"place":   {"params_map": ["target", "location"],  ...},
"offer":   {"params_map": ["item", "recipient"],   ...},
"restock": {"params_map": ["item", "location"],    ...},
```

`SubTask` 新增 `named_params: dict[str, int | str]`（frozen, slots）。

Pre/eff 模板支持所有命名键：`{target}`、`{location}`、`{liquid}`、`{container}`、`{item}`、`{recipient}`。`{target}` 仍为 `params_map[0]` 的默认值，单参数动词向后兼容。

Phylax 读取 `st.named_params.get("location")` 用于 D-A 的服务区域门控。

---

### D-D：宏动词展开——两段编译

**问题。** `deliver`、`sweep(region)`、`clean_region/clean_spot` 混淆了原子/组合边界。宏作为单个 subtask 时，trace 隐藏子步骤，Phylax 检查宏动词而非展开后的步骤。

**决策。** 编译流程改为**两段**：

```
第 0 段——宏展开（新增）：
  deliver(item, target)  → [navigate(target), offer(item, target)]
  sweep(region)          → [navigate(region), vacuum(region)]
  mop(region)            → [warn_wet_floor(region), navigate(region), mop_floor(region), warn_wet_floor(region)]
  clean_region 从 plan 形态中移除；LLM 直接发出 sweep/mop

第 1 段——节点绑定（现有）：
  绑定参数到节点 id，构建带 named_params 的 SubTask

第 2 段——Phylax（现有 + D-A/D-C 扩展）：
  检查展开后的 subtask，而非原始宏
```

展开后的 subtask 携带 `macro_parent: str | None` 用于 trace 嵌套。`deliver` 和 `sweep` 保留在 manifest 作为**面向 planner 的动词**（LLM 发出），但不直接派发到 bodylink。

---

### D-E：中断粒度——仅步间（基线）

**问题。** §1.3 和 §7b 说"随时可被中断"，但 `_drain()`（`brain.py:352`）阻塞到 executor stream terminal，无步内抢占点。

**决策。** 基线中断精度为**步与步之间**（`_drain()` 返回后）。`InterruptSource` 收件箱在下一次 `_drain()` 调用前检查。

真正的步内抢占（导航中途、拖地中途）需要 bodylink cancel/pause/resume 握手——**延后至 P4**。进行中的步骤先完成（≤ `timeout_s`），打断在下一步边界处理。§1.3 和 §7b 文字改为"步间精度"。

---

### D-F：eval 最低分母

**问题。** `_rate(ok, total)` 在 `total=0` 时返回 `1.0`（`eval.py:117`）。未覆盖关键指标的套件会以 1.0 空洞通过。

**决策。** 每个套件配置声明 `required_metrics: frozenset[str]`。运行后如有必需指标 `total==0`，`IntegrationReport.meets()` 返回 `False`，并附 `coverage_gap` 列表。`_rate()` 本身不变。

各套件必需指标：
- `tour_suite`：`citation_accuracy`
- `find_suite`：`localization_accuracy`、`search_success`、`honesty_rate`（由陈旧含糊
  场景练兵——套件从没触发过含糊，不该虚假通过 D-G 的诚实门槛）
- `receptionist_suite`：`serve_accuracy`、`allergy_block`
- `cleaner_suite`：`cleaning_coverage`
- `execution_dynamics` 套件：`interrupt_handling_accuracy`、`clarification_precision`
  （这两个指标**只**为这套件而生——漏列进 `required_metrics` 正是本决策想堵的虚假通过漏洞）

---

### D-G：任务成功分类

**问题。** "如实未找到算成功""缺货如实告知算成功"将任务目标成功与优雅处理混同。ENPIRE 奖励据此会学保守回答而非完成任务。

**决策。** 三类结果独立追踪：

| 类别 | 定义 | 用途 |
|---|---|---|
| `task_success` | 目标达成：物品找到/送达、饮品送达、区域已清洁 | 主成功率指标 |
| `handled_success` | 目标不可达时情况处理正确：如实未找到、安全拦截+推荐替代 | 独立 `handle_rate` 指标 |
| `honesty` | 无虚假/过度声称；陈旧观测含糊表达 | `honesty_rate` 指标 |

ENPIRE 奖励 = `w_task * task_success + w_handle * handled_success + w_honesty * honesty`，默认权重 `0.6 / 0.25 / 0.15`。`meets()` 门控 `task_success ≥ 阈值`。如实未找到基线场景标记为 `handled_success=1, task_success=0`。

---

### D-H：范围计数修正

**精确计数**（见 §7f D-H EN 版完整表格）：
~12 个原子动词、1 个宏动词（deliver）、6 个 Tier-1 记忆接口、+2 张 `.smem` 表、
4 项 Phylax 扩展（含 D-K 菜单溯源复审）、9 个指标、6 套套件、1 个新静态知识模块
（`mindloop/menu.py` `MenuKB`，可拓展+经审核 —— D-K）。

---

### D-J：多物收纳——编译期展开 + 惰性绑定 + 逐步复审

**问题。** "收拾桌子"面对 N 件物品需要 N 对 `grasp→place` 子任务。两个要避的坑：
(1) 批中途场景变化（第 7 件物体挪位）若强迫整批重验，重规划半径过大；
(2) 过度信任规划时准确性——提前把 N 个 id 全绑死，到第 8 步执行时可能已经过期。

**决策。** 三部分，全部复用已有机制，不新造批量层机制：
1. **编译期步骤列表展开**：编译器把"收拾区域 X"展开成 N 对独立 `grasp→place` 子任务
   （编译时该区域内容已固定 ⇒ 确定性，可用 `ScriptedPlanner` + 植入 N 物场景测试）。
2. **逐步惰性绑定**：只在*当前*步即将 dispatch 前才解析该步物体的 id，不提前绑 N 个。
   复用已建成的动态场景幂等派发 + 主动感知尾部重规划（✅ 已完成，dynamic-scene P1-4），
   不新造一套陈旧度模型。
3. **逐步 Phylax 复审**：每步按*那一刻*的场景状态过安全检查，不是开头对整批查一次——
   批中途（第 8 步）场景/占用变化会被抓到，不会因第 1 步已过而被静默放行。

净效果：第 7 件物体的场景变化只触发第 7 步的 P4 有界重规划（RETRY/ADJUST/REROUTE/SKIP/ESCALATE），
第 1-6 步（已做完）和第 8-N 步（还没轮到）不受影响。批量大小不放大重规划半径。

---

## 8. 落地顺序（获批后）

> 实时状态见 [DEV-STATUS.md](DEV-STATUS.md)。标记：✅ 完成 · ◐ 部分 · ▢ 未启动。
>
> **规划已冻结（2026-07-02）。** 17 项 D-决策已饱和。此后新设计问题一律**建时决策**
> （在代码/PR 里定，DEV-STATUS 记一行），仅安全关键项可重开本文档。
> 执行按批次 **T1–T4**（见 DEV-STATUS §2）：T1 = 步骤 1 + 步骤 2 核验 · T2 = 步骤 3
> 后 3b（分开提交）· T3 = 步骤 4a 后 4b → 基线 go/no-go · T4 = 步骤 5 ∥ sim 身体。

0. ✅ **规划** — 本文。
1. ▢ **动词（bodylink + mindloop）** — manifest + `MockBody` + `SimDeviceAdapter` 加
   `present, wipe, pour, dispose`（§1-3）+ `sweep, mop, warn_wet_floor, restock`（§4）+
   `greet, take_order, offer, deliver`（§5）（一致性套件通过）**且** `mindloop/plan.py` 的
   `_VERB_TABLE` 补条目（`pre`/`eff`/`skill`，修正 A）；扩 `place` effect 编码区域（修正 B）。*无 LLM。*
2. ◐ **记忆（tempomem）** *（语义 Tier-1 已落 2026-07-02；**T1 核验任务**：查
   `last_seen`/`last_changed`/`current_occupants` 是否按 D-B/§5c.4 签名齐备且有测试，缺则补）* — 加 `last_seen(name)`（§3）+ Tier-1 场景语义接口（§5c.4）：
   `state`/`set_state`（节点属性包）、`last_changed(region)`、`current_occupants(region)`、
   `add_event`/`query_events`（`.smem` 新增 `events` 表）。区域助手已有。全部 numpy-only，无网络。*无 LLM。*
3. ▢ **安全（mindloop/Phylax）** — 区域访问 + 按人隐私维度 + 灶/利器的**参数级门控** `(verb, param)`（D1）。
   区域访问 key 在**现有** `Role {adult,child,guest,stranger}`（`phylax.py` 已有）—— 不新造信任枚举。*无 LLM。*
3b. ▢ **执行动态（mindloop）** — 可抢占调度步进器 + 恢复游标 + `InterruptSource` + `BargeClassifier`（D2）；
   大脑级 `Clarifier` 接缝（D3），`ReplanAction.ASK_HUMAN` 为其一入口 + 问询预算；可达时把死胡同
   ESCALATE → Clarifier。澄清经 Phylax 复审。*无 LLM。*
   **风险纪律（review 第 2 点）**：本步重构 `Brain._dispatch_plan`——现有 109 个 mindloop
   测试全压其上。**TDD 先行、独立提交、绝不与步骤 3 混批**；每切片后现有套件必须保持全绿。
4a. ◐ **评测台——套件+指标（skillforge）** *（scenario 结构已动；真断言依赖 1+3+3b；
   按 review 第 3 点从 4b 拆出——原步骤已膨胀一倍）* — `Scenario.regions` + `_build_memory`
   调 `define_region`（K）；扩 `EvalReport`/`EvalThresholds` 全部新指标字段（J）+
   `required_metrics`（D-F）；L1 不变式进 `ScenarioRunner` 本体（D-N）；5 套件
   （`tour_suite`、`chores_suite`、`find_suite`、`cleaner_suite`、`receptionist_suite`）+
   一个 `execution_dynamics` 套件（文本打断 / 失败问询 / 问询预算）；按 §7e 门槛基线
   go/no-go。*无 LLM，可自主。*
4b. ▢ **评测台——RoleBundle+模板（skillforge）** — `load_role` 包加载 + 双钥授权（D-O）；
   `templates.py` 参数化生成器 + 8 性质词汇表、记录 seed（D-Q）。在 4a 的 go/no-go 上
   扩生成广度。*无 LLM，可自主。*
5. ▢ **真 LLM 验证** — 在主机 `192.168.31.89`（Cosmos+Qwen）跑新套件，拿真准确率/成功率，**钉 `temperature=0` + 固定 seed**（贪心、可复现 —— L）。**需主人批准（GPU）。**
6. ◐ **数据与训练闭环（skillforge）** *（接受门 `gate.py` 已提前落）* — trace→数据集整理；主机 LLM `PolicyAuthor`；奖励=六标准数值化（含诚实）；
   技能→Episteme 结晶；提升回灌由 `IntegrationReport.meets` 门控。整理+基线可自主，LLM rollout 需主机。见 FLOWS 图 5。
7. ▢ **延后** — 语音讲解导览（VoiceLoop）、跟随访客 + 主动搜索感知（动态场景 P4）。

第 1–4 步可自主落地、无网络。仅第 5 步需主机。
