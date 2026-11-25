# Copilot App 实跑手册 · Field Manual

本仓库是课程的**文档网站**，不是课程代码仓库。可运行的四个 Lab 位于独立仓库 [`kinfey/hol_ghc_app`](https://github.com/kinfey/hol_ghc_app)；Lab 1 在 `Lab1/Code/`。

## 分开放置两个仓库

建议在 `Demo-GH` 下创建两个平级目录：

```text
Demo-GH/
├── copilot-app-manual/
└── hol_ghc_app/
```

从 `Demo-GH` 的父目录开始，先创建并进入目标目录，再分别克隆两个仓库：

```bash
mkdir -p Demo-GH
cd Demo-GH
git clone https://github.com/ITD-NextDimension/copilot-app-manual copilot-app-manual
git clone https://github.com/kinfey/hol_ghc_app hol_ghc_app
```

这样会生成上方展示的两个平级目录。以上命令适用于目标子目录尚不存在的情况；不要在已有非空目录中运行 `git clone URL .`。如果目标目录已经有克隆，先运行 `git status --short --branch`，检查未提交改动后再决定是否更新；不要为了重克隆删除或移动已有内容。

如果文档仓库已经克隆在 `Demo-GH` 根目录，就保留原位，将课程仓库克隆到 `Demo-GH/hol_ghc_app/`。为避免父仓库把嵌套仓库当成待提交内容，只在文档仓库的 `.git/info/exclude` 添加 `hol_ghc_app/`；这是本机 Git 忽略规则，不是提交或子模块。

## 在 Copilot App 打开课程代码

从 **Sessions** 旁的 **+** 添加或打开本地文件夹 `hol_ghc_app/`，并确认里面有课程 `README.md` 和 `Lab1`–`Lab4`。App 的 **Project** 是组织项目会话的入口，不会替代 Git 克隆，也不会自动把课程文件放到本机。

新会话默认可能是 **New worktree**；课程要使用当前本地克隆，必须显式改为 **Where to work: Current checkout**，并核对 **Run on: This computer**、**GPT-6 Luna · Medium**；本次准备环境中 **Copilot Fusion 已关闭**。在发送任务前查看当前 **Tool permissions** 选项及其作用：`Always ask` 会逐项等待批准，`Assisted` 可减少部分确认，`Approve all` 允许该会话不经逐项确认运行命令和工具。按可信目录和组织策略选择权限，不要关闭 macOS 或其他系统安全保护。

首次发送后，App 可能显示 **Trust this repository?**。跳过信任会导致 Autopilot 工具调用被拒绝。选择 **Always trust** 前，先确认仓库来源并检查其配置、hooks、扩展等内容；该选项允许仓库配置、hooks、扩展及未来更新执行。仓库信任与 **Tool permissions** 是两个独立控制：前者决定是否信任仓库内容，后者决定 Copilot 使用工具时的批准方式。只信任你已审查并认可的仓库，不要因此关闭系统安全保护。

若多组织许可证账号遇到 **“Billing setup required”** 或主页显示 **usage blocked**，前往 [Copilot features 设置](https://github.com/settings/copilot/features)，在 **Usage billed to** 选择拥有 Copilot 授权的计费实体后重试；本次准备选择的是 **Miruth**。Credits 有余额不等于用户一定有可用预算，不能把所有拦截都归因于余额不足。与本地象棋无关的 MCP 登录提示不会妨碍 Python/HTML 游戏，不需要为本实验授权无关服务。

## 课程环境预检

在课程仓库根目录先检查工具版本。Lab 2 视频制作需要 Node.js 22+、FFmpeg 和 ffprobe；其他 Lab 按各自说明确认依赖。

```bash
python3 --version
copilot --version
node --version
npm --version
ffmpeg -version
ffprobe -version
python3 -m venv .venv
source .venv/bin/activate
python -m pip --version
python -m pip install -r requirements.txt --index-url https://packagefeedproxy.microsoft.io/pypi/simple/
python -m playwright install chromium
```

使用虚拟环境中的 `python -m pip` 安装依赖，避免 macOS/Homebrew 管理的系统 Python 因 PEP 668 拒绝安装；不要用 `--break-system-packages` 绕过保护。Windows PowerShell 请用课程 README 中的 `py -m venv .venv` 和 `.\.venv\Scripts\Activate.ps1` 激活命令。

## 2026-11-25 复跑记录

准备核对确认 `copilot-app-manual` 是文档网站，`hol_ghc_app` 是课程代码仓库；课程目录结构见该仓库。下表是本轮复跑结果，和 2026-10-26、2026-11-12 的旧记录分开。四个 Lab 验收通过；综合离线测试 62 项通过，未重复调用模型。

| 实验 | 2026-11-25 状态 |
|---|---|
| Lab 1 | 修复终局落点提示；20 项规则测试与 Playwright 通过；独立浏览器点击红兵、走一步和悔棋通过。 |
| Lab 2 | 通过：当前源码最终渲染；H.264/AAC、1080×1920、30 fps、3600 帧、120.000 秒；晓晓女声 111.336 秒；HyperFrames 检查、全片解码和音频信号检查通过。成片：Lab2/Code/film/output/surface-ultra-2026-11-25.mp4。 |
| Lab 3 | 真实单一 gpt-6-luna · Medium SDK 会话；财务定向 pytest 2 项通过；最终 Playwright 6 项通过且无页面错误。四张卡片：281724 / 128528 / 45.62% / 101832；Cloud：106265 / 44589 / 41.96%；FY2024 Cloud：87464。 |
| Lab 4 | 三个真实 gpt-6-luna / Autopilot 独立 SDK 会话、虚构资料和固定时钟；浏览器完成状态刷新后持久化；`app.py:8014`；私有路由 404、无令牌 POST 403。原生 hol-weekboard Canvas 加载、完成、重开持久化通过，取消勾选后界面恢复为 0/3。17 项定向测试通过。 |

详细手册保留旧实测材料并附本轮独立状态表；不要将旧失败会话或旧视频结果与本轮混为一谈。

## 在线阅读

| 语言 | 在线阅读 |
|---|---|
| 简体中文 | https://itd-nextdimension.github.io/copilot-app-manual/ |
| 繁體中文 | https://itd-nextdimension.github.io/copilot-app-manual/zh-TW/ |
| English | https://itd-nextdimension.github.io/copilot-app-manual/en/ |

截图中的个人账户信息与系统通知已做马赛克处理。

## 详细版 Lab 手册

逐步点击的详细版学员手册（简中 / 繁中 / English 三语，单文件 `lab-manual/index.html`）：https://itd-nextdimension.github.io/copilot-app-manual/lab-manual/

## 重新生成首页三语页面

三个首页由 `source/build.py` 生成：简体正文来自 `source/zh-CN.artifact.html`，繁体由 OpenCC（`opencc-js`，沿用上游课程的台湾术语表）转换，英文正文是 `source/body-en.html` 的人工翻译。

```bash
cd source
npm i --no-save opencc-js@1.0.5
python3 build.py
```

ITD · Next Dimension

[2026-11-25 最终验收报告](acceptance-2026-11-25.html) · [本轮课程成果分支](https://github.com/tarrywang/hol_ghc_app/tree/codex/labs-acceptance-2026-11-25)
