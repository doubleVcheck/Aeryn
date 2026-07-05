#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DATA_DIR", str(BACKEND_DIR / "open_webui" / "data"))

from open_webui.models.config import Config  # noqa: E402
from open_webui.models.users import Users  # noqa: E402


def _same_base(left: str, right: str) -> bool:
    return left.rstrip("/") == right.rstrip("/")


def _is_zane_artemisia_config(config: dict[str, object], base_url: str, upstream_base: str) -> bool:
    provider = str(config.get("provider") or "").lower()
    tags = config.get("tags") if isinstance(config.get("tags"), list) else []
    tag_text = " ".join(str(tag).lower() for tag in tags)
    return provider == "artemisiahub" or "zanecode" in tag_text or (
        _same_base(base_url, upstream_base) and "artemisia" in f"{provider} {tag_text} {base_url.lower()}"
    )


def _provider_rows(token: str, upstream_base: str) -> list[dict[str, object]]:
    raw = os.environ.get("ZANE_BOOTSTRAP_PROVIDERS", "").strip()
    providers: list[dict[str, object]] = []
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                providers = [item for item in parsed if isinstance(item, dict) and str(item.get("apiKey") or "").strip()]
        except json.JSONDecodeError:
            providers = []

    if not providers:
        providers = [{"apiKey": token, "group": "", "tokenName": "artemisiahub", "tokenId": ""}]

    rows: list[dict[str, object]] = []
    for provider in providers:
        group = str(provider.get("group") or "").strip()
        rows.append(
            {
                "base_url": upstream_base,
                "key": str(provider.get("apiKey") or "").strip(),
                "group": group,
                "tokenName": str(provider.get("tokenName") or "").strip(),
                "tokenId": str(provider.get("tokenId") or "").strip(),
            }
        )
    return rows


async def _ensure_local_api_key() -> dict[str, object]:
    user = await Users.get_super_admin_user()
    if user is None:
        users = await Users.get_users(skip=0, limit=1)
        user_list = users.get("users") if isinstance(users, dict) else []
        user = user_list[0] if user_list else None
    if user is None:
        return {"ok": False}

    api_key = await Users.get_user_api_key_by_id(user.id)
    created = False
    if not api_key:
        api_key = f"sk-{uuid.uuid4().hex}"
        await Users.update_user_api_key_by_id(user.id, api_key)
        created = True

    return {
        "ok": True,
        "user_id": user.id,
        "api_key": api_key,
        "created": created,
    }


async def main() -> int:
    token = os.environ.get("ZANE_BOOTSTRAP_TOKEN", "").strip()
    upstream_base = os.environ.get("ZANE_BOOTSTRAP_UPSTREAM_BASE", "https://artemisiahub.com/v1").strip().rstrip("/")
    model = os.environ.get("ZANE_BOOTSTRAP_MODEL", "").strip()

    if not token:
        print("missing ZANE_BOOTSTRAP_TOKEN", file=sys.stderr)
        return 2

    values = await Config.get_many(
        "openai.api_base_urls",
        "openai.api_keys",
        "openai.api_configs",
        "ui.default_models",
    )

    base_urls = list(values.get("openai.api_base_urls") or [])
    api_keys = list(values.get("openai.api_keys") or [])
    api_configs = dict(values.get("openai.api_configs") or {})

    next_base_urls: list[str] = []
    next_api_keys: list[str] = []
    next_api_configs: dict[str, dict[str, object]] = {}

    for idx, base_url in enumerate(base_urls):
        config = api_configs.get(str(idx), {})
        if not isinstance(config, dict):
            config = {}
        if _is_zane_artemisia_config(config, str(base_url), upstream_base):
            continue
        next_idx = len(next_base_urls)
        next_base_urls.append(str(base_url))
        next_api_keys.append(api_keys[idx] if idx < len(api_keys) else "")
        next_api_configs[str(next_idx)] = config

    for row in _provider_rows(token, upstream_base):
        next_idx = len(next_base_urls)
        group = str(row.get("group") or "")
        next_base_urls.append(str(row["base_url"]))
        next_api_keys.append(str(row["key"]))
        next_api_configs[str(next_idx)] = {
            "enable": True,
            "connection_type": "external",
            "provider": "artemisiahub",
            "tags": ["artemisiahub", "zanecode", group or "default"],
            "prefix_id": "",
            "model_ids": [],
            "api_type": "chat_completions",
            "auth_type": "bearer",
            "group": group,
            "token_name": str(row.get("tokenName") or ""),
            "token_id": str(row.get("tokenId") or ""),
        }

    updates = {
        "openai.enable": True,
        "openai.api_base_urls": next_base_urls,
        "openai.api_keys": next_api_keys,
        "openai.api_configs": next_api_configs,
        "auth.enable_api_keys": True,
        "auth.api_key.endpoint_restrictions": False,
        "models.base_models_cache": False,
    }

    if model:
        updates["ui.default_models"] = model

    await Config.upsert(updates)
    local_api_key = await _ensure_local_api_key()

    print(
        json.dumps(
            {
                "ok": True,
                "provider_count": len(_provider_rows(token, upstream_base)),
                "upstream_base": upstream_base,
                "model": model,
                "local_api_key": local_api_key.get("api_key") if local_api_key.get("ok") else "",
                "local_api_key_created": bool(local_api_key.get("created")),
                "local_user_id": local_api_key.get("user_id", ""),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
