"""账号 AI 密钥：加密存储、统一服务地址及无公用密钥回退。"""
from datetime import datetime, timezone
import os

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from filelock import FileLock

from app.config import DATA_DIR, settings as app_settings

PREFIX = "fernet:"


def _cipher() -> Fernet:
    configured = app_settings.ai_credential_encryption_key
    if configured:
        key = configured.encode()
    else:
        path = DATA_DIR / ".ai_credentials.key"
        with FileLock(str(path) + ".lock", timeout=10):
            if not path.exists():
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(descriptor, "wb") as output:
                    output.write(Fernet.generate_key())
            key = path.read_bytes().strip()
    try:
        return Fernet(key)
    except (ValueError, TypeError):
        raise HTTPException(503, "AI 密钥加密配置无效，请联系管理员。") from None


def encrypt_key(value: str | None) -> str | None:
    return PREFIX + _cipher().encrypt(value.encode()).decode() if value else None


def decrypt_key(value: str | None) -> str | None:
    if not value:
        return None
    if not value.startswith(PREFIX):
        raise HTTPException(503, "账号 AI 密钥尚未完成安全迁移，请联系管理员。")
    try:
        return _cipher().decrypt(value[len(PREFIX):].encode()).decode()
    except InvalidToken:
        raise HTTPException(503, "无法读取账号 AI 密钥，请检查加密配置。") from None


def connection_defaults() -> dict:
    provider = (app_settings.default_ai_provider or "openai").lower().strip()
    if provider == "gemini":
        url = app_settings.gemini_base_url or "https://generativelanguage.googleapis.com/v1beta"
    elif provider == "anthropic":
        url = app_settings.anthropic_base_url or "https://api.anthropic.com"
    elif provider == "xiaomi_mimo":
        provider = "openai"
        url = app_settings.xiaomi_mimo_base_url
    else:
        provider = "openai"
        url = app_settings.openai_base_url or "https://api.openai.com/v1"
    return {"api_provider": provider, "api_base_url": url}


def resolve_account_runtime(api_key: str | None) -> dict:
    if not api_key:
        raise HTTPException(409, "当前账号尚未绑定可用的 AI 密钥，请联系管理员。")
    return {**connection_defaults(), "api_key": api_key}


def binding_summary(row) -> dict:
    return {
        "ai_key_status": row.ai_key_status if row else "unbound",
        "ai_key_masked": row.ai_key_masked if row else None,
        "ai_key_updated_at": row.ai_key_updated_at.isoformat() if row and row.ai_key_updated_at else None,
    }


def scrub_credentials(value):
    """预设只保存模型参数，不保存或覆盖账号绑定的密钥和服务地址。"""
    if isinstance(value, dict):
        return {key: ("" if key == "api_key" else scrub_credentials(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [scrub_credentials(item) for item in value]
    return value


def managed_settings_update(values: dict) -> dict:
    values = dict(values)
    if values.pop("api_key", None):
        raise HTTPException(403, "AI 密钥由管理员在账号管理中分配。")
    values.update(connection_defaults())
    if "preferences" in values and values["preferences"]:
        import json
        try:
            values["preferences"] = json.dumps(scrub_credentials(json.loads(values["preferences"])), ensure_ascii=False)
        except (ValueError, TypeError):
            raise HTTPException(422, "偏好设置必须是有效的 JSON。") from None
    return values


def migrate_legacy_credentials(connection):
    """旧公共密钥只迁移给初始管理员；独立个人密钥保留，预设不携带密钥。"""
    import json
    import sqlalchemy as sa
    import uuid
    shared = {value for value in [app_settings.openai_api_key, app_settings.gemini_api_key, app_settings.anthropic_api_key, app_settings.xiaomi_mimo_api_key] if value}
    defaults = connection_defaults()
    # 初始管理员可能尚未打开过设置页，此时也需生成绑定记录。
    bootstrap_users = connection.execute(sa.text("SELECT u.user_id FROM users u LEFT JOIN settings s ON s.user_id=u.user_id WHERE u.is_admin=true AND u.username=:username AND s.id IS NULL"), {"username": app_settings.LOCAL_AUTH_USERNAME}).scalars().all()
    for user_id in bootstrap_users:
        connection.execute(sa.text("INSERT INTO settings(id,user_id,api_provider,api_base_url,llm_model,temperature,max_tokens,preferences) VALUES(:id,:user_id,:provider,:url,:model,:temperature,:max_tokens,'{}')"), {
            "id": str(uuid.uuid4()), "user_id": user_id, "provider": defaults["api_provider"], "url": defaults["api_base_url"],
            "model": app_settings.default_model, "temperature": app_settings.default_temperature, "max_tokens": app_settings.default_max_tokens,
        })
    rows = connection.execute(sa.text("SELECT s.id, s.api_key, s.preferences, u.username, u.is_admin FROM settings s LEFT JOIN users u ON u.user_id=s.user_id")).mappings().all()
    for row in rows:
        original = row["api_key"] or ""
        bootstrap = bool(row["is_admin"]) and row["username"] == app_settings.LOCAL_AUTH_USERNAME
        token = original
        if bootstrap and not token:
            token = {"openai": app_settings.openai_api_key, "gemini": app_settings.gemini_api_key, "anthropic": app_settings.anthropic_api_key, "xiaomi_mimo": app_settings.xiaomi_mimo_api_key}.get(app_settings.default_ai_provider)
        if not bootstrap and token in shared:
            token = None
        try:
            preferences = json.dumps(scrub_credentials(json.loads(row["preferences"] or "{}")), ensure_ascii=False)
        except (TypeError, ValueError):
            preferences = "{}"
        connection.execute(sa.text("UPDATE settings SET api_key=:key, ai_key_enabled=:enabled, ai_key_last4=:last4, ai_key_updated_at=:now, preferences=:preferences, api_provider=:provider, api_base_url=:url WHERE id=:id"), {
            "key": encrypt_key(token), "enabled": bool(token), "last4": token[-4:] if token else None,
            "now": datetime.now(timezone.utc), "preferences": preferences, "provider": defaults["api_provider"], "url": defaults["api_base_url"], "id": row["id"],
        })
