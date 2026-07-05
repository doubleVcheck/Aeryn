from __future__ import annotations

import logging
import os
from typing import Any
from urllib.parse import urlparse, urlunparse

import aiohttp
from fastapi import APIRouter, HTTPException, Request
from open_webui.env import AIOHTTP_CLIENT_SESSION_SSL
from open_webui.models.config import Config
from pydantic import BaseModel

log = logging.getLogger(__name__)

router = APIRouter()


class ZaneProviderUsage(BaseModel):
    provider: str
    base_url: str
    usage_url: str
    usage: dict[str, Any]


class ZaneAccountUsage(BaseModel):
    base_url: str
    user_id: str | None = None
    profile_url: str | None = None
    token_list_url: str | None = None
    models_url: str | None = None
    profile: dict[str, Any] | None = None
    tokens: list[dict[str, Any]] | None = None
    models: Any | None = None


class ZaneUsageResponse(BaseModel):
    configured: bool
    account: ZaneAccountUsage | None = None
    provider: ZaneProviderUsage | None = None
    message: str | None = None


def _is_local_request(request: Request) -> bool:
    host = request.client.host if request.client else ""
    return host in {"127.0.0.1", "::1", "localhost"}


def _usage_root_from_base_url(base_url: str) -> str:
    parsed = urlparse((base_url or "").strip())
    path = parsed.path.rstrip("/")
    for suffix in ("/openai/v1", "/compatible-mode/v1", "/api/v1", "/v1"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    return urlunparse(parsed._replace(path=path or "", params="", query="", fragment="")).rstrip("/")


def _usage_url(base_url: str) -> str:
    return f"{_usage_root_from_base_url(base_url)}/api/usage/token"


def _env_first(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def _account_headers(access_token: str, user_id: str = "") -> dict[str, str]:
    token = access_token.removeprefix("Bearer ").strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if user_id:
        headers["New-Api-User"] = user_id
    return headers


def _provider_name(config: dict[str, Any], base_url: str) -> str:
    value = config.get("provider")
    if isinstance(value, str) and value.strip():
        return value.strip()
    if "artemisiahub" in base_url.lower():
        return "artemisiahub"
    return "openai-compatible"


def _matches_artemisia_provider(config: dict[str, Any], base_url: str) -> bool:
    provider = _provider_name(config, base_url).lower()
    tags = config.get("tags") if isinstance(config.get("tags"), list) else []
    tag_text = " ".join(str(tag).lower() for tag in tags)
    haystack = f"{provider} {base_url.lower()} {tag_text}"
    return "artemisia" in haystack or "zanecode" in haystack


def _find_usage_provider(values: dict[str, Any]) -> tuple[str, str, dict[str, Any]] | None:
    base_urls = values.get("openai.api_base_urls") or []
    api_keys = values.get("openai.api_keys") or []
    api_configs = values.get("openai.api_configs") or {}
    candidates: list[tuple[int, str, str, dict[str, Any]]] = []

    for index, base_url in enumerate(base_urls):
        if not isinstance(base_url, str) or not base_url.strip():
            continue
        key = api_keys[index] if index < len(api_keys) else ""
        if not isinstance(key, str) or not key:
            continue
        config = api_configs.get(str(index), {}) if isinstance(api_configs, dict) else {}
        if not isinstance(config, dict):
            config = {}
        priority = 0 if _matches_artemisia_provider(config, base_url) else 1
        candidates.append((priority, base_url.strip(), key, config))

    if not candidates:
        return None

    _, base_url, key, config = sorted(candidates, key=lambda item: item[0])[0]
    return base_url, key, config


def _sanitize_usage(value: Any) -> Any:
    if isinstance(value, dict):
        blocked = {"api_key", "apikey", "key", "access_key", "secret", "password", "authorization"}
        return {
            key: _sanitize_usage(item)
            for key, item in value.items()
            if key.lower().replace("-", "_") not in blocked
        }
    if isinstance(value, list):
        return [_sanitize_usage(item) for item in value]
    return value


def _unwrap_data(value: Any) -> Any:
    if isinstance(value, dict) and "data" in value:
        return value["data"]
    return value


def _list_from_body(value: Any) -> list[dict[str, Any]]:
    data = _unwrap_data(value)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("items", "tokens", "records", "list", "rows", "data"):
            items = data.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("items", "tokens", "records", "list", "rows"):
            items = value.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
    return []


async def _fetch_json(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict[str, str],
) -> tuple[int, Any]:
    async with session.get(url, headers=headers, ssl=AIOHTTP_CLIENT_SESSION_SSL) as response:
        body = await response.json(content_type=None)
        return response.status, body


async def _fetch_account_usage(
    session: aiohttp.ClientSession,
    base_url: str,
    access_token: str,
    user_id: str,
) -> ZaneAccountUsage | None:
    root = _usage_root_from_base_url(base_url)
    headers = _account_headers(access_token, user_id)
    profile_url = f"{root}/api/user/self"
    token_urls = [
        f"{root}/api/token/?p=1&size=200",
        f"{root}/api/token/?p=0&page_size=200",
        f"{root}/api/token/",
    ]
    models_url = f"{root}/api/models"

    profile: Any | None = None
    tokens: list[dict[str, Any]] | None = None
    models: Any | None = None
    token_list_url: str | None = None

    try:
        status, body = await _fetch_json(session, profile_url, headers)
        if status < 400:
            profile = _sanitize_usage(body) if isinstance(body, dict) else {"data": body}
    except Exception:
        log.debug("Zane usage profile endpoint failed", exc_info=True)

    for url in token_urls:
        try:
            status, body = await _fetch_json(session, url, headers)
            if status < 400:
                tokens = [_sanitize_usage(item) for item in _list_from_body(body)]
                token_list_url = url
                break
        except Exception:
            log.debug("Zane usage token-list endpoint failed: %s", url, exc_info=True)

    try:
        status, body = await _fetch_json(session, models_url, headers)
        if status < 400:
            models = _sanitize_usage(body)
    except Exception:
        log.debug("Zane usage models endpoint failed", exc_info=True)

    if profile is None and tokens is None and models is None:
        return None

    return ZaneAccountUsage(
        base_url=root,
        user_id=user_id or None,
        profile_url=profile_url if profile is not None else None,
        token_list_url=token_list_url,
        models_url=models_url if models is not None else None,
        profile=profile,
        tokens=tokens,
        models=models,
    )


@router.get("/usage", response_model=ZaneUsageResponse)
async def get_zane_usage(request: Request):
    if not _is_local_request(request):
        raise HTTPException(status_code=403, detail="Zane usage is only available from localhost.")

    values = await Config.get_many("openai.api_base_urls", "openai.api_keys", "openai.api_configs")
    selected = _find_usage_provider(values)
    timeout = aiohttp.ClientTimeout(total=20)
    access_token = _env_first("ZANE_ARTEMISIA_ACCESS_TOKEN", "NEWAPI_ACCESS_TOKEN")
    user_id = _env_first("ZANE_NEWAPI_USER_ID", "NEWAPI_USER_ID")
    account_base_url = _env_first("NEWAPI_BASE_URL", "ZANE_NEWAPI_BASE_URL")
    if not account_base_url and selected:
        account_base_url = selected[0]

    account: ZaneAccountUsage | None = None
    provider: ZaneProviderUsage | None = None
    try:
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            if access_token and account_base_url:
                account = await _fetch_account_usage(session, account_base_url, access_token, user_id)

            if selected:
                base_url, key, config = selected
                usage_url = _usage_url(base_url)
                async with session.get(
                    usage_url,
                    headers={"Authorization": f"Bearer {key}"},
                    ssl=AIOHTTP_CLIENT_SESSION_SSL,
                ) as response:
                    body = await response.json(content_type=None)
                    if response.status >= 400:
                        if not account:
                            detail = body.get("error", body) if isinstance(body, dict) else body
                            raise HTTPException(status_code=response.status, detail=detail)
                    else:
                        provider = ZaneProviderUsage(
                            provider=_provider_name(config, base_url),
                            base_url=base_url,
                            usage_url=usage_url,
                            usage=_sanitize_usage(body) if isinstance(body, dict) else {"data": body},
                        )
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("Failed to fetch Zane usage")
        raise HTTPException(status_code=502, detail=f"Could not fetch upstream usage: {exc}") from exc

    if not account and not provider:
        return ZaneUsageResponse(
            configured=False,
            message="No artemisiahub access token or provider token is configured yet. Run `zanecode` or `zane setup` first.",
        )

    return ZaneUsageResponse(
        configured=True,
        account=account,
        provider=provider,
    )
