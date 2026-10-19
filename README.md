# MuMuAINovel 📚✨

<div align="center">

<img src="frontend/public/logo.svg" alt="MuMuAINovel logo" width="120" />

![Version](https://img.shields.io/badge/version-1.5.7-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![React](https://img.shields.io/badge/react-18.3.1-blue.svg)
![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)

**基于 AI 的智能小说创作助手**

[特性](#-特性) • [快速开始](#-快速开始) • [配置说明](#%EF%B8%8F-配置说明) • [项目结构](#-项目结构)

</div>

---

<div align="center">

## 💬 加入交流群

欢迎扫码加入 QQ 交流群，一起交流 AI 小说创作心得、反馈问题、获取最新动态！

<img src="frontend/public/qq.jpg" alt="QQ交流群二维码" width="300" />

</div>

---

<div align="center">

## 💖 支持项目

如果这个项目对你有帮助，欢迎通过以下方式支持开发：

**[☕ 请我喝杯咖啡](https://mumuverse.space:1588/)**

**[🌐 MuMuのAPI站点](https://zhongzhuan.mumuverse.space/register?aff=gt7d)**

> 在 MuMu の API 站点充值满 50 元及以上，也可以获得下方赞助专属权益。

### 🎁 赞助专属权益

| 权益 | 说明 |
|------|------|
| 📋 **优先需求响应** | 您的功能需求和问题反馈将获得优先处理 |
| 🚀 **Windows一键启动** | 获取免安装 EXE 程序，双击即可使用 |
| 💬 **专属技术支持** | 加入赞助者内部群，获得远程协助和配置指导 |

您的支持是我持续开发的动力！🙏

</div>

---

## 🤝 赞助商

> [希望合作或赞助本项目？](https://qm.qq.com/q/B5N2BgEmbu)

<table>
<tr>
<td width="200" align="center" valign="middle"><a href="https://www.aiyoyoo.com/register?aff=4AXY9WGE2C5Q"><img src="images/CrazyToken.png" alt="CrazyToken" width="180"></a></td>
<td valign="middle">感谢 <strong>CrazyToken</strong> 赞助支持本项目！CrazyToken 提供 Claude、GPT、Gemini、Kimi、GLM、DeepSeek、Qwen、Grok 等全系主流模型，覆盖大纲构思、正文续写、爽点打磨、润色改稿，针对不同环节选择最合适的模型。全模型低至官方价格的 5%（<code>0.05×</code>），Token 级账单透明可查；官方原生通道，不掺水、不混模、不压缩长上下文，保持模型原生输出体验；稳定高速、高并发不限流，支持多书创作和章节批量生成。新用户通过 <a href="https://www.aiyoyoo.com/register?aff=4AXY9WGE2C5Q">专属链接</a> 注册即送 <code>$20</code> 体验额度，充值额外加赠，并提供独家 1 对 1 远程配置服务，全程真人协助，开箱即用。</td>
</tr>
</table>

<br>

---

## ✨ 特性

- 🤖 **多 AI 模型** - 支持 OpenAI、Gemini、Claude 等主流模型
- 📝 **智能向导** - AI 自动生成大纲、角色和世界观
- 👥 **角色管理** - 人物关系、组织架构可视化管理
- 📖 **章节编辑** - 支持创建、编辑、重新生成和润色
- 🌐 **世界观设定** - 构建完整的故事背景
- 🔐 **多种登录** - LinuxDO OAuth 或本地账户登录
- 💾 **SQLite** - 本 fork 默认使用文件数据库，适合个人与小规模部署
- 🐳 **Docker 部署** - 一键启动，开箱即用

## 📸 项目预览

<details>

<summary>多图预警</summary>

<div align="center">

### 登录界面
![登录界面](images/1.png)

![登录界面](images/1-1.png)

### 主界面
![主界面](images/2.png)

![主界面（暗色）](images/2-1.png)

### 项目管理
![项目管理](images/3.png)

![项目管理](images/3-1.png)

### 赞助我 💖
![赞助我](images/4.png)

![赞助我](images/4-1.png)

</div>

</details>

## 📋 TODO List

### ✅ 已完成功能

- [x] **灵感模式** - 创作灵感和点子生成
- [x] **自定义写作风格** - 支持自定义 AI 写作风格
- [x] **数据导入导出** - 项目数据的导入导出
- [x] **Prompt 调整界面** - 可视化编辑 Prompt 模板
- [x] **章节字数限制** - 用户可设置生成字数
- [x] **思维链与章节关系图谱** - 可视化章节逻辑关系
- [x] **根据分析一键重写** - 根据分析建议重新生成
- [x] **Linux DO 自动创建账号** - OAuth 登录自动生成账号
- [x] **职业等级体系** - 自定义职业和等级系统，支持修仙境界、魔法等级等多种体系
- [x] **角色/组织卡片导入导出** - 单独导出角色和组织卡片，支持跨项目数据共享
- [x] **伏笔管理** - 智能追踪剧情伏笔，提醒未回收线索，可视化伏笔时间线
- [x] **提示词工坊** - 社区驱动的 Prompt 模板分享平台，一键导入优质提示词
- [x] **拆书功能** - 目前呼声比较高的功能，一键拆书，给当年的ta一个圆满的结局

### 📝 规划中功能

......

> 💡 欢迎提交 Issue 或 Pull Request！

## 💻 硬件配置要求

### 最低配置（个人使用/开发环境）

| 组件 | 要求 |
|------|------|
| **CPU** | 2 核 |
| **内存** | 2 GB RAM |
| **存储** | 10 GB 可用空间 |
| **网络** | 稳定互联网连接（用于调用 AI API） |

### 推荐配置（小型团队/生产环境）

| 组件 | 要求 |
|------|------|
| **CPU** | 4 核 |
| **内存** | 8 GB RAM |
| **存储** | 20 GB SSD |
| **网络** | 稳定互联网连接 |

### 较大规模部署的硬件参考（未经本 fork 压测）

| 组件 | 要求 |
|------|------|
| **CPU** | 8 核 |
| **内存** | 16 GB RAM |
| **存储** | 50 GB+ SSD |
| **网络** | 高带宽连接 |

> **📌 说明**
> - **Embedding 模型**：约 400 MB 磁盘空间，运行时加载到内存
> - **SQLite**：无需独立数据库服务，数据文件保存在持久化目录
> - 本 fork 的 SQLite 单进程方案面向个人与小规模使用，上述硬件参考不代表并发承诺
> - **Docker 部署**：建议预留额外 1-2 GB 内存给容器运行时
> - 本项目主要依赖外部 AI API（OpenAI/Claude/Gemini），不需要本地 GPU

## 🚀 快速开始

本 fork 默认使用 `gpt-6-sol`。模型配置位于项目根目录的 `.env`：

- `OPENAI_BASE_URL`：填写实际服务商的 OpenAI 兼容基础地址，不要附加 `/chat/completions`。
- `OPENAI_API_KEY`：填写该服务商提供的密钥。
- `DEFAULT_MODEL=gpt-6-sol`：接口必须支持这个模型名称。

`.env` 已由 Git 忽略，不要把真实密钥写入 `.env.example`。如果从 `backend/` 运行源码，
可将 `backend/.env` 链接到根目录 `.env`，让本地运行和 Docker 共用同一份配置。
应用中的“设置 → 当前配置”也可修改地址、密钥和模型；保存的用户配置会优先使用。

### Docker Compose 部署（SQLite 单容器）

需要 Docker、Docker Compose 和可用的 AI 服务密钥，无需安装 PostgreSQL。

```bash
git clone https://github.com/qingyuanfeiniao/MuMuAINovel.git
cd MuMuAINovel
cp backend/.env.example .env
# 编辑 .env：填写 OPENAI_BASE_URL、OPENAI_API_KEY 和登录密码。
# 已有 .env 时直接编辑，不要覆盖原配置。
docker compose up -d --build
docker compose logs -f
```

访问 `http://服务器IP:8000`。首次构建会安装依赖、构建前端并下载约 450 MB 的向量模型，需要联网。请使用本仓库构建的镜像，SQLite 启动流程已包含在其中。

容器固定使用 `/app/data/mumu.db`，不受宿主机 `.env` 中本地数据库路径影响；`.env.local` 不会打包或传入容器。启动时自动执行 SQLite 迁移，重建容器后数据保留在宿主机目录。

### 本地开发（SQLite）

本地源码运行可继续共用根目录 `.env`，并在 `backend/.env.local` 中覆盖本机配置：

```bash
DATABASE_URL=sqlite+aiosqlite:///./data/mumu-local.db
APP_HOST=127.0.0.1
SESSION_COOKIE_SECURE=false
```

后端使用 Python 3.12，安装 `backend/requirements.txt`，在 `backend/` 下执行：

```bash
python -m alembic -c alembic-sqlite.ini upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

本地运行还需要准备 ONNX 向量模型，路径见 Dockerfile 中的 `ONNX_EMBEDDING_MODEL_DIR` 及下载校验步骤；本地路径为 `backend/embedding/onnx/paraphrase-multilingual-MiniLM-L12-v2/`。

前端在 `frontend/` 下执行 `npm ci`、`npm run dev`，开发页面默认端口为 5173。`npm run build` 会生成后端使用的静态页面。

## ⚙️ 配置说明

### 必需配置

创建 `.env` 文件：

```bash
# Docker Compose 已固定 SQLite 路径，无需配置数据库密码。

# AI 服务
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-6-sol

# 本地账户登录
LOCAL_AUTH_ENABLED=true
LOCAL_AUTH_USERNAME=admin
LOCAL_AUTH_PASSWORD=your_password
```

### 可选配置

```bash
# LinuxDO OAuth
LINUXDO_CLIENT_ID=your_client_id
LINUXDO_CLIENT_SECRET=your_client_secret
LINUXDO_REDIRECT_URI=http://localhost:8000/api/auth/callback
# LinuxDO 登录专用代理（可选，仅影响 OAuth token 与用户信息请求）
LINUXDO_PROXY_URL=http://127.0.0.1:7890

# 会话 Cookie Secure 标记
# HTTP 部署使用 false；配置 HTTPS 后改为 true
SESSION_COOKIE_SECURE=false

# 本地 / Docker 内网 LLM（默认关闭，保持 SSRF 防护）
# ALLOW_PRIVATE_AI_ENDPOINTS=true
# ALLOWED_AI_HOSTS=host.docker.internal,127.0.0.1
```

> **🔐 Cookie Secure 说明**
>
> - HTTPS 部署：建议保持 `SESSION_COOKIE_SECURE=true`，浏览器只会通过 HTTPS 发送登录 Cookie。
> - HTTP 部署：如果登录后浏览器没有保存 Cookie，请在 `.env` 中设置 `SESSION_COOKIE_SECURE=false`，然后重启后端或 Docker 容器。
> - Docker Compose 默认使用 `SESSION_COOKIE_SECURE=false`；HTTPS 部署请在 `.env` 中设为 `true`。
>
> **🌐 LinuxDO 专用代理说明**
>
> - 如果只有 LinuxDO 授权登录在当前网络不可达，优先配置 `LINUXDO_PROXY_URL`，不要配置全局 `HTTP_PROXY` / `HTTPS_PROXY`。
> - `LINUXDO_PROXY_URL` 只会用于 LinuxDO OAuth 的 token 交换和用户信息请求，不影响 AI 服务、SMTP、数据库等其他网络调用。
> - 常见示例：`LINUXDO_PROXY_URL=http://127.0.0.1:7890`；Docker 容器内访问宿主机代理时通常需要使用宿主机在 Docker 网络中的地址，而不是容器内的 `127.0.0.1`。
> - 当前示例按 HTTP 代理配置；如果需要 SOCKS 代理，请先确保运行环境安装了 httpx 的 SOCKS 支持依赖。
>
> **🖥️ 本地 / Docker 内网 LLM 说明**
>
> - 默认会拒绝 `localhost`、`127.0.0.1`、私网 IP 以及解析到内网的主机名（例如 `host.docker.internal`），用于降低 SSRF 风险。
> - 如果 AI 服务跑在本机 Ollama / llama.cpp，或 Docker 容器需要访问宿主机上的模型，请在 `.env` 中设置 `ALLOW_PRIVATE_AI_ENDPOINTS=true`，或把允许的主机名写入 `ALLOWED_AI_HOSTS`。
> - 即使开启本地放行，链路本地地址（如云厂商元数据 `169.254.169.254`）仍然会被拒绝。
> - MCP 插件 URL 不受该开关影响，继续走严格的公网校验。

### 中转 API 配置

支持所有 OpenAI 兼容格式的中转服务：

```bash
# New API 示例
OPENAI_API_KEY=sk-xxxxxxxx
OPENAI_BASE_URL=https://api.new-api.com/v1

# 其他中转服务
OPENAI_BASE_URL=https://your-proxy-service.com/v1
```

## 🐳 Docker 部署详情

### 服务与数据

只有 `mumuainovel` 一个服务，对外端口为 8000。SQLite 不需要独立数据库容器，也不开放 5432 端口。应用使用单个工作进程，避免重复加载向量模型，并减少 SQLite 写入竞争。

| 宿主机路径 | 容器内路径 | 内容 |
|---|---|---|
| `./data/mumu.db` | `/app/data/mumu.db` | 小说、章节、人物、设置等 SQLite 数据 |
| `./data/chroma_db/` | `/app/data/chroma_db/` | 长期记忆和知识库向量数据 |
| `./storage/knowledge/` | `/app/storage/knowledge/` | 知识库上传文件 |
| `./storage/generated_covers/` | `/app/storage/generated_covers/` | 生成的封面 |
| `./logs/` | `/app/logs/` | 应用日志 |

首次启动自动建表，后续启动只执行尚未应用的迁移；迁移失败会停止启动。镜像不包含本机密钥、数据库、上传文件或虚拟环境。

本地源码运行的数据在 `backend/data/` 等目录，Docker 使用项目根目录的 `data/` 和 `storage/`，两者不会自动同步。已有小说可通过应用的项目导出、导入功能迁移。

### 常用命令

```bash
# 构建并启动；修改配置或更新代码后也执行此命令
docker compose up -d --build
# 查看状态及日志
docker compose ps
docker compose logs -f
# 停止（保留宿主机数据目录）
docker compose down
# 重启
docker compose restart
```

### 备份

先运行 `docker compose stop`，再完整备份 `data/`、`storage/` 和 `.env`，完成后执行 `docker compose start`。SQLite 的 `-wal`、`-shm` 等附属文件如存在，也应保留在目录中；不要只复制运行中的 `mumu.db`。恢复时使用同一批备份文件。

移除 PostgreSQL 可以减少资源占用，但本地向量模型仍会加载到内存；服务器容量还需包含应用和向量检索的开销。

### 端口配置

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8800:8000"  # 宿主机:容器
```

## 📁 项目结构

```
MuMuAINovel/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── middleware/     # 中间件
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # 应用入口
│   ├── scripts/            # 工具脚本
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── services/      # API 服务
│   │   └── store/         # 状态管理
│   └── package.json
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile             # Docker 镜像构建
└── README.md
```

## 🛠️ 技术栈

**后端**: FastAPI • SQLite • SQLAlchemy • OpenAI/Claude/Gemini SDK

**前端**: React 18 • TypeScript • Ant Design • Zustand • Vite

## 📖 使用指南

1. **登录系统** - 使用本地账户或 LinuxDO 账户
2. **创建项目** - 选择"使用向导创建"
3. **AI 生成** - 输入基本信息，AI 自动生成大纲和角色
4. **编辑完善** - 管理角色关系，生成和编辑章节

### API 文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 贡献者

感谢所有为本项目做出贡献的开发者！

<a href="https://github.com/xiamuceer-j/MuMuAINovel/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=xiamuceer-j/MuMuAINovel" />
</a>

## 📝 许可证

本项目采用 [GNU General Public License v3.0](LICENSE)

**GPL v3 意味着：**
- ✅ 可自由使用、修改和分发
- ✅ 可用于商业目的
- 📝 必须开源修改版本
- 📝 必须保留原作者版权
- 📝 衍生作品必须使用 GPL v3 协议

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - Python Web 框架
- [React](https://react.dev/) - 前端框架
- [Ant Design](https://ant.design/) - UI 组件库
- [PostgreSQL](https://www.postgresql.org/) - 数据库

## 📧 联系方式

- 提交 [Issue](https://github.com/xiamuceer-j/MuMuAINovel/issues)
- Linux DO [讨论](https://linux.do/t/topic/1106333)
- 加入QQ群 [QQ群](frontend/public/qq.jpg)
- 加入WX群 [WX群](frontend/public/WX.png)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star！**

Made with ❤️

</div>

## Star History

<a href="https://star-history.dera.page/#xiamuceer-j/MuMuAINovel&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=xiamuceer-j/MuMuAINovel&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=xiamuceer-j/MuMuAINovel&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=xiamuceer-j/MuMuAINovel&type=date&legend=top-left" />
 </picture>
</a>

## History

![Alt](https://repobeats.axiom.co/api/embed/ee7141a5f269c64759302e067abe23b46796bafe.svg "Repobeats analytics image")
