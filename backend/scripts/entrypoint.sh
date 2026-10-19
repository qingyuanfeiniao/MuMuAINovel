#!/bin/bash
# SQLite 容器入口：准备持久化目录、执行迁移、启动单进程服务。
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
cd "$APP_DIR"

export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///${APP_DIR}/data/mumu.db}"

echo "================================================"
echo "${APP_NAME:-MuMuAINovel} v${APP_VERSION:-1.5.7} · SQLite"
echo "================================================"

# 只连接本地 SQLite，不再等待 PostgreSQL 或访问 5432 端口。
python - <<'PY'
import os
import sqlite3
from pathlib import Path

from sqlalchemy.engine import make_url

url = make_url(os.environ["DATABASE_URL"])
if url.drivername != "sqlite+aiosqlite":
    raise SystemExit("此容器使用 SQLite；请配置 sqlite+aiosqlite 数据库地址。")
if not url.database or url.database == ":memory:":
    raise SystemExit("SQLite 必须使用持久化数据库文件，不能使用内存数据库。")

database = Path(url.database).expanduser().resolve()
database.parent.mkdir(parents=True, exist_ok=True)
Path("storage").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
with sqlite3.connect(database, timeout=30) as connection:
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=30000")
print("SQLite 数据文件已就绪。")
PY

# 首次启动创建表，再次启动只执行尚未应用的迁移，不清空已有数据。
python -m alembic -c alembic-sqlite.ini upgrade head

# 单进程避免重复加载本地向量模型，也减少 SQLite 的并发写入竞争。
exec python -m uvicorn app.main:app \
    --host "${APP_HOST:-0.0.0.0}" \
    --port "${APP_PORT:-8000}" \
    --workers 1 \
    --log-level info \
    --access-log
