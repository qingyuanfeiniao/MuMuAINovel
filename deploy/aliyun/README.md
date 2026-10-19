# 阿里云独立部署

本目录对应小服务器的 SQLite 部署方案。应用使用独立的 Compose 项目 `ai-novel-production`，不操作其他项目。

## 部署布局

```text
/opt/ai-novel/
├── releases/<版本>/        # 源码、前端构建结果、模型、镜像构建文件
├── current -> releases/…   # 当前版本
├── shared/.env            # 生产配置，仅服务器本机保存
├── shared/.instance_id
├── shared/data/            # SQLite 与 Chroma 长期记忆
├── shared/storage/         # 上传文件、封面
├── shared/logs/
└── backups/
```

- 独立使用宿主机 8000 端口，不占用现有网站的 80、8080 或 MySQL 端口。
- 单应用进程，CPU 上限 0.5 核、内存上限 512 MiB、进程数上限 96。
- SQLite、长期记忆与上传文件通过宿主机目录持久化，容器重建保留数据。
- 使用独立管理员密码和会话签名密钥。生产账号信息保存在本地忽略文件 `logs/aliyun-access.txt`，不提交到 Git。
- 当前使用 IP + HTTP。会话 Cookie 按 HTTP 环境配置；以后接入 HTTPS 时再启用 Secure。

## 模型和运行环境

原始模型与本地默认行为保留。服务器启用 `ONNX_EMBEDDING_LOW_MEMORY=true`：

1. 在开发机执行 `prepare_embedding.py`，生成按词条量化的词向量、INT8 矩阵权重和预处理 ORT 文件。
2. 从原来的词表、分数与规范化规则生成 SentencePiece 文件，减少分词器内存。
3. 设置 `ONNX_EMBEDDING_MODEL_FILE=model.ort`、`ONNX_EMBEDDING_TOKENIZER=sentencepiece`，限制模型使用一个线程。

转换工具额外需要 `onnx`、`sentencepiece` 和 `protobuf`；生产运行不需要安装转换工具。原模型对比及分词一致性验证记录见 `model-validation.json` 和 `validate_embedding.py`。

前端在开发机执行 `npm run build`，避免服务器运行前端编译。部署构建上下文包含 `backend/`（含构建后的 `static/`，不含本机环境及数据）、`embedding/`、`LICENSE` 和本目录的 Dockerfile、依赖清单与 compose.yaml。

镜像运行 Python 3.13。`requirements.lock` 固定基础依赖，`low-memory-requirements.txt` 增加低内存分词器，并将 SQLAlchemy 调整为兼容 Python 3.13 的 2.0.36。本地 Python 3.12 的依赖保持原样。

本次构建复用服务器已有镜像的 Python 基础环境，在新镜像中建立独立虚拟环境，不改变基础镜像或原项目容器。后续也可以通过 `PYTHON_IMAGE` 构建参数指定独立 Python 镜像。

## 运维

在服务器 `/opt/ai-novel/current` 中执行：

```bash
docker compose ps
docker compose logs --tail=100 novel
docker compose up -d --no-deps novel
```

发布前先停止本项目并备份 `shared` 数据，确保 SQLite 与向量索引属于同一时刻。备份文件包含敏感配置，需要设置为仅管理员可读。

更新时创建新的版本目录与镜像，再切换 `current`；不要覆盖 `shared` 中的环境文件或数据库。应用启动会运行尚未执行的 SQLite 迁移，不清空已有小说。遇到启动问题，只停止或回退本项目，不执行 Docker 全局清理或重启 Docker 服务。
