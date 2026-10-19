"""账号独立 AI Key：状态及密文迁移。"""
from alembic import op
import sqlalchemy as sa

revision = "20261019_account_ai_keys"
down_revision = '20260914_knowledge'
branch_labels = None
depends_on = None


def upgrade():
    from app.services.user_ai_credentials import _cipher
    _cipher()  # 先验证/创建加密配置，避免配置错误导致 SQLite 结构半迁移。
    if op.get_bind().dialect.name == "postgresql":
        op.alter_column("settings", "api_key", existing_type=sa.String(500), type_=sa.Text())
    op.add_column("settings", sa.Column("ai_key_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("settings", sa.Column("ai_key_last4", sa.String(4), nullable=True))
    op.add_column("settings", sa.Column("ai_key_updated_at", sa.DateTime(), nullable=True))
    from app.services.user_ai_credentials import migrate_legacy_credentials
    migrate_legacy_credentials(op.get_bind())


def downgrade():
    # 回退不恢复公用或明文密钥，避免重新暴露凭据。
    op.execute("UPDATE settings SET api_key=NULL")
    op.drop_column("settings", "ai_key_updated_at")
    op.drop_column("settings", "ai_key_last4")
    op.drop_column("settings", "ai_key_enabled")
