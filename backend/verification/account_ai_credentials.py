"""Run: .venv/bin/python -m unittest discover -s verification -p account_ai_credentials.py -v"""
import json
import stat
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.config import settings as config
from app.models.settings import Settings
from app.models.user import User
from app.api import admin, settings as settings_api
from app.services.ai_service import AIService
from app.services.user_ai_credentials import decrypt_key, encrypt_key, migrate_legacy_credentials
from app.services import user_ai_credentials as credentials

KEY_A = 'unit-test-alice-secret-1234'
KEY_B = 'unit-test-bob-secret-5678'
GLOBAL_KEY = 'unit-test-global-must-never-fallback'
TRUSTED_URL = 'https://trusted.example/v1'


class AccountCredentialTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved_config = {key: getattr(config, key) for key in (
            'ai_credential_encryption_key', 'default_ai_provider', 'openai_api_key', 'openai_base_url',
            'LOCAL_AUTH_USERNAME', 'gemini_api_key', 'anthropic_api_key', 'xiaomi_mimo_api_key')}
        config.ai_credential_encryption_key = Fernet.generate_key().decode()
        config.default_ai_provider = 'openai'
        config.openai_api_key = GLOBAL_KEY
        config.openai_base_url = TRUSTED_URL
        config.LOCAL_AUTH_USERNAME = 'admin'
        config.gemini_api_key = config.anthropic_api_key = config.xiaomi_mimo_api_key = None
        self.engine = create_async_engine(f'sqlite+aiosqlite:///{self.tmp.name}/test.db')
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        async with self.sessions() as db:
            db.add_all([User(user_id=name, username=name, display_name=name, linuxdo_id=name, is_admin=name == 'admin') for name in ['admin', 'alice', 'bob']])
            await db.commit()
        self.app = FastAPI()

        async def database():
            async with self.sessions() as db:
                yield db

        @self.app.middleware('http')
        async def test_identity(request: Request, call_next):
            async with self.sessions() as db:
                request.state.user = await db.get(User, request.headers.get('x-test-user', ''))
            return await call_next(request)

        self.app.dependency_overrides[get_db] = database
        self.app.include_router(admin.router, prefix='/api')
        self.app.include_router(settings_api.router, prefix='/api')
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url='http://test')

    async def asyncTearDown(self):
        await self.client.aclose()
        await self.engine.dispose()
        for key, value in self.saved_config.items():
            setattr(config, key, value)
        self.tmp.cleanup()

    async def request(self, method, path, user='alice', **kwargs):
        return await self.client.request(method, '/api' + path, headers={'x-test-user': user}, **kwargs)

    async def bind(self, user='alice', key=KEY_A):
        result = await self.request('PUT', f'/admin/users/{user}/ai-key', user='admin', json={'api_key': key})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertNotIn(key, result.text)
        return result

    async def test_generated_master_key_is_persistent_private_and_fails_closed(self):
        config.ai_credential_encryption_key = None
        with patch.object(credentials, 'DATA_DIR', Path(self.tmp.name)):
            encrypted = encrypt_key(KEY_A)
            path = Path(self.tmp.name) / '.ai_credentials.key'
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(decrypt_key(encrypted), KEY_A)
            initial = path.read_bytes()
            self.assertEqual(decrypt_key(encrypt_key(KEY_B)), KEY_B)
            self.assertEqual(path.read_bytes(), initial)
            with self.assertRaises(HTTPException):
                decrypt_key(KEY_A)
            config.ai_credential_encryption_key = Fernet.generate_key().decode()
            with self.assertRaises(HTTPException):
                decrypt_key(encrypted)

    async def test_admin_only_encryption_masking_and_account_isolation(self):
        for user, status in [('alice', 403), ('', 401)]:
            result = await self.request('PUT', '/admin/users/alice/ai-key', user=user, json={'api_key': KEY_A})
            self.assertEqual(result.status_code, status)
        await self.bind()
        await self.bind('bob', KEY_B)
        async with self.sessions() as db:
            values = (await db.execute(text('SELECT user_id, api_key FROM settings'))).all()
            for user, ciphertext in values:
                expected = KEY_A if user == 'alice' else KEY_B
                self.assertTrue(ciphertext.startswith('fernet:'))
                self.assertNotIn(expected, ciphertext)
                self.assertEqual(decrypt_key(ciphertext), expected)
        alice = await self.request('GET', '/settings')
        bob = await self.request('GET', '/settings', user='bob')
        self.assertEqual(alice.json()['api_key'], '')
        self.assertEqual(alice.json()['ai_key_masked'], '••••1234')
        self.assertEqual(bob.json()['ai_key_masked'], '••••5678')
        self.assertNotIn(KEY_A, alice.text + bob.text)
        self.assertNotIn(KEY_B, alice.text + bob.text)

    async def test_unbound_and_unauthenticated_have_no_global_fallback(self):
        result = await self.request('GET', '/settings')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['ai_key_status'], 'unbound')
        self.assertEqual(result.json()['api_key'], '')
        payload = {'provider': 'openai', 'api_key': KEY_B, 'api_base_url': 'https://attacker.example', 'llm_model': 'test'}
        for route in ['/settings/test', '/settings/check-function-calling']:
            result = await self.request('POST', route, json=payload)
            self.assertEqual(result.status_code, 409, result.text)
            result = await self.request('POST', route, user='', json=payload)
            self.assertEqual(result.status_code, 401, result.text)
        self.assertEqual((await self.request('GET', '/settings/models')).status_code, 409)
        with self.assertRaises(HTTPException) as raised:
            AIService()
        self.assertEqual(raised.exception.status_code, 409)

    async def test_generic_settings_cannot_replace_binding_and_reset_preserves_it(self):
        await self.bind()
        result = await self.request('PUT', '/settings', json={'api_key': KEY_B})
        self.assertEqual(result.status_code, 403)
        result = await self.request('PUT', '/settings', json={'api_base_url': 'https://attacker.example', 'api_provider': 'gemini', 'temperature': 0.5})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['api_base_url'], TRUSTED_URL)
        self.assertEqual(result.json()['api_provider'], 'openai')
        self.assertEqual((await self.request('DELETE', '/settings')).status_code, 200)
        self.assertEqual((await self.request('GET', '/settings')).json()['ai_key_status'], 'bound')
        # Reading settings does not require decrypting a key; ordinary editing survives a lost cipher configuration.
        config.ai_credential_encryption_key = Fernet.generate_key().decode()
        self.assertEqual((await self.request('GET', '/settings')).status_code, 200)

    async def test_tests_models_and_background_ignore_client_key_and_endpoint(self):
        await self.bind()
        await self.bind('bob', KEY_B)
        captured = []
        class FakeService:
            def __init__(self, **values):
                captured.append(values)
            async def generate_text(self, **kwargs):
                return {'content': '测试成功'}
        payload = {'provider': 'gemini', 'api_key': KEY_B, 'api_base_url': 'https://attacker.example', 'llm_model': 'test'}
        with patch.object(settings_api, 'AIService', FakeService):
            result = await self.request('POST', '/settings/test', json=payload)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertTrue(result.json()['success'], result.text)
        self.assertEqual(captured[-1]['api_key'], KEY_A)
        self.assertEqual(captured[-1]['api_base_url'], TRUSTED_URL)
        with patch.object(settings_api, 'create_user_ai_service_with_mcp', side_effect=lambda **values: values):
            async with self.sessions() as db:
                alice = await settings_api.get_user_ai_service_from_db('alice', db)
                bob = await settings_api.get_user_ai_service_from_db('bob', db)
        self.assertEqual(alice['api_key'], KEY_A)
        self.assertEqual(bob['api_key'], KEY_B)
        response = httpx.Response(200, json={'data': [{'id': 'test-model'}]}, request=httpx.Request('GET', TRUSTED_URL + '/models'))
        fake_client = AsyncMock()
        fake_client.__aenter__.return_value = fake_client
        fake_client.get.return_value = response
        with patch.object(settings_api, 'validate_ai_http_url', side_effect=lambda value: value), patch.object(settings_api.httpx, 'AsyncClient', return_value=fake_client):
            result = await self.request('GET', '/settings/models', params={'api_key': KEY_B, 'api_base_url': 'https://attacker.example'})
        self.assertEqual(result.status_code, 200, result.text)
        args, kwargs = fake_client.get.call_args
        self.assertEqual(args[0], TRUSTED_URL + '/models')
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer ' + KEY_A)

    async def test_disable_and_rotate_stop_reused_batch_service(self):
        await self.bind()
        await self.bind('bob', KEY_B)
        async with self.sessions() as db:
            service = await settings_api.get_user_ai_service_from_db('alice', db)
            generate = AsyncMock(return_value={'content': 'chapter'})
            service._openai_provider.generate = generate
            await service.generate_text('chapter one', auto_mcp=False)
            result = await self.request('PUT', '/admin/users/alice/ai-key/status', user='admin', json={'enabled': False})
            self.assertEqual(result.json()['ai_key_status'], 'disabled')
            with self.assertRaises(HTTPException):
                await service.generate_text('chapter two', auto_mcp=False)
            with self.assertRaises(HTTPException):
                await anext(service.generate_text_stream('chapter two', auto_mcp=False))
            generate.assert_awaited_once()
            self.assertEqual((await self.request('GET', '/settings', user='bob')).json()['ai_key_status'], 'bound')
            await self.request('PUT', '/admin/users/alice/ai-key/status', user='admin', json={'enabled': True})
            await self.bind('alice', 'unit-test-new-secret-9999')
            with self.assertRaises(HTTPException):
                await service.generate_text('chapter three', auto_mcp=False)

    async def test_presets_cannot_store_or_override_keys(self):
        await self.bind()
        payload = {'name': 'analysis', 'config': {'api_provider': 'gemini', 'api_key': KEY_B, 'api_base_url': 'https://attacker.example', 'llm_model': 'analysis-model'}}
        result = await self.request('POST', '/settings/presets', json=payload)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertNotIn(KEY_B, result.text)
        preset_id = result.json()['id']
        self.assertEqual((await self.request('POST', f'/settings/presets/{preset_id}/activate')).status_code, 200)
        async with self.sessions() as db:
            row = (await db.execute(select(Settings).where(Settings.user_id == 'alice'))).scalar_one()
            self.assertNotIn(KEY_B, row.preferences)
            prefs = json.loads(row.preferences)
            prefs['chapter_analysis_preset_id'] = preset_id
            row.preferences = json.dumps(prefs)
            await db.commit()
            with patch.object(settings_api, 'create_user_ai_service_with_mcp', side_effect=lambda **values: values):
                runtime = await settings_api.get_user_ai_service_from_db_by_usage('alice', db, usage='chapter_analysis')
            self.assertEqual(runtime['api_key'], KEY_A)
            self.assertEqual(runtime['api_base_url'], TRUSTED_URL)
            self.assertEqual(runtime['model_name'], 'analysis-model')

    async def test_candidate_key_test_does_not_persist_or_echo_errors(self):
        await self.bind()
        candidate = 'unit-test-candidate-secret-2222'
        with patch('app.services.ai_service.AIService.generate_text', new=AsyncMock(side_effect=RuntimeError(candidate))):
            result = await self.request('POST', '/admin/users/alice/ai-key/test', user='admin', json={'api_key': candidate})
        self.assertEqual(result.status_code, 502)
        self.assertNotIn(candidate, result.text)
        async with self.sessions() as db:
            row = (await db.execute(select(Settings).where(Settings.user_id == 'alice'))).scalar_one()
            self.assertEqual(row.api_key, KEY_A)
        with patch.object(settings_api, 'AIService') as service:
            service.return_value.generate_text = AsyncMock(side_effect=RuntimeError(KEY_A))
            result = await self.request('POST', '/settings/test', json={'provider': 'openai', 'api_key': '', 'api_base_url': TRUSTED_URL, 'llm_model': 'test'})
        self.assertNotIn(KEY_A, result.text)

    async def test_create_user_optional_binding_and_delete_cleanup(self):
        # Managers use the same isolated database as the API dependency.
        with patch.object(admin.user_manager, '_get_session', new=AsyncMock(side_effect=lambda: self.sessions())), patch.object(admin.password_manager, '_get_session', new=AsyncMock(side_effect=lambda: self.sessions())):
            for username, token in [('with_key', KEY_A), ('without_key', '')]:
                result = await self.request('POST', '/admin/users', user='admin', json={'username': username, 'display_name': username, 'password': 'test-password', 'api_key': token, 'is_admin': username == 'with_key'})
                self.assertEqual(result.status_code, 200, result.text)
                self.assertNotIn(KEY_A, result.text)
                user_id = result.json()['user']['user_id']
                state = await self.request('GET', '/settings', user=user_id)
                self.assertEqual(state.json()['ai_key_status'], 'bound' if token else 'unbound')
                if token:
                    self.assertTrue(result.json()['user']['is_admin'])
                    bound_user = user_id
            listed = await self.request('GET', '/admin/users', user='admin')
            self.assertNotIn(KEY_A, listed.text)
            self.assertEqual(listed.status_code, 200)
            self.assertEqual((await self.request('DELETE', '/admin/users/' + bound_user, user='admin')).status_code, 200)
            async with self.sessions() as db:
                self.assertIsNone((await db.execute(select(Settings).where(Settings.user_id == bound_user))).scalar_one_or_none())

    async def test_legacy_migration_keeps_private_keys_and_removes_shared_keys(self):
        engine = create_engine(f'sqlite:///{self.tmp.name}/legacy.db')
        with engine.begin() as conn:
            conn.execute(text('CREATE TABLE users(user_id TEXT PRIMARY KEY, username TEXT, is_admin BOOLEAN)'))
            conn.execute(text('CREATE TABLE settings(id TEXT, user_id TEXT, api_key TEXT, preferences TEXT, ai_key_enabled BOOLEAN, ai_key_last4 TEXT, ai_key_updated_at DATETIME, api_provider TEXT, api_base_url TEXT, llm_model TEXT, temperature REAL, max_tokens INTEGER)'))
            for name, token in [('admin', GLOBAL_KEY), ('alice', GLOBAL_KEY), ('bob', KEY_B)]:
                conn.execute(text('INSERT INTO users VALUES(:id,:id,:admin)'), {'id': name, 'admin': name == 'admin'})
                conn.execute(text('INSERT INTO settings(id,user_id,api_key,preferences) VALUES(:id,:id,:key,:prefs)'), {'id': name, 'key': token, 'prefs': json.dumps({'api_presets': {'presets': [{'config': {'api_key': token}}]}})})
            conn.execute(text("INSERT INTO users VALUES('fresh_admin','admin',true)"))
            migrate_legacy_credentials(conn)
            rows = {r['user_id']: r for r in conn.execute(text('SELECT * FROM settings')).mappings()}
            self.assertEqual(decrypt_key(rows['admin']['api_key']), GLOBAL_KEY)
            self.assertEqual(decrypt_key(rows['fresh_admin']['api_key']), GLOBAL_KEY)
            self.assertFalse(rows['alice']['ai_key_enabled'])
            self.assertIsNone(rows['alice']['api_key'])
            self.assertEqual(decrypt_key(rows['bob']['api_key']), KEY_B)
            for row in rows.values():
                self.assertNotIn(GLOBAL_KEY, row['preferences'])
                self.assertNotIn(KEY_B, row['preferences'])
        engine.dispose()


if __name__ == '__main__':
    unittest.main()
