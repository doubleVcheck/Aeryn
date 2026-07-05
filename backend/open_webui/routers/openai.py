from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import time
from typing import Optional
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

import aiohttp
from aiocache import cached
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    StreamingResponse,
)
from open_webui.config import (
    CACHE_DIR,
)
from open_webui.constants import ERROR_MESSAGES
from open_webui.events import EVENTS, publish_event, publish_model_provider_request_failed
from open_webui.env import (
    AIOHTTP_CLIENT_SESSION_SSL,
    AIOHTTP_CLIENT_TIMEOUT,
    AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST,
    BYPASS_MODEL_ACCESS_CONTROL,
    ENABLE_FORWARD_USER_INFO_HEADERS,
    ENABLE_OPENAI_API_PASSTHROUGH,
    FORWARD_SESSION_INFO_HEADER_CHAT_ID,
    MODELS_CACHE_TTL,
)
from open_webui.internal.db import get_async_session
from open_webui.models.access_grants import AccessGrants
from open_webui.models.config import Config
from open_webui.models.groups import Groups
from open_webui.models.models import Models
from open_webui.models.users import UserModel
from open_webui.utils.access_control import check_model_access, has_connection_access, has_permission
from open_webui.utils.anthropic import get_anthropic_models, is_anthropic_url
from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.headers import get_custom_headers, include_user_info_headers
from open_webui.utils.misc import (
    convert_logit_bias_input_to_json,
    stream_chunks_handler,
)
from open_webui.utils.payload import (
    apply_model_params_to_body_openai,
    apply_system_prompt_to_body,
)
from open_webui.utils.session_pool import (
    cleanup_response,
    get_session,
    stream_wrapper,
)
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


##########################################
#
# Utility functions
# Let the responses returned through this gate be worth
# the question that summoned them.
#
##########################################

# Headers that become stale after aiohttp auto-decompresses the upstream
# response body.  Forwarding them verbatim causes desktop / programmatic
# clients to attempt decompression of an already-decoded payload, resulting
# in ZlibError.  See https://github.com/aio-libs/aiohttp/issues/4462.
_STRIP_PROXY_HEADERS = frozenset({'Content-Encoding', 'Content-Length', 'Transfer-Encoding'})


def _clean_proxy_headers(raw_headers) -> dict:
    """Return a copy of *raw_headers* with stale encoding headers removed."""
    return {k: v for k, v in raw_headers.items() if k not in _STRIP_PROXY_HEADERS}


async def send_get_request(
    request: Request = None,
    url=None,
    key=None,
    user: UserModel = None,
    config=None,
):
    timeout = aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST)
    try:
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            if request and config:
                headers, cookies = await get_headers_and_cookies(request, url, key, config, user=user)
            else:
                headers = {
                    **({'Authorization': f'Bearer {key}'} if key else {}),
                }
                cookies = None

                if ENABLE_FORWARD_USER_INFO_HEADERS and user:
                    headers = include_user_info_headers(headers, user)

            async with session.get(
                url,
                headers=headers,
                cookies=cookies,
                ssl=AIOHTTP_CLIENT_SESSION_SSL,
            ) as response:
                return await response.json()
    except Exception as e:
        # Handle connection error here
        log.error(f'Connection error: {e}')
        return None


class ModelDiscoveryError(Exception):
    pass


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _join_url_path(base_url: str, path: str) -> str:
    base_url = (base_url or '').strip().rstrip('/')
    path = (path or '').strip()
    if not path:
        return base_url
    if path.startswith('http://') or path.startswith('https://'):
        return path.rstrip('/')
    return f'{base_url}/{path.lstrip("/")}'


def _with_query_param(url: str, key: str, value: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query[key] = value
    return urlunparse(parsed._replace(query=urlencode(query)))


def _is_gemini_models_url(url: str, config: dict | None = None) -> bool:
    if _uses_native_gemini_api(url, config):
        return True

    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    return 'generativelanguage.googleapis.com' in hostname or '/v1beta/models' in parsed.path


def _configured_api_format(config: dict | None = None) -> str:
    config = config or {}
    for key in ('api_format', 'api_style', 'protocol', 'provider_api'):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower().replace('-', '_')
    return ''


def _uses_native_anthropic_api(url: str, config: dict | None = None) -> bool:
    api_format = _configured_api_format(config)
    if api_format in {'anthropic', 'claude', 'native_anthropic', 'anthropic_native'}:
        return True
    if api_format in {'openai', 'openai_compatible', 'oai', 'chat_completions'}:
        return False

    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    return 'api.anthropic.com' in hostname


def _uses_native_gemini_api(url: str, config: dict | None = None) -> bool:
    api_format = _configured_api_format(config)
    if api_format in {'gemini', 'google_gemini', 'native_gemini', 'gemini_native'}:
        return True
    if api_format in {'openai', 'openai_compatible', 'oai', 'chat_completions'}:
        return False

    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    path = parsed.path.rstrip('/')
    return 'generativelanguage.googleapis.com' in hostname and '/openai' not in path


def _get_provider_hint(url: str, config: dict | None = None) -> str:
    config = config or {}
    provider = config.get('provider', '')
    if isinstance(provider, str):
        provider = provider.strip().lower()
    else:
        provider = ''

    aliases = {
        'anthropic': 'anthropic',
        'claude': 'anthropic',
        'gemini': 'gemini',
        'google': 'gemini',
        'google-gemini': 'gemini',
        'deepseek': 'deepseek',
        'xai': 'xai',
        'grok': 'xai',
        'zai': 'zai',
        'z.ai': 'zai',
        'zhipu': 'zai',
        'glm': 'zai',
        'bigmodel': 'zai',
        'aliyun': 'ali',
        'ali': 'ali',
        'dashscope': 'ali',
        'openrouter': 'openrouter',
        'groq': 'groq',
        'mistral': 'mistral',
        'perplexity': 'perplexity',
        'together': 'together',
        'fireworks': 'fireworks',
        'nvidia': 'nvidia',
        'cerebras': 'cerebras',
        'sambanova': 'sambanova',
        'openai': 'openai',
    }
    if provider in aliases:
        return aliases[provider]

    hostname = (urlparse(url).hostname or '').lower()
    if 'api.anthropic.com' in hostname:
        return 'anthropic'
    if 'generativelanguage.googleapis.com' in hostname:
        return 'gemini'
    if 'deepseek.com' in hostname:
        return 'deepseek'
    if hostname in {'api.x.ai'} or 'x.ai' in hostname:
        return 'xai'
    if 'bigmodel.cn' in hostname or hostname.endswith('z.ai'):
        return 'zai'
    if 'dashscope.aliyuncs.com' in hostname or 'bailian.aliyuncs.com' in hostname:
        return 'ali'
    if 'openrouter.ai' in hostname:
        return 'openrouter'
    if 'groq.com' in hostname:
        return 'groq'
    if 'mistral.ai' in hostname:
        return 'mistral'
    if 'perplexity.ai' in hostname:
        return 'perplexity'
    if 'together.xyz' in hostname:
        return 'together'
    if 'fireworks.ai' in hostname:
        return 'fireworks'
    if 'nvidia.com' in hostname:
        return 'nvidia'
    if 'cerebras.ai' in hostname:
        return 'cerebras'
    if 'sambanova.ai' in hostname:
        return 'sambanova'
    if 'api.openai.com' in hostname:
        return 'openai'

    return ''


def _provider_display_name(provider: str) -> str:
    provider = (provider or '').strip().lower()
    names = {
        'anthropic': 'Claude',
        'gemini': 'Gemini',
        'deepseek': 'DeepSeek',
        'xai': 'Grok',
        'groq': 'Groq',
        'zai': 'GLM',
        'ali': 'Qwen',
        'openrouter': 'OpenRouter',
        'openai': 'OpenAI',
        'mistral': 'Mistral',
        'together': 'Together',
        'fireworks': 'Fireworks',
        'perplexity': 'Perplexity',
        'nvidia': 'NVIDIA',
        'cerebras': 'Cerebras',
        'sambanova': 'SambaNova',
    }
    return names.get(provider, provider.upper() if provider else '')


def _infer_model_family(model_id: str, provider: str = '') -> str:
    value = (model_id or '').lower()
    provider = (provider or '').lower()

    checks = [
        ('Claude', ('claude', 'anthropic')),
        ('Gemini', ('gemini', 'google')),
        ('Grok', ('grok', 'x-ai', 'xai')),
        ('DeepSeek', ('deepseek',)),
        ('GPT', ('gpt-', 'chatgpt', 'openai/', 'o1', 'o3', 'o4', 'o5')),
        ('Qwen', ('qwen', 'qwq', 'dashscope')),
        ('GLM', ('glm', 'z-ai', 'bigmodel')),
        ('Mistral', ('mistral', 'codestral', 'mixtral')),
        ('Llama', ('llama', 'meta-llama')),
        ('Kimi', ('kimi', 'moonshot')),
        ('Hermes', ('hermes',)),
        ('Command', ('command-', 'cohere')),
        ('Sonar', ('sonar', 'perplexity')),
    ]

    combined = f'{provider}/{value}' if provider else value
    for label, needles in checks:
        if any(needle in combined for needle in needles):
            return label

    return _provider_display_name(provider) or 'External'


def _get_connection_source_label(url: str, config: dict | None = None) -> str:
    config = config or {}
    for key in ('label', 'name', 'connection_label', 'display_name'):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    parsed = urlparse(url or '')
    hostname = parsed.hostname or ''
    provider = _get_provider_hint(url, config)
    provider_label = _provider_display_name(provider)

    if provider_label and (not hostname or provider in hostname.replace('.', '')):
        return provider_label
    return hostname or provider_label or 'External'


def _get_model_discovery_urls(url: str, config: dict | None = None) -> list[str]:
    """Return candidate model-list endpoints for OpenAI-compatible gateways.

    Many routers ask users for a root URL, while OpenAI SDK-style clients ask
    for a versioned base URL. Probe both shapes, plus common provider variants.
    """
    config = config or {}
    base_url = (url or '').strip().rstrip('/')
    if not base_url:
        return []

    configured_urls = []
    for key in ('models_url', 'model_list_url'):
        configured_url = config.get(key)
        if isinstance(configured_url, str) and configured_url.strip():
            configured_urls.append(_join_url_path(base_url, configured_url))

    configured_paths = []
    for key in ('models_path', 'model_list_path'):
        configured_path = config.get(key)
        if isinstance(configured_path, str) and configured_path.strip():
            configured_paths.append(_join_url_path(base_url, configured_path))

    parsed = urlparse(base_url)
    path = parsed.path.rstrip('/')
    provider = _get_provider_hint(base_url, config)

    urls = [*configured_urls, *configured_paths]

    if path.endswith('/models'):
        urls.append(base_url)
    elif _is_gemini_models_url(base_url, config):
        urls.extend(
            [
                _join_url_path(base_url, '/models') if path.endswith('/v1beta') else _join_url_path(base_url, '/v1beta/models'),
                _join_url_path(base_url, '/models'),
                _join_url_path(base_url, '/v1/models'),
            ]
        )
    elif provider == 'openrouter':
        urls.extend(
            [
                _join_url_path(base_url, '/api/v1/models'),
                _join_url_path(base_url, '/models'),
                _join_url_path(base_url, '/v1/models'),
            ]
        )
    elif provider == 'groq':
        urls.extend(
            [
                _join_url_path(base_url, '/openai/v1/models'),
                _join_url_path(base_url, '/models'),
                _join_url_path(base_url, '/v1/models'),
            ]
        )
    elif provider == 'ali':
        urls.extend(
            [
                _join_url_path(base_url, '/compatible-mode/v1/models'),
                _join_url_path(base_url, '/models'),
                _join_url_path(base_url, '/v1/models'),
            ]
        )
    elif provider == 'zai':
        urls.extend(
            [
                _join_url_path(base_url, '/api/paas/v4/models'),
                _join_url_path(base_url, '/models'),
                _join_url_path(base_url, '/v1/models'),
            ]
        )
    elif provider == 'fireworks':
        urls.extend(
            [
                _join_url_path(base_url, '/inference/v1/models'),
                _join_url_path(base_url, '/models'),
                _join_url_path(base_url, '/v1/models'),
            ]
        )
    elif provider == 'perplexity':
        urls.extend(
            [
                _join_url_path(base_url, '/models'),
                _join_url_path(base_url, '/v1/models'),
            ]
        )
    else:
        urls.append(_join_url_path(base_url, '/models'))

        if not _is_openai_versioned_base_path(path):
            urls.extend(
                [
                    _join_url_path(base_url, '/v1/models'),
                    _join_url_path(base_url, '/openai/v1/models'),
                    _join_url_path(base_url, '/compatible-mode/v1/models'),
                    _join_url_path(base_url, '/api/paas/v4/models'),
                    _join_url_path(base_url, '/api/v1/models'),
                    _join_url_path(base_url, '/inference/v1/models'),
                ]
            )

    return _dedupe_preserve_order(urls)


def _is_openai_versioned_base_path(path: str) -> bool:
    return bool(
        re.search(
            r'/(v1|v1beta|openai/v1|v1beta/openai|ml/gateway/v1|v2/ext/openai/v1|compatible-mode/v1|api/paas/v4|api/v1|inference/v1)$',
            path.rstrip('/'),
        )
    )


def _get_openai_endpoint_url(url: str, endpoint: str, config: dict | None = None) -> str:
    """Build the request URL for OpenAI-compatible chat endpoints.

    Open WebUI historically expected users to enter a versioned base URL like
    ``https://host/v1``. Routers often document a root URL instead. Normalize
    root URLs to the conventional ``/v1`` prefix while preserving already
    versioned bases and allowing explicit per-connection overrides.
    """
    config = config or {}
    base_url = (url or '').strip().rstrip('/')
    endpoint = endpoint.strip('/')

    if endpoint == 'responses':
        override_keys = ('responses_url', 'response_url', 'responses_path')
    elif endpoint == 'chat/completions':
        override_keys = ('chat_completions_url', 'chat_completion_url', 'chat_completions_path')
    else:
        override_keys = ()

    for key in override_keys:
        override = config.get(key)
        if isinstance(override, str) and override.strip():
            return _join_url_path(base_url, override)

    parsed = urlparse(base_url)
    path = parsed.path.rstrip('/')
    provider = _get_provider_hint(base_url, config)

    if path.endswith(f'/{endpoint}'):
        return base_url

    if endpoint == 'chat/completions' and path.endswith('/responses'):
        path = path.removesuffix('/responses')
        base_url = urlunparse(parsed._replace(path=path))
    elif endpoint == 'responses' and path.endswith('/chat/completions'):
        path = path.removesuffix('/chat/completions')
        base_url = urlunparse(parsed._replace(path=path))

    if _is_openai_versioned_base_path(path):
        return _join_url_path(base_url, endpoint)

    if provider == 'openrouter':
        return _join_url_path(base_url, f'/api/v1/{endpoint}')
    if provider == 'groq':
        return _join_url_path(base_url, f'/openai/v1/{endpoint}')
    if provider == 'ali':
        if endpoint == 'responses':
            return _join_url_path(base_url, '/api/v2/apps/protocols/compatible-mode/v1/responses')
        return _join_url_path(base_url, f'/compatible-mode/v1/{endpoint}')
    if provider == 'zai':
        return _join_url_path(base_url, f'/api/paas/v4/{endpoint}')
    if provider == 'fireworks':
        return _join_url_path(base_url, f'/inference/v1/{endpoint}')
    if provider == 'perplexity':
        return _join_url_path(base_url, endpoint)

    return _join_url_path(base_url, f'/v1/{endpoint}')


def _get_anthropic_messages_url(url: str) -> str:
    base_url = (url or '').strip().rstrip('/')
    path = urlparse(base_url).path.rstrip('/')
    if path.endswith('/messages'):
        return base_url
    if path.endswith('/v1'):
        return _join_url_path(base_url, '/messages')
    return _join_url_path(base_url, '/v1/messages')


def _get_gemini_generate_url(url: str, model: str) -> str:
    base_url = (url or '').strip().rstrip('/')
    path = urlparse(base_url).path.rstrip('/')
    if ':generateContent' in path or ':streamGenerateContent' in path:
        return base_url
    if path.endswith('/models'):
        return _join_url_path(base_url, f'{quote(model, safe="")}:generateContent')
    if re.search(r'/v\d+(beta)?$', path):
        return _join_url_path(base_url, f'/models/{quote(model, safe="")}:generateContent')
    return _join_url_path(base_url, f'/v1beta/models/{quote(model, safe="")}:generateContent')


def _extract_model_id(model: object) -> str | None:
    if isinstance(model, str):
        return model.strip() or None

    if not isinstance(model, dict):
        return None

    value = model.get('id') or model.get('name') or model.get('model') or model.get('slug')
    if not isinstance(value, str):
        return None

    value = value.strip()
    if value.startswith('models/'):
        value = value.removeprefix('models/')
    return value or None


def _normalize_model_list_response(response_data: object) -> dict | None:
    if isinstance(response_data, list):
        raw_models = response_data
        response = {'object': 'list'}
    elif isinstance(response_data, dict):
        if isinstance(response_data.get('data'), list):
            raw_models = response_data.get('data', [])
        elif isinstance(response_data.get('models'), list):
            raw_models = response_data.get('models', [])
        elif isinstance(response_data.get('model'), list):
            raw_models = response_data.get('model', [])
        else:
            return None
        response = dict(response_data)
    else:
        return None

    models = []
    for model in raw_models:
        model_id = _extract_model_id(model)
        if not model_id:
            continue

        if isinstance(model, dict):
            normalized = dict(model)
            normalized['id'] = model_id
            if normalized.get('name') is None:
                normalized.pop('name', None)
            elif 'name' not in normalized:
                normalized['name'] = model_id
        else:
            normalized = {
                'id': model_id,
                'name': model_id,
                'object': 'model',
            }

        models.append(normalized)

    response['object'] = response.get('object') or 'list'
    response['data'] = models
    return response


async def discover_models_request(
    request: Request = None,
    url=None,
    key=None,
    user: UserModel = None,
    config=None,
    raise_on_error: bool = False,
):
    config = config or {}

    if is_anthropic_url(url):
        result = await get_anthropic_models(url, key, user=user)
        if result is None and raise_on_error:
            raise ModelDiscoveryError('Failed to connect to Anthropic API')
        return result

    candidate_urls = _get_model_discovery_urls(url, config)
    if not candidate_urls:
        if raise_on_error:
            raise ModelDiscoveryError('Model discovery URL is empty')
        return None

    errors = []
    timeout = aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST)

    try:
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            headers, cookies = await get_headers_and_cookies(request, url, key, config, user=user)

            header_variants = [headers]
            if key and _is_gemini_models_url(url, config):
                gemini_headers = {k: v for k, v in headers.items() if k.lower() != 'authorization'}
                gemini_headers['x-goog-api-key'] = key
                header_variants.insert(0, gemini_headers)

            for candidate_url in candidate_urls:
                for candidate_headers in header_variants:
                    page_url = candidate_url
                    merged_response = None

                    for _ in range(100):
                        async with session.get(
                            page_url,
                            headers=candidate_headers,
                            cookies=cookies,
                            ssl=AIOHTTP_CLIENT_SESSION_SSL,
                        ) as response:
                            body = await response.text()

                            if response.status != 200:
                                detail = f'HTTP {response.status}'
                                try:
                                    error_data = json.loads(body)
                                    if isinstance(error_data, dict) and error_data.get('error'):
                                        detail = f'{detail}: {error_data.get("error")}'
                                except Exception:
                                    if body:
                                        detail = f'{detail}: {body[:200]}'
                                errors.append(f'{page_url} -> {detail}')
                                break

                            try:
                                response_data = json.loads(body)
                            except Exception:
                                errors.append(f'{page_url} -> response is not JSON')
                                break

                            normalized = _normalize_model_list_response(response_data)
                            if normalized is None:
                                errors.append(f'{page_url} -> unsupported model-list response shape')
                                break

                            if merged_response is None:
                                merged_response = normalized
                            else:
                                merged_response['data'].extend(normalized.get('data', []))

                            next_page_token = (
                                response_data.get('nextPageToken') if isinstance(response_data, dict) else None
                            )
                            if not next_page_token:
                                return merged_response

                            page_url = _with_query_param(candidate_url, 'pageToken', next_page_token)

                    if merged_response is not None:
                        return merged_response

    except Exception as e:
        errors.append(str(e))

    log.warning('Model discovery failed for %s: %s', url, '; '.join(errors[-5:]))
    if raise_on_error:
        raise ModelDiscoveryError('; '.join(errors[-5:]) or 'Failed to discover models')
    return None


async def get_models_request(
    request: Request = None,
    url=None,
    key=None,
    user: UserModel = None,
    config=None,
):
    return await discover_models_request(request, url, key, user=user, config=config)


def openai_reasoning_model_handler(payload):
    """
    Handle reasoning model specific parameters
    """
    if 'max_tokens' in payload:
        # Convert "max_tokens" to "max_completion_tokens" for all reasoning models
        payload['max_completion_tokens'] = payload['max_tokens']
        del payload['max_tokens']

    # Handle system role conversion based on model type
    if payload['messages'][0]['role'] == 'system':
        model_lower = payload['model'].lower()
        # Legacy models use "user" role instead of "system"
        if model_lower.startswith('o1-mini') or model_lower.startswith('o1-preview'):
            payload['messages'][0]['role'] = 'user'
        else:
            payload['messages'][0]['role'] = 'developer'

    return payload


async def get_headers_and_cookies(
    request: Request,
    url,
    key=None,
    config=None,
    metadata: dict | None = None,
    user: UserModel = None,
):
    cookies = {}
    headers = {
        'Content-Type': 'application/json',
        **(
            {
                'HTTP-Referer': 'https://zanellm.ai/',
                'X-Title': 'ZaneLLM',
            }
            if 'openrouter.ai' in url
            else {}
        ),
    }

    if ENABLE_FORWARD_USER_INFO_HEADERS and user:
        headers = include_user_info_headers(headers, user)
        if metadata and metadata.get('chat_id'):
            headers[FORWARD_SESSION_INFO_HEADER_CHAT_ID] = metadata.get('chat_id')

    token = None
    auth_type = config.get('auth_type')

    if auth_type == 'bearer' or auth_type is None:
        # Default to bearer if not specified
        token = f'{key}'
    elif auth_type == 'none':
        token = None
    elif auth_type == 'session':
        cookies = request.cookies
        token = request.state.token.credentials
    elif auth_type == 'system_oauth':
        cookies = request.cookies

        oauth_token = None
        try:
            if request.cookies.get('oauth_session_id', None):
                oauth_token = await request.app.state.oauth_manager.get_oauth_token(
                    user.id,
                    request.cookies.get('oauth_session_id', None),
                )
        except Exception as e:
            log.error(f'Error getting OAuth token: {e}')

        if oauth_token:
            token = f'{oauth_token.get("access_token", "")}'

    elif auth_type in ('azure_ad', 'microsoft_entra_id'):
        token = get_microsoft_entra_id_access_token()

    if token:
        headers['Authorization'] = f'Bearer {token}'

    if config.get('headers') and isinstance(config.get('headers'), dict):
        custom_headers = get_custom_headers(config.get('headers'), user, metadata, request=request)
        headers.update(custom_headers)

    return headers, cookies


def get_microsoft_entra_id_access_token():
    """
    Get Microsoft Entra ID access token using DefaultAzureCredential for Azure OpenAI.
    Returns the token string or None if authentication fails.
    """
    try:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), 'https://cognitiveservices.azure.com/.default'
        )
        return token_provider()
    except Exception as e:
        log.error(f'Error getting Microsoft Entra ID access token: {e}')
        return None


##########################################
#
# API routes
#
##########################################

router = APIRouter()

LLAMACPP_LOADED_STATES = {'loaded', 'sleeping'}
LLAMACPP_UNLOADED_STATES = {'loading', 'unloaded'}


def get_llamacpp_model_loaded_state(model: dict, provider: str, manual_model_ids: bool = False) -> bool | None:
    if provider != 'llama.cpp':
        return None

    status = model.get('status')
    if isinstance(status, dict):
        value = status.get('value')
        if value in LLAMACPP_LOADED_STATES:
            return True
        if value in LLAMACPP_UNLOADED_STATES:
            return False

    if not manual_model_ids and 'status' not in model:
        return True

    return None


OPENAI_CONFIG_KEYS = {
    'ENABLE_OPENAI_API': 'openai.enable',
    'OPENAI_API_BASE_URLS': 'openai.api_base_urls',
    'OPENAI_API_KEYS': 'openai.api_keys',
    'OPENAI_API_CONFIGS': 'openai.api_configs',
}


async def get_openai_config() -> dict:
    values = await Config.get_many(*OPENAI_CONFIG_KEYS.values())
    return {field: values[storage_key] for field, storage_key in OPENAI_CONFIG_KEYS.items() if storage_key in values}


async def get_openai_runtime_config() -> tuple[bool, list[str], list[str], dict]:
    values = await Config.get_many('openai.enable', 'openai.api_base_urls', 'openai.api_keys', 'openai.api_configs')
    return (
        values.get('openai.enable'),
        values.get('openai.api_base_urls') or [],
        values.get('openai.api_keys') or [],
        values.get('openai.api_configs') or {},
    )


async def normalize_openai_api_keys(api_base_urls: list[str], api_keys: list[str]) -> list[str]:
    if len(api_keys) > len(api_base_urls):
        api_keys = api_keys[: len(api_base_urls)]
    elif len(api_keys) < len(api_base_urls):
        api_keys = [*api_keys, *([''] * (len(api_base_urls) - len(api_keys)))]

    await Config.upsert({'openai.api_keys': api_keys})
    return api_keys


async def get_openai_connection(idx: int) -> tuple[str, str, dict]:
    _, api_base_urls, api_keys, api_configs = await get_openai_runtime_config()
    url = api_base_urls[idx]
    key = api_keys[idx]
    api_config = api_configs.get(str(idx), api_configs.get(url, {}))
    return url, key, api_config


@router.get('/config')
async def get_config(request: Request, user=Depends(get_admin_user)):
    return await get_openai_config()


class OpenAIConfigForm(BaseModel):
    ENABLE_OPENAI_API: bool | None = None
    OPENAI_API_BASE_URLS: list[str]
    OPENAI_API_KEYS: list[str]
    OPENAI_API_CONFIGS: dict


@router.post('/config/update')
async def update_config(request: Request, form_data: OpenAIConfigForm, user=Depends(get_admin_user)):
    api_keys = form_data.OPENAI_API_KEYS

    if len(api_keys) > len(form_data.OPENAI_API_BASE_URLS):
        api_keys = api_keys[: len(form_data.OPENAI_API_BASE_URLS)]
    elif len(api_keys) < len(form_data.OPENAI_API_BASE_URLS):
        api_keys = [*api_keys, *([''] * (len(form_data.OPENAI_API_BASE_URLS) - len(api_keys)))]

    valid_keys = set(map(str, range(len(form_data.OPENAI_API_BASE_URLS))))
    api_configs = {key: value for key, value in form_data.OPENAI_API_CONFIGS.items() if key in valid_keys}

    await Config.upsert(
        {
            'openai.enable': form_data.ENABLE_OPENAI_API,
            'openai.api_base_urls': form_data.OPENAI_API_BASE_URLS,
            'openai.api_keys': api_keys,
            'openai.api_configs': api_configs,
        }
    )
    await publish_event(
        request,
        EVENTS.MODEL_PROVIDER_CONFIG_UPDATED,
        actor=user,
        subject_id='openai',
        subject_type='model.provider_config',
        data={
            'provider': 'openai',
            'enabled': form_data.ENABLE_OPENAI_API,
            'base_url_count': len(form_data.OPENAI_API_BASE_URLS),
        },
    )

    return {
        'ENABLE_OPENAI_API': form_data.ENABLE_OPENAI_API,
        'OPENAI_API_BASE_URLS': form_data.OPENAI_API_BASE_URLS,
        'OPENAI_API_KEYS': api_keys,
        'OPENAI_API_CONFIGS': api_configs,
    }


@router.post('/audio/speech')
async def speech(request: Request, user=Depends(get_verified_user)):
    if user.role != 'admin' and not await has_permission(user.id, 'chat.tts', await Config.get('user.permissions')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    idx = None
    try:
        _, api_base_urls, _, _ = await get_openai_runtime_config()
        idx = api_base_urls.index('https://api.openai.com/v1')

        body = await request.body()
        name = hashlib.sha256(body).hexdigest()

        SPEECH_CACHE_DIR = CACHE_DIR / 'audio' / 'speech'
        SPEECH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        file_path = SPEECH_CACHE_DIR.joinpath(f'{name}.mp3')
        file_body_path = SPEECH_CACHE_DIR.joinpath(f'{name}.json')

        # Check if the file already exists in the cache
        if file_path.is_file():
            return FileResponse(file_path)

        url, key, api_config = await get_openai_connection(idx)

        headers, cookies = await get_headers_and_cookies(request, url, key, api_config, user=user)

        r = None
        try:
            session = await get_session()
            r = await session.post(
                url=f'{url}/audio/speech',
                data=body,
                headers=headers,
                cookies=cookies,
                ssl=AIOHTTP_CLIENT_SESSION_SSL,
            )

            r.raise_for_status()

            # Save the streaming content to a file
            with open(file_path, 'wb') as f:
                async for chunk in r.content.iter_chunked(8192):
                    f.write(chunk)

            with open(file_body_path, 'w') as f:
                json.dump(json.loads(body.decode('utf-8')), f)

            # Return the saved file
            return FileResponse(file_path)

        except Exception as e:
            log.exception(e)

            detail = None
            if r is not None:
                try:
                    res = await r.json()
                    if 'error' in res:
                        detail = f'External: {res["error"]}'
                except Exception:
                    detail = f'External: {e}'

            raise HTTPException(
                status_code=r.status if r else 500,
                detail=detail if detail else 'ZaneLLM: Server Connection Error',
            )

    except ValueError:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES.OPENAI_NOT_FOUND)


async def get_all_models_responses(request: Request, user: UserModel) -> list:
    enable_openai_api, api_base_urls, api_keys, api_configs = await get_openai_runtime_config()
    if not enable_openai_api:
        return []

    num_urls = len(api_base_urls)
    num_keys = len(api_keys)

    if num_keys != num_urls:
        api_keys = await normalize_openai_api_keys(api_base_urls, api_keys)

    request_tasks = []
    for idx, url in enumerate(api_base_urls):
        if (str(idx) not in api_configs) and (url not in api_configs):  # Legacy support
            request_tasks.append(get_models_request(request, url, api_keys[idx], user=user))
        else:
            api_config = api_configs.get(
                str(idx),
                api_configs.get(url, {}),  # Legacy support
            )

            enable = api_config.get('enable', True)
            model_ids = api_config.get('model_ids', [])

            if enable:
                if len(model_ids) == 0:
                    request_tasks.append(get_models_request(request, url, api_keys[idx], user=user, config=api_config))
                else:
                    model_list = {
                        'object': 'list',
                        'data': [
                            {
                                'id': model_id,
                                'name': model_id,
                                'owned_by': 'openai',
                                'openai': {'id': model_id},
                                'urlIdx': idx,
                            }
                            for model_id in model_ids
                        ],
                    }

                    request_tasks.append(asyncio.ensure_future(asyncio.sleep(0, model_list)))
            else:
                request_tasks.append(asyncio.ensure_future(asyncio.sleep(0, None)))

    responses = await asyncio.gather(*request_tasks)

    for idx, response in enumerate(responses):
        if response:
            url = api_base_urls[idx]
            api_config = api_configs.get(
                str(idx),
                api_configs.get(url, {}),  # Legacy support
            )

            connection_type = api_config.get('connection_type', 'external')
            prefix_id = api_config.get('prefix_id', None)
            tags = api_config.get('tags', [])
            provider = api_config.get('provider', '')

            model_list = response if isinstance(response, list) else response.get('data', [])
            if not isinstance(model_list, list):
                # Catch non-list responses
                model_list = []

            for model in model_list:
                # Remove name key if its value is None #16689
                if 'name' in model and model['name'] is None:
                    del model['name']

                if prefix_id:
                    model['id'] = f'{prefix_id}.{model.get("id", model.get("name", ""))}'

                if tags:
                    model['tags'] = tags

                if connection_type:
                    model['connection_type'] = connection_type

                if provider:
                    model['provider'] = provider

    log.debug(f'get_all_models:responses() {responses}')
    return responses


async def get_filtered_models(models, user, db=None):
    # Filter models based on user access control
    model_ids = [model['id'] for model in models.get('data', [])]
    model_infos = {model_info.id: model_info for model_info in await Models.get_models_by_ids(model_ids, db=db)}
    user_group_ids = {group.id for group in await Groups.get_groups_by_member_id(user.id, db=db)}

    # Batch-fetch accessible resource IDs in a single query instead of N has_access calls
    accessible_model_ids = await AccessGrants.get_accessible_resource_ids(
        user_id=user.id,
        resource_type='model',
        resource_ids=list(model_infos.keys()),
        permission='read',
        user_group_ids=user_group_ids,
        db=db,
    )

    filtered_models = []
    for model in models.get('data', []):
        model_info = model_infos.get(model['id'])
        if model_info:
            if user.id == model_info.user_id or model_info.id in accessible_model_ids:
                filtered_models.append(model)
    return filtered_models


@cached(
    ttl=MODELS_CACHE_TTL,
    # key_builder (not key) is the per-call hook in aiocache 0.12; `key=` is a
    # static key, so a `key=lambda` collapsed every caller to one shared entry.
    key_builder=lambda _func, request, user=None: f'openai_all_models_{user.id}' if user else 'openai_all_models',
)
async def get_all_models(request: Request, user: UserModel) -> dict[str, list]:
    log.info('get_all_models()')

    enable_openai_api, api_base_urls, _, api_configs = await get_openai_runtime_config()
    if not enable_openai_api:
        return {'data': []}

    responses = await get_all_models_responses(request, user=user)

    def extract_data(response):
        if response and 'data' in response:
            return response['data']
        if isinstance(response, list):
            return response
        return None

    def is_supported_openai_models(model_id):
        if any(
            name in model_id
            for name in [
                'babbage',
                'dall-e',
                'davinci',
                'embedding',
                'tts',
                'whisper',
            ]
        ):
            return False
        return True

    def get_merged_models(model_lists):
        log.debug(f'merge_models_lists {model_lists}')
        models = {}

        for idx, model_list in enumerate(model_lists):
            if model_list is not None and 'error' not in model_list:
                for model in model_list:
                    model_id = model.get('id') or model.get('name')

                    base_url = api_base_urls[idx]
                    hostname = urlparse(base_url).hostname if base_url else None
                    if hostname == 'api.openai.com' and not is_supported_openai_models(model_id):
                        # Skip unwanted OpenAI models
                        continue

                    if model_id and model_id not in models:
                        api_config = api_configs.get(str(idx), api_configs.get(base_url, {}))
                        provider = model.get('provider', '')
                        provider_hint = provider or _get_provider_hint(base_url, api_config)
                        source_label = _get_connection_source_label(base_url, api_config)
                        model_family = _infer_model_family(model_id, provider_hint)
                        merged = {
                            **model,
                            'name': model.get('name', model_id),
                            'owned_by': 'openai',
                            'openai': model,
                            'connection_type': model.get('connection_type', 'external'),
                            'provider': provider,
                            'provider_hint': provider_hint,
                            'model_family': model_family,
                            'source_label': source_label,
                            'source_host': urlparse(base_url).hostname or '',
                            'urlIdx': idx,
                        }

                        loaded = get_llamacpp_model_loaded_state(
                            model,
                            provider,
                            manual_model_ids=bool(api_config.get('model_ids')),
                        )
                        if loaded is not None:
                            merged['loaded'] = loaded

                        models[model_id] = merged

        return models

    models = get_merged_models(map(extract_data, responses))
    log.debug(f'models: {models}')

    request.app.state.OPENAI_MODELS = models
    return {'data': list(models.values())}


@router.get('/models')
@router.get('/models/{url_idx}')
async def get_models(request: Request, url_idx: int | None = None, user=Depends(get_verified_user)):
    if not await Config.get('openai.enable'):
        raise HTTPException(status_code=503, detail='OpenAI API is disabled')

    models = {
        'data': [],
    }

    if url_idx is None:
        models = await get_all_models(request, user=user)
    else:
        url, key, api_config = await get_openai_connection(url_idx)

        r = None
        async with aiohttp.ClientSession(
            trust_env=True,
            timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST),
        ) as session:
            try:
                headers, cookies = await get_headers_and_cookies(request, url, key, api_config, user=user)

                if api_config.get('azure') or api_config.get('provider') == 'azure':
                    models = {
                        'data': api_config.get('model_ids', []) or [],
                        'object': 'list',
                    }
                elif is_anthropic_url(url):
                    models = await get_anthropic_models(url, key, user=user)
                    if models is None:
                        raise Exception('Failed to connect to Anthropic API')
                else:
                    response_data = await discover_models_request(
                        request,
                        url,
                        key,
                        user=user,
                        config=api_config,
                        raise_on_error=True,
                    )

                    if 'api.openai.com' in url:
                        response_data['data'] = [
                            model
                            for model in response_data.get('data', [])
                            if not any(
                                name in model['id']
                                for name in [
                                    'babbage',
                                    'dall-e',
                                    'davinci',
                                    'embedding',
                                    'tts',
                                    'whisper',
                                ]
                            )
                        ]

                    models = response_data
            except aiohttp.ClientError as e:
                # ClientError covers all aiohttp requests issues
                log.exception(f'Client error: {str(e)}')
                raise HTTPException(status_code=500, detail='ZaneLLM: Server Connection Error')
            except Exception as e:
                log.exception(f'Unexpected error: {e}')
                error_detail = f'Unexpected error: {str(e)}'
                raise HTTPException(status_code=500, detail=error_detail)

    if user.role == 'user' and not BYPASS_MODEL_ACCESS_CONTROL:
        models['data'] = await get_filtered_models(models, user)

    return models


class ConnectionVerificationForm(BaseModel):
    url: str
    key: str

    config: dict | None = None


@router.post('/verify')
async def verify_connection(
    request: Request,
    form_data: ConnectionVerificationForm,
    user=Depends(get_admin_user),
):
    url = form_data.url
    key = form_data.key

    api_config = form_data.config or {}

    async with aiohttp.ClientSession(
        trust_env=True,
        timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST),
    ) as session:
        try:
            headers, cookies = await get_headers_and_cookies(request, url, key, api_config, user=user)

            if api_config.get('azure') or api_config.get('provider') == 'azure':
                # Only set api-key header if not using Azure Entra ID authentication
                auth_type = api_config.get('auth_type', 'bearer')
                if auth_type not in ('azure_ad', 'microsoft_entra_id'):
                    headers['api-key'] = key

                # Azure v1 format: base URL already ends with /openai/v1,
                # use standard /models endpoint without api-version.
                is_azure_v1 = bool(re.search(r'/openai/v1(?:/|$)', url))

                if is_azure_v1:
                    verify_url = f'{url.rstrip("/")}/models'
                else:
                    api_version = api_config.get('api_version', '') or '2023-03-15-preview'
                    verify_url = f'{url}/openai/models?api-version={api_version}'

                async with session.get(
                    url=verify_url,
                    headers=headers,
                    cookies=cookies,
                    ssl=AIOHTTP_CLIENT_SESSION_SSL,
                ) as r:
                    try:
                        response_data = await r.json()
                    except Exception:
                        response_data = await r.text()

                    if r.status != 200:
                        if isinstance(response_data, (dict, list)):
                            return JSONResponse(status_code=r.status, content=response_data)
                        else:
                            return PlainTextResponse(status_code=r.status, content=response_data)

                    return response_data
            elif is_anthropic_url(url):
                result = await get_anthropic_models(url, key)
                if result is None:
                    raise HTTPException(status_code=500, detail=ERROR_MESSAGES.SERVER_CONNECTION_ERROR)
                if 'error' in result:
                    raise HTTPException(status_code=500, detail=result['error'])
                return result
            else:
                return await discover_models_request(
                    request,
                    url,
                    key,
                    user=user,
                    config=api_config,
                    raise_on_error=True,
                )

        except aiohttp.ClientError as e:
            # ClientError covers all aiohttp requests issues
            log.exception(f'Client error: {str(e)}')
            raise HTTPException(status_code=500, detail=ERROR_MESSAGES.SERVER_CONNECTION_ERROR)
        except ModelDiscoveryError as e:
            log.exception(f'Model discovery error: {e}')
            raise HTTPException(status_code=500, detail=f'Model discovery failed: {e}')
        except Exception as e:
            log.exception(f'Unexpected error: {e}')
            raise HTTPException(status_code=500, detail=ERROR_MESSAGES.SERVER_CONNECTION_ERROR)


def get_azure_allowed_params(api_version: str) -> set[str]:
    allowed_params = {
        'messages',
        'temperature',
        'role',
        'content',
        'contentPart',
        'contentPartImage',
        'enhancements',
        'dataSources',
        'n',
        'stream',
        'stop',
        'max_tokens',
        'presence_penalty',
        'frequency_penalty',
        'logit_bias',
        'user',
        'function_call',
        'functions',
        'tools',
        'tool_choice',
        'top_p',
        'log_probs',
        'top_logprobs',
        'response_format',
        'seed',
        'max_completion_tokens',
        'reasoning_effort',
    }

    try:
        if api_version >= '2024-09-01-preview':
            allowed_params.add('stream_options')
    except ValueError:
        log.debug(f'Invalid API version {api_version} for Azure OpenAI. Defaulting to allowed parameters.')

    return allowed_params


def is_openai_new_model(model: str) -> bool:
    model_lower = model.lower()
    # o-series models (o1, o3, o4, o5, ...)
    if re.match(r'^o\d+', model_lower):
        return True
    # gpt-N where N >= 5 (gpt-5, gpt-5.2, gpt-6, ...)
    m = re.match(r'^gpt-(\d+)', model_lower)
    if m and int(m.group(1)) >= 5:
        return True
    return False


def _sanitize_model_for_url(model: str) -> str:
    """Sanitize a model name before interpolating it into a URL path.

    Rejects path traversal attempts (../, /, \\) and percent-encodes
    the name so it is safe to use as a single URL path segment
    (e.g. Azure deployment name).
    """
    if not model or '..' in model or '/' in model or '\\' in model:
        raise HTTPException(
            status_code=400,
            detail='Invalid model name: must not be empty or contain path separators or traversal sequences',
        )
    return quote(model, safe='')


def convert_to_azure_payload(url, payload: dict, api_version: str):
    model = payload.get('model', '')

    # Filter allowed parameters based on Azure OpenAI API
    allowed_params = get_azure_allowed_params(api_version)

    # Special handling for o-series models
    if is_openai_new_model(model):
        # Convert max_tokens to max_completion_tokens for o-series models
        if 'max_tokens' in payload:
            payload['max_completion_tokens'] = payload['max_tokens']
            del payload['max_tokens']

        # Remove temperature if not 1 for o-series models
        if 'temperature' in payload and payload['temperature'] != 1:
            log.debug(
                f'Removing temperature parameter for o-series model {model} as only default value (1) is supported'
            )
            del payload['temperature']

    # Filter out unsupported parameters
    payload = {k: v for k, v in payload.items() if k in allowed_params}

    # Sanitize model name to prevent path traversal in the deployment URL
    model = _sanitize_model_for_url(model)

    url = f'{url}/openai/deployments/{model}'
    return url, payload


# Fields accepted by the Responses API for each input item type.
RESPONSES_ALLOWED_FIELDS: dict[str, set[str]] = {
    'message': {'type', 'role', 'content'},
    'function_call': {'type', 'call_id', 'name', 'arguments', 'id'},
    'function_call_output': {'type', 'call_id', 'output'},
}


def _normalize_stored_item(item: dict) -> dict:
    """Strip local-only fields from a stored output item before replaying it.

    ZaneLLM stores extra bookkeeping fields (``id``, ``status``,
    ``started_at``, ``ended_at``, ``duration``, ``_tag_type``,
    ``attributes``, ``summary``, etc.) that the Responses API does
    not accept.  This helper returns a copy containing only the
    fields the API understands.
    """
    item_type = item.get('type', '')
    allowed = RESPONSES_ALLOWED_FIELDS.get(item_type)
    if allowed is None:
        # Unknown type — pass through as-is (e.g. reasoning, extension items).
        return item
    return {k: v for k, v in item.items() if k in allowed}


def convert_to_responses_payload(payload: dict) -> dict:
    """
    Convert Chat Completions payload to Responses API format.

    Chat Completions: { messages: [{role, content}], ... }
    Responses API: { input: [{type: "message", role, content: [...]}], instructions: "system" }
    """
    messages = payload.pop('messages', [])

    system_content = ''
    input_items = []

    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')

        # Check for stored output items (from previous Responses API turn)
        stored_output = msg.get('output')
        if stored_output and isinstance(stored_output, list):
            input_items.extend(_normalize_stored_item(item) for item in stored_output)
            continue

        if role == 'system':
            if isinstance(content, str):
                system_content = content
            elif isinstance(content, list):
                system_content = '\n'.join(p.get('text', '') for p in content if p.get('type') == 'text')
            continue

        # Handle assistant messages with tool_calls (from convert_output_to_messages)
        if role == 'assistant' and msg.get('tool_calls'):
            # Add text content as message if present
            if content:
                text = (
                    content
                    if isinstance(content, str)
                    else '\n'.join(p.get('text', '') for p in content if p.get('type') == 'text')
                )
                if text.strip():
                    input_items.append(
                        {
                            'type': 'message',
                            'role': 'assistant',
                            'content': [{'type': 'output_text', 'text': text}],
                        }
                    )
            # Convert each tool_call to a function_call input item
            for tool_call in msg['tool_calls']:
                func = tool_call.get('function', {})
                input_items.append(
                    {
                        'type': 'function_call',
                        'call_id': tool_call.get('id', ''),
                        'name': func.get('name', ''),
                        'arguments': func.get('arguments', '{}'),
                    }
                )
            continue

        # Handle tool result messages
        if role == 'tool':
            input_items.append(
                {
                    'type': 'function_call_output',
                    'call_id': msg.get('tool_call_id', ''),
                    'output': msg.get('content', ''),
                }
            )
            continue

        # Convert content format
        text_type = 'output_text' if role == 'assistant' else 'input_text'

        if isinstance(content, str):
            content_parts = [{'type': text_type, 'text': content}]
        elif isinstance(content, list):
            content_parts = []
            for part in content:
                if part.get('type') == 'text':
                    content_parts.append({'type': text_type, 'text': part.get('text', '')})
                elif part.get('type') == 'image_url':
                    url_data = part.get('image_url', {})
                    url = url_data.get('url', '') if isinstance(url_data, dict) else url_data
                    content_parts.append({'type': 'input_image', 'image_url': url})
        else:
            content_parts = [{'type': text_type, 'text': str(content)}]

        input_items.append({'type': 'message', 'role': role, 'content': content_parts})

    responses_payload = {**payload, 'input': input_items}

    # Forward previous_response_id when the middleware has set it
    # (only used when ENABLE_RESPONSES_API_STATEFUL is enabled).
    previous_response_id = responses_payload.pop('previous_response_id', None)
    if previous_response_id:
        responses_payload['previous_response_id'] = previous_response_id

    if system_content:
        responses_payload['instructions'] = system_content

    if 'max_tokens' in responses_payload:
        responses_payload['max_output_tokens'] = responses_payload.pop('max_tokens')

    if 'max_completion_tokens' in responses_payload:
        responses_payload['max_output_tokens'] = responses_payload.pop('max_completion_tokens')

    reasoning_effort = responses_payload.pop('reasoning_effort', None)
    if reasoning_effort:
        reasoning = responses_payload.get('reasoning')
        if not isinstance(reasoning, dict):
            reasoning = {}
        reasoning.setdefault('effort', reasoning_effort)
        responses_payload['reasoning'] = reasoning

    # Remove Chat Completions-only parameters not supported by the Responses API
    for unsupported_key in (
        'stream_options',
        'logit_bias',
        'frequency_penalty',
        'presence_penalty',
        'stop',
    ):
        responses_payload.pop(unsupported_key, None)

    # Convert Chat Completions tools format to Responses API format
    # Chat Completions: {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}
    # Responses API:    {"type": "function", "name": ..., "description": ..., "parameters": ...}
    if 'tools' in responses_payload and isinstance(responses_payload['tools'], list):
        converted_tools = []
        for tool in responses_payload['tools']:
            if isinstance(tool, dict) and 'function' in tool:
                func = tool['function']
                converted_tool = {'type': tool.get('type', 'function')}
                if isinstance(func, dict):
                    converted_tool['name'] = func.get('name', '')
                    if 'description' in func:
                        converted_tool['description'] = func['description']
                    if 'parameters' in func:
                        converted_tool['parameters'] = func['parameters']
                    if 'strict' in func:
                        converted_tool['strict'] = func['strict']
                converted_tools.append(converted_tool)
            else:
                # Already in correct format or unknown format, pass through
                converted_tools.append(tool)
        responses_payload['tools'] = converted_tools

    return responses_payload


def _normalize_openai_content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        values = []
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get('type') in {'text', 'input_text', 'output_text'}:
                values.append(str(part.get('text', '')))
        return '\n'.join(value for value in values if value)
    return '' if content is None else str(content)


def _openai_content_to_anthropic_blocks(content) -> list[dict]:
    if isinstance(content, str):
        return [{'type': 'text', 'text': content}]

    blocks = []
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            part_type = part.get('type')
            if part_type in {'text', 'input_text', 'output_text'}:
                blocks.append({'type': 'text', 'text': str(part.get('text', ''))})
            elif part_type == 'image_url':
                image = part.get('image_url')
                image_url = image.get('url', '') if isinstance(image, dict) else image
                if isinstance(image_url, str) and image_url.startswith('data:') and ';base64,' in image_url:
                    media_type = image_url.split(';base64,', 1)[0].removeprefix('data:')
                    data = image_url.split(';base64,', 1)[1]
                    blocks.append(
                        {
                            'type': 'image',
                            'source': {'type': 'base64', 'media_type': media_type, 'data': data},
                        }
                    )
                elif isinstance(image_url, str) and image_url:
                    blocks.append({'type': 'image', 'source': {'type': 'url', 'url': image_url}})

    if not blocks:
        text = _normalize_openai_content_to_text(content)
        if text:
            blocks.append({'type': 'text', 'text': text})
    return blocks


def _convert_openai_to_anthropic_payload(payload: dict) -> dict:
    messages = payload.get('messages', [])
    system_parts = []
    anthropic_messages = []

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get('role', 'user')
        content = message.get('content', '')

        if role in {'system', 'developer'}:
            text = _normalize_openai_content_to_text(content)
            if text:
                system_parts.append(text)
            continue

        if role == 'tool':
            anthropic_messages.append(
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'tool_result',
                            'tool_use_id': message.get('tool_call_id', ''),
                            'content': _normalize_openai_content_to_text(content),
                        }
                    ],
                }
            )
            continue

        anthropic_role = 'assistant' if role == 'assistant' else 'user'
        content_blocks = _openai_content_to_anthropic_blocks(content)

        tool_calls = message.get('tool_calls') or []
        for tool_call in tool_calls:
            function = tool_call.get('function', {}) if isinstance(tool_call, dict) else {}
            try:
                tool_input = json.loads(function.get('arguments') or '{}')
            except Exception:
                tool_input = {}
            content_blocks.append(
                {
                    'type': 'tool_use',
                    'id': tool_call.get('id', ''),
                    'name': function.get('name', ''),
                    'input': tool_input,
                }
            )

        anthropic_messages.append({'role': anthropic_role, 'content': content_blocks})

    anthropic_payload = {
        'model': payload.get('model', ''),
        'messages': anthropic_messages,
        'max_tokens': payload.get('max_tokens')
        or payload.get('max_completion_tokens')
        or payload.get('max_output_tokens')
        or 4096,
    }

    if system_parts:
        anthropic_payload['system'] = '\n\n'.join(system_parts)

    for key in ('temperature', 'top_p', 'metadata'):
        if payload.get(key) is not None:
            anthropic_payload[key] = payload[key]

    if payload.get('stop'):
        anthropic_payload['stop_sequences'] = payload['stop'] if isinstance(payload['stop'], list) else [payload['stop']]

    if payload.get('tools') and isinstance(payload['tools'], list):
        tools = []
        for tool in payload['tools']:
            if not isinstance(tool, dict):
                continue
            function = tool.get('function') if tool.get('type') == 'function' else tool
            if not isinstance(function, dict):
                continue
            tools.append(
                {
                    'name': function.get('name', ''),
                    'description': function.get('description', ''),
                    'input_schema': function.get('parameters', {'type': 'object', 'properties': {}}),
                }
            )
        if tools:
            anthropic_payload['tools'] = tools

    reasoning_effort = payload.get('reasoning_effort')
    if reasoning_effort:
        effort = str(reasoning_effort).lower()
        budgets = {'minimal': 1024, 'low': 2048, 'medium': 4096, 'high': 8192, 'xhigh': 16384}
        if effort not in {'none', 'off', 'false'}:
            anthropic_payload['thinking'] = {
                'type': 'enabled',
                'budget_tokens': budgets.get(effort, 4096),
            }

    return anthropic_payload


def _convert_anthropic_to_openai_response(response: dict, model: str) -> dict:
    content = []
    tool_calls = []

    for block in (response.get('content', []) if isinstance(response.get('content'), list) else []):
        if not isinstance(block, dict):
            continue
        if block.get('type') == 'text':
            content.append(block.get('text', ''))
        elif block.get('type') == 'tool_use':
            tool_calls.append(
                {
                    'id': block.get('id', ''),
                    'type': 'function',
                    'function': {
                        'name': block.get('name', ''),
                        'arguments': json.dumps(block.get('input', {})),
                    },
                }
            )

    stop_reason = response.get('stop_reason')
    finish_reason = {'end_turn': 'stop', 'max_tokens': 'length', 'tool_use': 'tool_calls'}.get(stop_reason, stop_reason)
    usage = response.get('usage', {}) if isinstance(response.get('usage'), dict) else {}

    message = {'role': 'assistant', 'content': ''.join(content)}
    if tool_calls:
        message['tool_calls'] = tool_calls

    return {
        'id': response.get('id', ''),
        'object': 'chat.completion',
        'created': 0,
        'model': response.get('model') or model,
        'choices': [{'index': 0, 'message': message, 'finish_reason': finish_reason or 'stop'}],
        'usage': {
            'prompt_tokens': usage.get('input_tokens', 0),
            'completion_tokens': usage.get('output_tokens', 0),
            'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0),
        },
    }


def _openai_content_to_gemini_parts(content) -> list[dict]:
    if isinstance(content, str):
        return [{'text': content}]

    parts = []
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            part_type = part.get('type')
            if part_type in {'text', 'input_text', 'output_text'}:
                parts.append({'text': str(part.get('text', ''))})
            elif part_type == 'image_url':
                image = part.get('image_url')
                image_url = image.get('url', '') if isinstance(image, dict) else image
                if isinstance(image_url, str) and image_url.startswith('data:') and ';base64,' in image_url:
                    media_type = image_url.split(';base64,', 1)[0].removeprefix('data:')
                    data = image_url.split(';base64,', 1)[1]
                    parts.append({'inline_data': {'mime_type': media_type, 'data': data}})
                elif isinstance(image_url, str) and image_url:
                    parts.append({'file_data': {'mime_type': 'image/jpeg', 'file_uri': image_url}})

    if not parts:
        text = _normalize_openai_content_to_text(content)
        if text:
            parts.append({'text': text})
    return parts


def _convert_openai_to_gemini_payload(payload: dict) -> dict:
    messages = payload.get('messages', [])
    contents = []
    system_parts = []

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get('role', 'user')
        content = message.get('content', '')

        if role in {'system', 'developer'}:
            text = _normalize_openai_content_to_text(content)
            if text:
                system_parts.append({'text': text})
            continue

        gemini_role = 'model' if role == 'assistant' else 'user'
        parts = _openai_content_to_gemini_parts(content)
        if parts:
            contents.append({'role': gemini_role, 'parts': parts})

    generation_config = {}
    if payload.get('temperature') is not None:
        generation_config['temperature'] = payload['temperature']
    if payload.get('top_p') is not None:
        generation_config['topP'] = payload['top_p']
    max_tokens = payload.get('max_tokens') or payload.get('max_completion_tokens') or payload.get('max_output_tokens')
    if max_tokens is not None:
        generation_config['maxOutputTokens'] = max_tokens
    if payload.get('stop'):
        generation_config['stopSequences'] = payload['stop'] if isinstance(payload['stop'], list) else [payload['stop']]

    reasoning_effort = payload.get('reasoning_effort')
    if reasoning_effort:
        budgets = {
            'none': 0,
            'off': 0,
            'false': 0,
            'minimal': 512,
            'low': 1024,
            'medium': 4096,
            'high': 8192,
            'xhigh': 16384,
        }
        generation_config['thinkingConfig'] = {
            'thinkingBudget': budgets.get(str(reasoning_effort).lower(), 4096),
        }

    gemini_payload = {'contents': contents}
    if system_parts:
        gemini_payload['systemInstruction'] = {'parts': system_parts}
    if generation_config:
        gemini_payload['generationConfig'] = generation_config

    return gemini_payload


def _convert_gemini_to_openai_response(response: dict, model: str) -> dict:
    candidate = {}
    if isinstance(response.get('candidates'), list) and response['candidates']:
        candidate = response['candidates'][0]

    content = []
    candidate_content = candidate.get('content', {}) if isinstance(candidate, dict) else {}
    for part in (candidate_content.get('parts', []) if isinstance(candidate_content.get('parts'), list) else []):
        if isinstance(part, dict) and part.get('text'):
            content.append(part.get('text', ''))

    usage = response.get('usageMetadata', {}) if isinstance(response.get('usageMetadata'), dict) else {}

    return {
        'id': response.get('responseId', ''),
        'object': 'chat.completion',
        'created': 0,
        'model': model,
        'choices': [
            {
                'index': 0,
                'message': {'role': 'assistant', 'content': ''.join(content)},
                'finish_reason': candidate.get('finishReason', 'STOP').lower() if isinstance(candidate, dict) else 'stop',
            }
        ],
        'usage': {
            'prompt_tokens': usage.get('promptTokenCount', 0),
            'completion_tokens': usage.get('candidatesTokenCount', 0),
            'total_tokens': usage.get('totalTokenCount', 0),
        },
    }


def convert_responses_result(response: dict) -> dict:
    """
    Convert non-streaming Responses API result to Chat Completions format.

    Extracts text from message output items so all downstream consumers
    (frontend tasks, get_content_from_response) work without modification.
    """
    output_items = response.get('output', [])

    content = ''
    for item in output_items:
        if item.get('type') == 'message':
            for part in item.get('content', []):
                if part.get('type') == 'output_text':
                    content += part.get('text', '')

    return {
        'id': response.get('id', ''),
        'object': 'chat.completion',
        'model': response.get('model', ''),
        'choices': [
            {
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': content,
                },
                'finish_reason': 'stop',
            }
        ],
        'usage': response.get('usage', {}),
    }


def _responses_content_to_openai_content(content):
    if isinstance(content, str):
        return content

    parts = []
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            part_type = part.get('type')
            if part_type in {'input_text', 'output_text', 'text'}:
                parts.append({'type': 'text', 'text': str(part.get('text', ''))})
            elif part_type == 'input_image':
                image_url = part.get('image_url') or part.get('file_id') or ''
                if image_url:
                    parts.append({'type': 'image_url', 'image_url': {'url': image_url}})

    if not parts:
        return ''
    if len(parts) == 1 and parts[0].get('type') == 'text':
        return parts[0].get('text', '')
    return parts


def convert_responses_payload_to_chat(payload: dict) -> dict:
    messages = []
    instructions = payload.get('instructions')
    if instructions:
        messages.append({'role': 'system', 'content': str(instructions)})

    input_data = payload.get('input', [])
    if isinstance(input_data, str):
        messages.append({'role': 'user', 'content': input_data})
    elif isinstance(input_data, list):
        pending_tool_calls = []
        for item in input_data:
            if isinstance(item, str):
                messages.append({'role': 'user', 'content': item})
                continue
            if not isinstance(item, dict):
                continue

            item_type = item.get('type')
            if item_type == 'message':
                role = item.get('role', 'user')
                if role not in {'system', 'developer', 'user', 'assistant'}:
                    role = 'user'
                if role == 'developer':
                    role = 'system'
                messages.append(
                    {
                        'role': role,
                        'content': _responses_content_to_openai_content(item.get('content', '')),
                    }
                )
            elif item_type == 'function_call':
                pending_tool_calls.append(
                    {
                        'id': item.get('call_id') or item.get('id') or '',
                        'type': 'function',
                        'function': {
                            'name': item.get('name', ''),
                            'arguments': item.get('arguments', '{}'),
                        },
                    }
                )
            elif item_type == 'function_call_output':
                if pending_tool_calls:
                    messages.append({'role': 'assistant', 'content': '', 'tool_calls': pending_tool_calls})
                    pending_tool_calls = []
                messages.append(
                    {
                        'role': 'tool',
                        'tool_call_id': item.get('call_id') or item.get('id') or '',
                        'content': item.get('output', ''),
                    }
                )

        if pending_tool_calls:
            messages.append({'role': 'assistant', 'content': '', 'tool_calls': pending_tool_calls})

    chat_payload = {'model': payload.get('model', ''), 'messages': messages}

    for key in ('temperature', 'top_p', 'metadata', 'parallel_tool_calls', 'user'):
        if payload.get(key) is not None:
            chat_payload[key] = payload[key]

    max_tokens = payload.get('max_output_tokens')
    if max_tokens is not None:
        chat_payload['max_tokens'] = max_tokens

    reasoning = payload.get('reasoning')
    if isinstance(reasoning, dict) and reasoning.get('effort'):
        chat_payload['reasoning_effort'] = reasoning.get('effort')

    if payload.get('tools') and isinstance(payload['tools'], list):
        tools = []
        for tool in payload['tools']:
            if not isinstance(tool, dict):
                continue
            if tool.get('type') == 'function':
                tools.append(
                    {
                        'type': 'function',
                        'function': {
                            'name': tool.get('name', ''),
                            'description': tool.get('description', ''),
                            'parameters': tool.get('parameters', {'type': 'object', 'properties': {}}),
                        },
                    }
                )
            else:
                tools.append(tool)
        if tools:
            chat_payload['tools'] = tools

    if payload.get('tool_choice') is not None:
        chat_payload['tool_choice'] = payload['tool_choice']

    return chat_payload


def convert_chat_completion_to_responses_result(response: dict, request_payload: dict) -> dict:
    choice = {}
    if isinstance(response.get('choices'), list) and response['choices']:
        choice = response['choices'][0]

    message = choice.get('message', {}) if isinstance(choice, dict) else {}
    text = _normalize_openai_content_to_text(message.get('content', ''))
    output = []

    if text:
        output.append(
            {
                'type': 'message',
                'id': f'msg_{hashlib.sha256(text.encode()).hexdigest()[:24]}',
                'status': 'completed',
                'role': 'assistant',
                'content': [{'type': 'output_text', 'text': text, 'annotations': []}],
            }
        )

    for tool_call in message.get('tool_calls') or []:
        if not isinstance(tool_call, dict):
            continue
        function = tool_call.get('function', {})
        output.append(
            {
                'type': 'function_call',
                'id': tool_call.get('id', ''),
                'call_id': tool_call.get('id', ''),
                'name': function.get('name', ''),
                'arguments': function.get('arguments', '{}'),
                'status': 'completed',
            }
        )

    usage = response.get('usage', {}) if isinstance(response.get('usage'), dict) else {}
    responses_usage = {
        'input_tokens': usage.get('prompt_tokens', 0),
        'output_tokens': usage.get('completion_tokens', 0),
        'total_tokens': usage.get('total_tokens', 0),
    }

    return {
        'id': response.get('id') or f'resp_{hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:24]}',
        'object': 'response',
        'created_at': response.get('created', 0),
        'status': 'completed',
        'error': None,
        'incomplete_details': None,
        'instructions': request_payload.get('instructions'),
        'model': response.get('model') or request_payload.get('model', ''),
        'output': output,
        'output_text': text,
        'parallel_tool_calls': request_payload.get('parallel_tool_calls', True),
        'temperature': request_payload.get('temperature'),
        'tool_choice': request_payload.get('tool_choice', 'auto'),
        'tools': request_payload.get('tools', []),
        'top_p': request_payload.get('top_p'),
        'usage': responses_usage,
    }


async def responses_result_to_sse(response: dict):
    def event(name: str, payload: dict):
        payload = {'type': name, **payload}
        return f"event: {name}\ndata: {json.dumps(payload)}\n\n"

    created = {k: v for k, v in response.items() if k != 'output'}
    created['output'] = []
    yield event('response.created', {'response': created})
    in_progress = {**created, 'status': 'in_progress'}
    yield event('response.in_progress', {'response': in_progress})

    for index, item in enumerate(response.get('output', [])):
        yield event('response.output_item.added', {'output_index': index, 'item': item})
        if item.get('type') == 'message':
            for content_index, part in enumerate(item.get('content', [])):
                if part.get('type') == 'output_text':
                    text = part.get('text', '')
                    base = {
                        'item_id': item.get('id'),
                        'output_index': index,
                        'content_index': content_index,
                    }
                    yield event(
                        'response.content_part.added',
                        {
                            **base,
                            'part': {'type': 'output_text', 'text': '', 'annotations': []},
                        },
                    )
                    yield event('response.output_text.delta', {**base, 'delta': text})
                    yield event('response.output_text.done', {**base, 'text': text})
                    yield event('response.content_part.done', {**base, 'part': part})
        yield event('response.output_item.done', {'output_index': index, 'item': item})

    yield event('response.completed', {'response': response})


def _chat_stream_chunk(
    chunk_id: str,
    model: str,
    created: int,
    delta: dict | None = None,
    finish_reason: str | None = None,
    usage: dict | None = None,
) -> bytes:
    payload = {
        'id': chunk_id,
        'object': 'chat.completion.chunk',
        'created': created,
        'model': model,
        'choices': [
            {
                'index': 0,
                'delta': delta or {},
                'finish_reason': finish_reason,
            }
        ],
    }
    if usage is not None:
        payload['usage'] = usage
    return f'data: {json.dumps(payload)}\n\n'.encode()


def _responses_usage_to_chat_usage(usage: dict | None) -> dict:
    usage = usage or {}
    return {
        'prompt_tokens': usage.get('prompt_tokens', usage.get('input_tokens', 0)),
        'completion_tokens': usage.get('completion_tokens', usage.get('output_tokens', 0)),
        'total_tokens': usage.get('total_tokens', 0),
    }


async def _iter_sse_events_from_aiter(aiter, initial_buffer: bytes = b''):
    buffer = initial_buffer
    event_name = ''
    data_lines: list[str] = []

    while True:
        newline = buffer.find(b'\n')
        if newline < 0:
            try:
                chunk, _ = await aiter.__anext__()
            except StopAsyncIteration:
                break
            if chunk:
                buffer += chunk
            continue

        raw_line = buffer[: newline + 1]
        buffer = buffer[newline + 1 :]
        line = raw_line.rstrip(b'\r\n').decode('utf-8', 'replace')

        if line == '':
            if event_name or data_lines:
                yield event_name, '\n'.join(data_lines)
            event_name = ''
            data_lines = []
        elif line.startswith('event:'):
            event_name = line[6:].strip()
        elif line.startswith('data:'):
            data_lines.append(line[5:].lstrip())

    if buffer:
        line = buffer.rstrip(b'\r\n').decode('utf-8', 'replace')
        if line.startswith('event:'):
            event_name = line[6:].strip()
        elif line.startswith('data:'):
            data_lines.append(line[5:].lstrip())

    if event_name or data_lines:
        yield event_name, '\n'.join(data_lines)


def _is_responses_sse_event(event_name: str, data_text: str) -> bool:
    if event_name.startswith('response.'):
        return True
    if not data_text or data_text == '[DONE]':
        return False
    try:
        payload = json.loads(data_text)
    except json.JSONDecodeError:
        return False
    return isinstance(payload, dict) and str(payload.get('type') or '').startswith('response.')


async def _responses_sse_to_chat_chunks(first_event, events, default_model: str):
    chunk_id = ''
    model = default_model or ''
    created = int(time.time())
    role_sent = False
    finished = False
    emitted_text = False
    saw_tool_call = False
    tool_indexes: dict[str, int] = {}

    async def all_events():
        yield first_event
        async for item in events:
            yield item

    def ensure_role_chunk():
        nonlocal role_sent, chunk_id, model, created
        if role_sent:
            return None
        role_sent = True
        return _chat_stream_chunk(chunk_id or f'chatcmpl-{created}', model, created, {'role': 'assistant'})

    def emit_tool_call_start(item: dict, output_index: int | None):
        nonlocal saw_tool_call
        item_id = str(item.get('id') or item.get('call_id') or output_index or len(tool_indexes))
        if item_id in tool_indexes:
            return None
        tool_index = len(tool_indexes)
        tool_indexes[item_id] = tool_index
        saw_tool_call = True
        return _chat_stream_chunk(
            chunk_id or f'chatcmpl-{created}',
            model,
            created,
            {
                'tool_calls': [
                    {
                        'index': tool_index,
                        'id': item.get('call_id') or item.get('id') or f'call_{tool_index}',
                        'type': 'function',
                        'function': {
                            'name': item.get('name', ''),
                            'arguments': item.get('arguments', '') or '',
                        },
                    }
                ]
            },
        )

    def tool_index_for(payload: dict) -> int:
        key = str(payload.get('item_id') or payload.get('call_id') or payload.get('output_index') or 0)
        if key not in tool_indexes:
            tool_indexes[key] = len(tool_indexes)
        return tool_indexes[key]

    async for event_name, data_text in all_events():
        if data_text == '[DONE]':
            break
        if not data_text:
            continue
        try:
            payload = json.loads(data_text)
        except json.JSONDecodeError:
            continue

        event_type = str(payload.get('type') or event_name)

        if payload.get('error') and not event_type.startswith('response.'):
            yield f"data: {json.dumps({'error': payload['error']})}\n\n".encode()
            yield b'data: [DONE]\n\n'
            return

        if event_type == 'response.created':
            response = payload.get('response') or {}
            chunk_id = response.get('id') or chunk_id or f'chatcmpl-{created}'
            model = response.get('model') or model
            created = int(response.get('created_at') or created)
            role_chunk = ensure_role_chunk()
            if role_chunk:
                yield role_chunk
            continue

        if event_type in {'response.failed', 'response.incomplete'}:
            response = payload.get('response') or {}
            error = response.get('error') or payload.get('error') or {'message': event_type}
            yield f"data: {json.dumps({'error': error})}\n\n".encode()
            yield b'data: [DONE]\n\n'
            return

        if event_type == 'response.output_item.added':
            role_chunk = ensure_role_chunk()
            if role_chunk:
                yield role_chunk
            item = payload.get('item') or {}
            if item.get('type') == 'function_call':
                chunk = emit_tool_call_start(item, payload.get('output_index'))
                if chunk:
                    yield chunk
            continue

        if event_type == 'response.output_text.delta':
            role_chunk = ensure_role_chunk()
            if role_chunk:
                yield role_chunk
            delta = payload.get('delta')
            if delta:
                emitted_text = True
                yield _chat_stream_chunk(chunk_id or f'chatcmpl-{created}', model, created, {'content': str(delta)})
            continue

        if event_type == 'response.function_call_arguments.delta':
            role_chunk = ensure_role_chunk()
            if role_chunk:
                yield role_chunk
            saw_tool_call = True
            yield _chat_stream_chunk(
                chunk_id or f'chatcmpl-{created}',
                model,
                created,
                {
                    'tool_calls': [
                        {
                            'index': tool_index_for(payload),
                            'function': {'arguments': str(payload.get('delta') or '')},
                        }
                    ]
                },
            )
            continue

        if event_type == 'response.output_item.done':
            role_chunk = ensure_role_chunk()
            if role_chunk:
                yield role_chunk
            item = payload.get('item') or {}
            if item.get('type') == 'message' and not emitted_text:
                for part in item.get('content') or []:
                    if isinstance(part, dict) and part.get('type') == 'output_text' and part.get('text'):
                        emitted_text = True
                        yield _chat_stream_chunk(
                            chunk_id or f'chatcmpl-{created}',
                            model,
                            created,
                            {'content': str(part.get('text') or '')},
                        )
            elif item.get('type') == 'function_call':
                chunk = emit_tool_call_start(item, payload.get('output_index'))
                if chunk:
                    yield chunk
            continue

        if event_type == 'response.completed':
            response = payload.get('response') or {}
            chunk_id = response.get('id') or chunk_id or f'chatcmpl-{created}'
            model = response.get('model') or model
            usage = _responses_usage_to_chat_usage(response.get('usage'))
            finish_reason = 'tool_calls' if saw_tool_call else 'stop'
            if response.get('status') == 'incomplete' or response.get('incomplete_details'):
                finish_reason = 'length'
            role_chunk = ensure_role_chunk()
            if role_chunk:
                yield role_chunk
            yield _chat_stream_chunk(chunk_id, model, created, {}, finish_reason, usage)
            yield b'data: [DONE]\n\n'
            finished = True
            break

    if not finished:
        role_chunk = ensure_role_chunk()
        if role_chunk:
            yield role_chunk
        yield _chat_stream_chunk(
            chunk_id or f'chatcmpl-{created}',
            model,
            created,
            {},
            'tool_calls' if saw_tool_call else 'stop',
        )
        yield b'data: [DONE]\n\n'


async def chat_completion_stream_handler(stream: aiohttp.StreamReader, default_model: str = ''):
    aiter = stream.iter_chunks().__aiter__()
    buffer = b''
    pending: list[bytes] = []
    event_name = ''
    data_lines: list[str] = []

    while True:
        newline = buffer.find(b'\n')
        if newline < 0:
            try:
                chunk, _ = await aiter.__anext__()
            except StopAsyncIteration:
                if pending:
                    yield b''.join(pending)
                if buffer:
                    yield buffer
                return
            if chunk:
                buffer += chunk
            continue

        raw_line = buffer[: newline + 1]
        buffer = buffer[newline + 1 :]
        pending.append(raw_line)
        line = raw_line.rstrip(b'\r\n').decode('utf-8', 'replace')

        if line == '':
            data_text = '\n'.join(data_lines)
            if _is_responses_sse_event(event_name, data_text):
                remaining_events = _iter_sse_events_from_aiter(aiter, buffer)
                async for chunk in _responses_sse_to_chat_chunks(
                    (event_name, data_text),
                    remaining_events,
                    default_model,
                ):
                    yield chunk
                return

            yield b''.join(pending)
            if buffer:
                yield buffer
            async for chunk, _ in aiter:
                if chunk:
                    yield chunk
            return

        if line.startswith('event:'):
            event_name = line[6:].strip()
        elif line.startswith('data:'):
            data_lines.append(line[5:].lstrip())


@router.post('/chat/completions')
async def generate_chat_completion(
    request: Request,
    form_data: dict,
    user=Depends(get_verified_user),
):
    # NOTE: We intentionally do NOT use Depends(get_async_session) here.
    # Database operations (get_model_by_id, AccessGrants.has_access) manage their own short-lived sessions.
    # This prevents holding a connection during the entire LLM call (30-60+ seconds),
    # which would exhaust the connection pool under concurrent load.

    # bypass_filter and bypass_system_prompt are read from request.state to prevent
    # external clients from setting them via query parameter. Only internal
    # server-side callers (e.g. utils/chat.py) should set
    # request.state.bypass_filter / request.state.bypass_system_prompt = True.
    bypass_filter = getattr(request.state, 'bypass_filter', False)
    if BYPASS_MODEL_ACCESS_CONTROL:
        bypass_filter = True
    bypass_system_prompt = getattr(request.state, 'bypass_system_prompt', False)

    idx = 0

    payload = {**form_data}
    metadata = payload.pop('metadata', None)

    model_id = form_data.get('model')
    model_info = await Models.get_model_by_id(model_id)

    # Check model info and override the payload
    if model_info:
        if model_info.base_model_id:
            base_model_id = (
                request.base_model_id if hasattr(request, 'base_model_id') else model_info.base_model_id
            )  # Use request's base_model_id if available
            payload['model'] = base_model_id
            model_id = base_model_id

        params = model_info.params.model_dump()

        if params:
            system = params.pop('system', None)

            payload = apply_model_params_to_body_openai(params, payload)
            if not bypass_system_prompt:
                payload = await apply_system_prompt_to_body(system, payload, metadata, user)

        await check_model_access(user, model_info, bypass_filter)
    else:
        await check_model_access(user, None, bypass_filter)

    # Check if model is already in app state cache to avoid expensive get_all_models() call
    models = request.app.state.OPENAI_MODELS
    if not models or model_id not in models:
        await get_all_models(request, user=user)
        models = request.app.state.OPENAI_MODELS
    model = models.get(model_id)

    if model:
        idx = model['urlIdx']
    else:
        raise HTTPException(
            status_code=404,
            detail=ERROR_MESSAGES.MODEL_NOT_FOUND(),
        )

    url, key, api_config = await get_openai_connection(idx)

    prefix_id = api_config.get('prefix_id', None)
    if prefix_id:
        payload['model'] = payload['model'].replace(f'{prefix_id}.', '')

    # Add user info to the payload if the model is a pipeline
    if 'pipeline' in model and model.get('pipeline'):
        payload['user'] = {
            'name': user.name,
            'id': user.id,
            'email': user.email,
            'role': user.role,
        }

    # Check if model is a reasoning model that needs special handling
    if is_openai_new_model(payload['model']):
        payload = openai_reasoning_model_handler(payload)
    elif 'api.openai.com' not in url:
        # Remove "max_completion_tokens" from the payload for backward compatibility
        if 'max_completion_tokens' in payload:
            payload['max_tokens'] = payload['max_completion_tokens']
            del payload['max_completion_tokens']

    if 'max_tokens' in payload and 'max_completion_tokens' in payload:
        del payload['max_tokens']

    # Convert the modified body back to JSON
    if 'logit_bias' in payload and payload['logit_bias']:
        logit_bias = convert_logit_bias_input_to_json(payload['logit_bias'])

        if logit_bias:
            payload['logit_bias'] = json.loads(logit_bias)

    headers, cookies = await get_headers_and_cookies(request, url, key, api_config, metadata, user=user)

    provider_hint = _get_provider_hint(url, api_config)
    is_responses = api_config.get('api_type') == 'responses'
    chat_fallback_payload = {**payload}
    native_response_converter = None

    if _uses_native_anthropic_api(url, api_config) and not (api_config.get('azure') or api_config.get('provider') == 'azure'):
        is_responses = False
        payload = _convert_openai_to_anthropic_payload(payload)
        request_url = _get_anthropic_messages_url(url)
        headers = {k: v for k, v in headers.items() if k.lower() != 'authorization'}
        headers['x-api-key'] = key
        headers['anthropic-version'] = api_config.get('anthropic_version', '2023-06-01')
        if api_config.get('anthropic_beta'):
            headers['anthropic-beta'] = api_config['anthropic_beta']
        native_response_converter = lambda response: _convert_anthropic_to_openai_response(response, payload.get('model', ''))
    elif _uses_native_gemini_api(url, api_config) and not (api_config.get('azure') or api_config.get('provider') == 'azure'):
        is_responses = False
        model_for_response = payload.get('model', '')
        payload = _convert_openai_to_gemini_payload(payload)
        request_url = _get_gemini_generate_url(url, model_for_response)
        headers = {k: v for k, v in headers.items() if k.lower() != 'authorization'}
        headers['x-goog-api-key'] = key
        native_response_converter = lambda response: _convert_gemini_to_openai_response(response, model_for_response)
    elif api_config.get('azure') or api_config.get('provider') == 'azure':
        # Only set api-key header if not using Azure Entra ID authentication
        auth_type = api_config.get('auth_type', 'bearer')
        if auth_type not in ('azure_ad', 'microsoft_entra_id'):
            headers['api-key'] = key

        # Azure v1 format: base URL already ends with /openai/v1,
        # model stays in the payload, no deployment URL rewriting.
        is_azure_v1 = bool(re.search(r'/openai/v1(?:/|$)', url))

        if is_azure_v1:
            if is_responses:
                payload = convert_to_responses_payload(payload)
                request_url = f'{url.rstrip("/")}/responses'
            else:
                request_url = f'{url.rstrip("/")}/chat/completions'
        else:
            api_version = api_config.get('api_version', '2023-03-15-preview')
            request_url, payload = convert_to_azure_payload(url, payload, api_version)
            headers['api-version'] = api_version

            if is_responses:
                payload = convert_to_responses_payload(payload)
                request_url = f'{request_url}/responses?api-version={api_version}'
            else:
                request_url = f'{request_url}/chat/completions?api-version={api_version}'
    else:
        if is_responses:
            payload = convert_to_responses_payload(payload)
            request_url = _get_openai_endpoint_url(url, 'responses', api_config)
        else:
            request_url = _get_openai_endpoint_url(url, 'chat/completions', api_config)
    requested_model = chat_fallback_payload.get('model') or payload.get('model')
    # For Chat Completions, strip image parts from multimodal tool messages
    # (Chat Completions doesn't support images in tool content).
    if not is_responses and 'messages' in payload:
        for message in payload['messages']:
            if message.get('role') == 'tool' and isinstance(message.get('content'), list):
                message['content'] = ''.join(
                    part.get('text', '') for part in message['content'] if part.get('type') in ('input_text', 'text')
                )

    payload = json.dumps(payload)

    r = None
    streaming = False
    response = None

    try:
        session = await get_session()

        r = await session.request(
            method='POST',
            url=request_url,
            data=payload,
            headers=headers,
            cookies=cookies,
            ssl=AIOHTTP_CLIENT_SESSION_SSL,
            timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT),
        )

        # Check if response is SSE
        if 'text/event-stream' in r.headers.get('Content-Type', ''):
            # If the provider returned an error status with SSE content-type,
            # read the body and return a proper error response instead of
            # streaming the error back (which hides the error from logs).
            if r.status >= 400:
                error_body = await r.text()
                log.error(
                    'Provider returned HTTP %d with SSE content-type: %s',
                    r.status,
                    error_body[:1000],
                )
                try:
                    error_json = json.loads(error_body)
                    await publish_model_provider_request_failed(
                        request,
                        actor=user,
                        provider='openai-compatible',
                        base_url=url,
                        api_key=key,
                        status=r.status,
                        requested_model=requested_model,
                        upstream_error=error_json,
                    )
                    return JSONResponse(status_code=r.status, content=error_json)
                except json.JSONDecodeError:
                    await publish_model_provider_request_failed(
                        request,
                        actor=user,
                        provider='openai-compatible',
                        base_url=url,
                        api_key=key,
                        status=r.status,
                        requested_model=requested_model,
                        upstream_error=error_body,
                    )
                    return JSONResponse(
                        status_code=r.status,
                        content={'error': {'message': error_body, 'code': r.status}},
                    )

            streaming = True
            return StreamingResponse(
                stream_wrapper(
                    r,
                    content_handler=lambda stream: chat_completion_stream_handler(stream, requested_model or ''),
                ),
                status_code=r.status,
                headers=_clean_proxy_headers(r.headers),
            )
        else:
            try:
                response = await r.json()
            except Exception as e:
                log.error(e)
                response = await r.text()

            if is_responses and (
                r.status in {404, 405}
                or 'text/html' in r.headers.get('Content-Type', '')
                or (r.status == 200 and isinstance(response, str))
            ):
                log.warning(
                    'Responses endpoint %s did not return a usable JSON response; retrying chat/completions',
                    request_url,
                )
                await cleanup_response(r)

                is_responses = False
                request_url = _get_openai_endpoint_url(url, 'chat/completions', api_config)
                payload = json.dumps(chat_fallback_payload)

                r = await session.request(
                    method='POST',
                    url=request_url,
                    data=payload,
                    headers=headers,
                    cookies=cookies,
                    ssl=AIOHTTP_CLIENT_SESSION_SSL,
                    timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT),
                )

                if 'text/event-stream' in r.headers.get('Content-Type', ''):
                    if r.status >= 400:
                        error_body = await r.text()
                        await publish_model_provider_request_failed(
                            request,
                            actor=user,
                            provider='openai-compatible',
                            base_url=url,
                            api_key=key,
                            status=r.status,
                            requested_model=requested_model,
                            upstream_error=error_body,
                        )
                        return JSONResponse(
                            status_code=r.status,
                            content={'error': {'message': error_body, 'code': r.status}},
                        )

                    streaming = True
                    return StreamingResponse(
                        stream_wrapper(
                            r,
                            content_handler=lambda stream: chat_completion_stream_handler(stream, requested_model or ''),
                        ),
                        status_code=r.status,
                        headers=_clean_proxy_headers(r.headers),
                    )

                try:
                    response = await r.json()
                except Exception as e:
                    log.error(e)
                    response = await r.text()

            if r.status >= 400:
                await publish_model_provider_request_failed(
                    request,
                    actor=user,
                    provider='openai-compatible',
                    base_url=url,
                    api_key=key,
                    status=r.status,
                    requested_model=requested_model,
                    upstream_error=response,
                )
                if isinstance(response, (dict, list)):
                    return JSONResponse(status_code=r.status, content=response)
                else:
                    return PlainTextResponse(status_code=r.status, content=response)

            # Convert Responses API result to simple format
            if is_responses and isinstance(response, dict):
                response = convert_responses_result(response)
            elif native_response_converter and isinstance(response, dict):
                response = native_response_converter(response)

            return response
    except Exception as e:
        log.exception(e)

        raise HTTPException(
            status_code=r.status if r else 500,
            detail=ERROR_MESSAGES.SERVER_CONNECTION_ERROR,
        )
    finally:
        if not streaming:
            await cleanup_response(r)


async def embeddings(request: Request, form_data: dict, user):
    """
    Calls the embeddings endpoint for OpenAI-compatible providers.

    Args:
        request (Request): The FastAPI request context.
        form_data (dict): OpenAI-compatible embeddings payload.
        user (UserModel): The authenticated user.

    Returns:
        dict: OpenAI-compatible embeddings response.
    """
    idx = 0
    # Prepare payload/body
    body = json.dumps(form_data)
    # Find correct backend url/key based on model
    model_id = form_data.get('model')
    # Check if model is already in app state cache to avoid expensive get_all_models() call
    models = request.app.state.OPENAI_MODELS
    if not models or model_id not in models:
        await get_all_models(request, user=user)
        models = request.app.state.OPENAI_MODELS
    if model_id in models:
        idx = models[model_id]['urlIdx']

    url, key, api_config = await get_openai_connection(idx)

    r = None
    streaming = False

    headers, cookies = await get_headers_and_cookies(request, url, key, api_config, user=user)

    if api_config.get('azure') or api_config.get('provider') == 'azure':
        # Only set api-key header if not using Azure Entra ID authentication
        auth_type = api_config.get('auth_type', 'bearer')
        if auth_type not in ('azure_ad', 'microsoft_entra_id'):
            headers['api-key'] = key

        # Azure v1 format: base URL already ends with /openai/v1,
        # model stays in the payload, no deployment URL rewriting.
        is_azure_v1 = bool(re.search(r'/openai/v1(?:/|$)', url))

        if is_azure_v1:
            embeddings_url = f'{url.rstrip("/")}/embeddings'
        else:
            api_version = api_config.get('api_version', '2023-03-15-preview')
            model = _sanitize_model_for_url(form_data.get('model', ''))
            embeddings_url = f'{url}/openai/deployments/{model}/embeddings?api-version={api_version}'
            headers['api-version'] = api_version
    else:
        embeddings_url = f'{url}/embeddings'
    requested_model = form_data.get('model')

    try:
        session = await get_session()
        r = await session.request(
            method='POST',
            url=embeddings_url,
            data=body,
            headers=headers,
            cookies=cookies,
            timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT),
            ssl=AIOHTTP_CLIENT_SESSION_SSL,
        )

        if 'text/event-stream' in r.headers.get('Content-Type', ''):
            streaming = True
            return StreamingResponse(
                stream_wrapper(r),
                status_code=r.status,
                headers=_clean_proxy_headers(r.headers),
            )
        else:
            try:
                response_data = await r.json()
            except Exception:
                response_data = await r.text()

            if r.status >= 400:
                await publish_model_provider_request_failed(
                    request,
                    actor=user,
                    provider='openai-compatible',
                    base_url=url,
                    api_key=key,
                    status=r.status,
                    requested_model=requested_model,
                    upstream_error=response_data,
                )
                if isinstance(response_data, (dict, list)):
                    return JSONResponse(status_code=r.status, content=response_data)
                else:
                    return PlainTextResponse(status_code=r.status, content=response_data)

            return response_data
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=r.status if r else 500,
            detail=ERROR_MESSAGES.SERVER_CONNECTION_ERROR,
        )
    finally:
        if not streaming:
            await cleanup_response(r)


class ResponsesForm(BaseModel):
    model_config = ConfigDict(extra='allow')

    model: str
    input: list | str | None = None
    instructions: str | None = None
    stream: bool | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    top_p: float | None = None
    tools: list | None = None
    tool_choice: str | dict | None = None
    text: dict | None = None
    truncation: str | None = None
    metadata: dict | None = None
    store: bool | None = None
    reasoning: dict | None = None
    previous_response_id: str | None = None


@router.post('/responses')
async def responses(
    request: Request,
    form_data: ResponsesForm,
    user=Depends(get_verified_user),
):
    """
    Forward requests to the OpenAI Responses API endpoint.
    Routes to the correct upstream backend based on the model field.
    """
    payload = form_data.model_dump(exclude_none=True)

    idx = 0
    model_id = form_data.model

    # Enforce per-model access control
    await check_model_access(user, await Models.get_model_by_id(model_id), BYPASS_MODEL_ACCESS_CONTROL)

    wants_stream = bool(payload.get('stream'))
    chat_payload = convert_responses_payload_to_chat(payload)
    # Most configured routers/providers are Chat Completions compatible even
    # when the client speaks Responses. Do the provider call non-streaming, then
    # emit a minimal Responses SSE stream when the client requested streaming.
    chat_payload['stream'] = False
    chat_response = await generate_chat_completion(request, chat_payload, user)

    if isinstance(chat_response, (JSONResponse, PlainTextResponse, StreamingResponse)):
        return chat_response

    responses_response = convert_chat_completion_to_responses_result(chat_response, payload)
    if wants_stream:
        return StreamingResponse(
            responses_result_to_sse(responses_response),
            media_type='text/event-stream',
        )
    return responses_response

    body = json.dumps(payload)

    if model_id:
        models = request.app.state.OPENAI_MODELS
        if not models or model_id not in models:
            await get_all_models(request, user=user)
            models = request.app.state.OPENAI_MODELS
        if model_id in models:
            idx = models[model_id]['urlIdx']

    url, key, api_config = await get_openai_connection(idx)

    r = None
    streaming = False

    try:
        headers, cookies = await get_headers_and_cookies(request, url, key, api_config, user=user)

        if api_config.get('azure') or api_config.get('provider') == 'azure':
            auth_type = api_config.get('auth_type', 'bearer')
            if auth_type not in ('azure_ad', 'microsoft_entra_id'):
                headers['api-key'] = key

            is_azure_v1 = bool(re.search(r'/openai/v1(?:/|$)', url))

            if is_azure_v1:
                request_url = f'{url.rstrip("/")}/responses'
            else:
                api_version = api_config.get('api_version', '2023-03-15-preview')
                headers['api-version'] = api_version
                model = _sanitize_model_for_url(payload.get('model', ''))
                request_url = f'{url}/openai/deployments/{model}/responses?api-version={api_version}'
        else:
            request_url = _get_openai_endpoint_url(url, 'responses', api_config)

        session = await get_session()
        r = await session.request(
            method='POST',
            url=request_url,
            data=body,
            headers=headers,
            cookies=cookies,
            ssl=AIOHTTP_CLIENT_SESSION_SSL,
            timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT),
        )

        # Check if response is SSE
        if 'text/event-stream' in r.headers.get('Content-Type', ''):
            streaming = True
            return StreamingResponse(
                stream_wrapper(r),
                status_code=r.status,
                headers=_clean_proxy_headers(r.headers),
            )
        else:
            try:
                response_data = await r.json()
            except Exception:
                response_data = await r.text()

            if r.status >= 400:
                await publish_model_provider_request_failed(
                    request,
                    actor=user,
                    provider='openai-compatible',
                    base_url=url,
                    api_key=key,
                    status=r.status,
                    requested_model=payload.get('model'),
                    upstream_error=response_data,
                )
                if isinstance(response_data, (dict, list)):
                    return JSONResponse(status_code=r.status, content=response_data)
                else:
                    return PlainTextResponse(status_code=r.status, content=response_data)

            return response_data

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=r.status if r else 500,
            detail=ERROR_MESSAGES.SERVER_CONNECTION_ERROR,
        )
    finally:
        if not streaming:
            await cleanup_response(r)


@router.api_route('/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def proxy(path: str, request: Request, user=Depends(get_verified_user)):
    """
    Deprecated: proxy all requests to OpenAI API.
    Disabled by default. Set ENABLE_OPENAI_API_PASSTHROUGH=True to enable.
    """

    if not ENABLE_OPENAI_API_PASSTHROUGH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Direct API passthrough is disabled. Set ENABLE_OPENAI_API_PASSTHROUGH=True to enable.',
        )

    body = await request.body()

    # Parse JSON body to resolve model-based routing
    payload = None
    if body:
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            payload = None

    idx = 0
    model_id = payload.get('model') if isinstance(payload, dict) else None
    if model_id:
        models = request.app.state.OPENAI_MODELS
        if not models or model_id not in models:
            await get_all_models(request, user=user)
            models = request.app.state.OPENAI_MODELS
        if model_id in models:
            idx = models[model_id]['urlIdx']

    url, key, api_config = await get_openai_connection(idx)
    base_url = url

    r = None
    streaming = False

    try:
        headers, cookies = await get_headers_and_cookies(request, url, key, api_config, user=user)

        if api_config.get('azure') or api_config.get('provider') == 'azure':
            # Only set api-key header if not using Azure Entra ID authentication
            auth_type = api_config.get('auth_type', 'bearer')
            if auth_type not in ('azure_ad', 'microsoft_entra_id'):
                headers['api-key'] = key

            is_azure_v1 = bool(re.search(r'/openai/v1(?:/|$)', url))

            if is_azure_v1:
                qs = request.url.query
                request_url = f'{url.rstrip("/")}/{path}' + (f'?{qs}' if qs else '')
            else:
                api_version = api_config.get('api_version', '2023-03-15-preview')
                headers['api-version'] = api_version

                payload = json.loads(body)
                url, payload = convert_to_azure_payload(url, payload, api_version)
                body = json.dumps(payload).encode()

                request_url = f'{url}/{path}?api-version={api_version}'
        else:
            request_url = f'{url}/{path}'

        session = await get_session()
        r = await session.request(
            method=request.method,
            url=request_url,
            data=body,
            headers=headers,
            cookies=cookies,
            ssl=AIOHTTP_CLIENT_SESSION_SSL,
            timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT),
        )

        # Check if response is SSE
        if 'text/event-stream' in r.headers.get('Content-Type', ''):
            streaming = True
            return StreamingResponse(
                stream_wrapper(r),
                status_code=r.status,
                headers=_clean_proxy_headers(r.headers),
            )
        else:
            try:
                response_data = await r.json()
            except Exception:
                response_data = await r.text()

            if r.status >= 400:
                await publish_model_provider_request_failed(
                    request,
                    actor=user,
                    provider='openai-compatible',
                    base_url=base_url,
                    api_key=key,
                    status=r.status,
                    requested_model=model_id,
                    upstream_error=response_data,
                )
                if isinstance(response_data, (dict, list)):
                    return JSONResponse(status_code=r.status, content=response_data)
                else:
                    return PlainTextResponse(status_code=r.status, content=response_data)

            return response_data

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=r.status if r else 500,
            detail='ZaneLLM: Server Connection Error',
        )
    finally:
        if not streaming:
            await cleanup_response(r)
