#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DATA_DIR", str(BACKEND_DIR / "open_webui" / "data"))

from open_webui.models.config import Config  # noqa: E402


async def main() -> int:
    upstream = os.environ.get("ZANE_BOOTSTRAP_UPSTREAM_BASE", "https://artemisiahub.com/v1").strip().rstrip("/")
    # image endpoint root should be without trailing /v1 sometimes; OpenWebUI appends /images/generations
    # IMAGES_OPENAI_API_BASE_URL should be like https://artemisiahub.com/v1
    token = (
        os.environ.get("ZANE_BOOTSTRAP_TOKEN")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("ZANELLM_API_KEY")
        or ""
    ).strip()
    model = os.environ.get("ZANE_IMAGE_MODEL", "gpt-image-2").strip() or "gpt-image-2"
    size = os.environ.get("ZANE_IMAGE_SIZE", "1024x1024").strip() or "1024x1024"

    if not token:
        print("missing token", file=sys.stderr)
        return 2

    # gpt-image* models match OpenWebUI's IMAGE_URL_RESPONSE_MODELS_REGEX (^gpt-image),
    # so it omits response_format and Artemisia returns b64_json by default.
    # Do NOT force response_format=url: Artemisia image CDN URLs often require the
    # same Bearer key and otherwise return HTML, which breaks Aeryn's image fetch.
    updates = {
        "image_generation.enable": True,
        "image_generation.prompt.enable": True,
        "image_generation.engine": "openai",
        "image_generation.model": model,
        "image_generation.size": size,
        "image_generation.openai.api_base_url": upstream,
        "image_generation.openai.api_key": token,
        "image_generation.openai.params": {},
        "images.edit.enable": True,
        "images.edit.engine": "openai",
        "images.edit.model": model,
        "images.edit.size": size,
        "images.edit.openai.api_base_url": upstream,
        "images.edit.openai.api_key": token,
    }
    await Config.upsert(updates)
    print(json.dumps({"ok": True, "updates": {k: ("***" if "key" in k else v) for k, v in updates.items()}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
