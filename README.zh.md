> 🌐 [English](README.md) · **中文**

# SpatialRobot

**具身大脑**技术栈的工作区总览 —— 包含一个记忆核心、可选的视觉感知模块以及一个 LLM 大脑，拆分为三个独立发布、独立版本管理的代码仓库，并通过 git submodule 与一个 [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) 统一组织在此处。

> 本仓库**不包含任何自有源码** —— 仅存放 submodule 指针和共享开发配置（uv workspace、lockfile、Python 版本锁定、`CLAUDE.md`、本 README）。每个包在其自有仓库中独立开发；workspace 的作用仅是为它们提供一个统一的依赖解析环境。

```
RGB(-D) ─► spatialmem-perception (eyes) ─► Detections
                                              │
                                              ▼
                              spatialmem (memory: fuse → persist → query)
                                              │ serialize
                                              ▼
              spatialmem-brain  Brain.ask ─► Reasoner (LLM) ─► Answer(text, cited node ids)
```

| Submodule | 包名 | 职责 | 仓库 |
|---|---|---|---|
| `SpatialMem/` | `spatialmem` | 记忆核心 —— `.smem` SQLite 场景图、融合、查询（仅依赖 numpy）。 | [wikieden/spatialmem](https://github.com/wikieden/spatialmem) |
| `spatialmem-perception/` | `spatialmem-perception` | 视觉感知 —— RGB(-D) → 世界坐标系 `Detection`（CLIP 位于 `[clip]` extra 之后）。 | [wikieden/spatialmem-perception](https://github.com/wikieden/spatialmem-perception) |
| `spatialmem-brain/` | `spatialmem-brain` | 大脑 —— `Brain` 认知循环 + `Reasoner` + `CosmosReasonVerbalizer`。 | [wikieden/spatialmem-brain](https://github.com/wikieden/spatialmem-brain) |

依赖方向：`perception → core`，`brain → core`（以及可选的 `brain[perception]`）。核心层永远不导入其他两个模块。

## 克隆

```bash
git clone --recurse-submodules https://github.com/wikieden/SpatialRobot.git
cd SpatialRobot
# 如果忘记了 --recurse-submodules：
git submodule update --init --recursive
```

## 环境配置

从本仓库根目录为全部三个包共用一个环境（Python 版本通过 `.python-version` 锁定为 3.12）：

```bash
uv sync                 # 在根目录创建 .venv，以可编辑模式安装全部 3 个成员包及共享开发工具
uv sync --extra clip    # 额外安装 GPU/CLIP 技术栈（torch、open-clip、pillow）
```

`[tool.uv.sources]` 将 `spatialmem` / `spatialmem-perception` 映射到本地目录树 —— 修改核心代码后，brain/perception 立即可见，无需重新安装。

## 常用命令

`Makefile` 封装了常用的 `uv run` 调用：

```bash
make sync            # uv sync
make test            # 对全部 3 个成员包执行 pytest
make test-core       # 单个成员包（还有：test-brain、test-perception）
make lint            # ruff check .
make fmt             # ruff format .
make types           # 对全部 3 个 src 目录执行 pyright
make bump            # 将每个 submodule 拉取到其跟踪分支的最新提交
```

也可以直接运行任意命令，例如 `uv run pytest SpatialMem/tests` 或 `uv run spatialmem viz store.smem -o scene.html`。

## 日常 submodule 工作流

1. 在成员目录内工作（`SpatialMem/`、……）—— 在子仓库中提交并推送。
2. 回到根目录，记录新的指针：
   ```bash
   git submodule update --remote   # 或直接执行 `make bump`
   git add <member> && git commit -m "chore: bump <member> → <sha>"
   git push
   ```

跟踪分支：`SpatialMem` → `feat/cosmos-integration`，其余两个 → `main`。

## 更多资料

- 面向 agent / 贡献者的工作区指南：[CLAUDE.md](CLAUDE.md)
- 各包文档：每个 submodule 自身的 `README.md` + `docs/` 目录。
