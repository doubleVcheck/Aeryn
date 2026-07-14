"""Chat-side media bridge for Artemisia image/video models.

Aeryn chat always posts to /api/chat/completions. Some Artemisia models are not
chat-completions models:

- gpt-image-*  -> /v1/images/generations
- seedance-*   -> /v1/video/generations (+ poll)

This module converts those chat requests into the correct media flow and returns
an OpenAI-style chat.completion payload so the existing chat UI can render media.
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
import mimetypes
import re
import time
from pathlib import Path
from typing import Any, Awaitable, Callable

import aiohttp
from fastapi import HTTPException, Request, UploadFile, status

from open_webui.env import AIOHTTP_CLIENT_SESSION_SSL, AIOHTTP_CLIENT_TIMEOUT
from open_webui.models.chats import Chats
from open_webui.models.config import Config
from open_webui.routers.files import get_file_content_by_id, upload_file_handler
from open_webui.routers.images import CreateImageForm, EditImageForm, image_edits, image_generations, upload_image
from open_webui.utils.session_pool import get_session
from starlette.responses import FileResponse

log = logging.getLogger(__name__)

IMAGE_MODEL_RE = re.compile(r"^(gpt-image|dall-e|imagen)", re.I)
VIDEO_MODEL_RE = re.compile(r"^(seedance|sora|kling|runway|luma)", re.I)
IMAGE_CONTENT_RE = re.compile(r"^image/", re.I)
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FILE_URL_RE = re.compile(r"/api/v1/files/([0-9a-fA-F-]{16,})")
FILE_ID_RE = re.compile(r"^[0-9a-fA-F-]{16,}$")
FOLLOWUP_HINT_RE = re.compile(
    r"\b(also|again|same|keep|change|edit|modify|instead|make|turn|cover|add|remove|more|less|"
    r"bigger|smaller|brighter|darker|but|now|please|update|revise|fix|eyes|clothes|background)\b",
    re.I,
)


def is_media_chat_model(model_id: str | None) -> bool:
    model_id = (model_id or "").strip()
    if not model_id:
        return False
    return bool(IMAGE_MODEL_RE.match(model_id) or VIDEO_MODEL_RE.match(model_id))


def is_image_chat_model(model_id: str | None) -> bool:
    return bool(IMAGE_MODEL_RE.match((model_id or "").strip()))


def is_video_chat_model(model_id: str | None) -> bool:
    return bool(VIDEO_MODEL_RE.match((model_id or "").strip()))


def extract_prompt_from_messages(
    form_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> str:
    """Pull prompt text from every shape Aeryn/OpenWebUI chat may send."""
    metadata = metadata or {}

    # 1) Direct prompt field
    if isinstance(form_data.get("prompt"), str) and form_data["prompt"].strip():
        return form_data["prompt"].strip()

    # 2) OpenWebUI chat UI often sends user_message / parent_message objects
    #    (and main.py moves user_message into metadata before process_chat).
    for candidate in (
        form_data.get("user_message"),
        form_data.get("parent_message"),
        metadata.get("user_message"),
    ):
        text = _message_to_text(candidate)
        if text:
            return text

    # 3) Standard OpenAI-style messages array
    messages = form_data.get("messages") or []
    if isinstance(messages, list):
        for message in reversed(messages):
            if not isinstance(message, dict):
                continue
            if message.get("role") not in (None, "user"):
                continue
            text = _content_to_text(message.get("content"))
            if text:
                return text
        for message in reversed(messages):
            text = _message_to_text(message)
            if text:
                return text

    # 4) Metadata variables / input leftovers used by some clients
    variables = metadata.get("variables") if isinstance(metadata.get("variables"), dict) else {}
    for key in ("prompt", "input", "query", "text", "message"):
        value = variables.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def _message_to_text(message: Any) -> str:
    if isinstance(message, str):
        return message.strip()
    if not isinstance(message, dict):
        return ""
    for key in ("content", "text", "prompt", "message", "input"):
        text = _content_to_text(message.get(key))
        if text:
            return text
    return ""


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif item.get("type") in (None, "text", "input_text") and isinstance(
                    item.get("content"), str
                ):
                    parts.append(item["content"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "\n".join(p.strip() for p in parts if p and p.strip()).strip()
    if isinstance(content, dict):
        for key in ("text", "content", "prompt", "value"):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def chat_completion_payload(model: str, content: str) -> dict[str, Any]:
    created = int(time.time())
    return {
        "id": f"chatcmpl-media-{created}",
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


async def handle_media_chat(
    request: Request,
    form_data: dict[str, Any],
    user,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = metadata or {}
    model_id = str(form_data.get("model") or "").strip()
    if not model_id and isinstance(metadata.get("model"), dict):
        model_id = str(metadata["model"].get("id") or "").strip()

    prompt = extract_prompt_from_messages(form_data, metadata)
    if not prompt:
        # Helpful debug without leaking full payload secrets.
        log.warning(
            "media chat missing prompt model=%s form_keys=%s meta_keys=%s",
            model_id,
            sorted(list(form_data.keys())),
            sorted(list(metadata.keys())),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Media model requires a text prompt in the chat message.",
        )

    if is_image_chat_model(model_id):
        input_images = extract_input_images(form_data, metadata)
        if not input_images:
            # Follow-up turns often only send text ("cover his eyes too").
            # Reuse the most recent image from this chat so multi-turn edits work.
            input_images = await extract_followup_images(form_data, metadata)
            if input_images:
                log.info(
                    "media follow-up using prior image(s) model=%s images=%s",
                    model_id,
                    input_images[:3],
                )
                # Enrich short follow-up prompts with previous intent when useful.
                prompt = enrich_followup_prompt(prompt, form_data, metadata)
        return await _handle_image_chat(
            request,
            model_id,
            prompt,
            user,
            metadata,
            input_images=input_images,
        )
    if is_video_chat_model(model_id):
        return await _handle_video_chat(request, model_id, prompt, form_data, user, metadata)
    raise HTTPException(status_code=400, detail=f"Unsupported media model: {model_id}")


def enrich_followup_prompt(
    prompt: str,
    form_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> str:
    """For short follow-ups, prepend a compact prior user intent if available."""
    prompt = (prompt or "").strip()
    if not prompt:
        return prompt
    # Keep long prompts as-is.
    if len(prompt) > 220 and not FOLLOWUP_HINT_RE.search(prompt):
        return prompt

    prior = extract_prior_user_prompt(form_data, metadata)
    if not prior or prior == prompt:
        return prompt
    # Avoid huge prior dumps.
    prior = prior.strip()
    if len(prior) > 700:
        prior = prior[:700].rstrip() + "..."
    return (
        f"{prompt}\n\n"
        "Continue from the previous image/result. Previous request for context:\n"
        f"{prior}"
    )


def extract_prior_user_prompt(
    form_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> str:
    metadata = metadata or {}
    # Prefer parent/user history if present in payload.
    for candidate in (
        form_data.get("parent_message"),
        metadata.get("parent_message"),
    ):
        text = _message_to_text(candidate)
        if text:
            return text

    messages = form_data.get("messages") or []
    if isinstance(messages, list):
        # second-latest user message
        user_texts = []
        for message in messages:
            if isinstance(message, dict) and message.get("role") in (None, "user"):
                text = _content_to_text(message.get("content"))
                if text:
                    user_texts.append(text)
        if len(user_texts) >= 2:
            return user_texts[-2]
    return ""


async def extract_followup_images(
    form_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> list[str]:
    """Find the most recent image from prior turns for multi-turn edit continuity."""
    metadata = metadata or {}
    found: list[str] = []

    def add_from_text(text: Any):
        if not isinstance(text, str) or not text.strip():
            return
        for match in MARKDOWN_IMAGE_RE.findall(text):
            ref = match.strip().strip("<>\"'")
            if ref:
                found.append(ref)
        for match in FILE_URL_RE.findall(text):
            found.append(match)

    def add_from_message(message: Any):
        if not isinstance(message, dict):
            return
        add_from_text(message.get("content"))
        # Non-streaming path may persist media under output instead of content.
        output = message.get("output")
        # output may be JSON string in DB rows
        if isinstance(output, str):
            raw = output.strip()
            if raw.startswith("[") or raw.startswith("{"):
                try:
                    import json as _json

                    output = _json.loads(raw)
                except Exception:
                    add_from_text(raw)
                    output = None
            else:
                add_from_text(raw)
                output = None

        if isinstance(output, list):
            for item in output:
                if isinstance(item, dict):
                    # nested content parts: [{type:message, content:[{type:output_text,text:...}]}]
                    nested = item.get("content")
                    if isinstance(nested, list):
                        for part in nested:
                            if isinstance(part, dict):
                                add_from_text(part.get("text") or part.get("content") or "")
                            elif isinstance(part, str):
                                add_from_text(part)
                    add_from_text(item.get("text") or "")
                    for key in ("url", "image_url", "file_id", "id"):
                        val = item.get(key)
                        if isinstance(val, str) and val.strip():
                            found.append(val.strip())
                    if isinstance(item.get("image_url"), dict):
                        url = item["image_url"].get("url")
                        if isinstance(url, str) and url.strip():
                            found.append(url.strip())
                elif isinstance(item, str):
                    add_from_text(item)
        elif isinstance(output, dict):
            nested = output.get("content")
            if isinstance(nested, list):
                for part in nested:
                    if isinstance(part, dict):
                        add_from_text(part.get("text") or part.get("content") or "")
                    elif isinstance(part, str):
                        add_from_text(part)
            add_from_text(output.get("text") or output.get("content") or "")
            for key in ("url", "image_url", "file_id", "id"):
                val = output.get(key)
                if isinstance(val, str) and val.strip():
                    found.append(val.strip())

        # assistant/user files
        files = message.get("files")
        if isinstance(files, list):
            for item in files:
                if isinstance(item, dict):
                    for key in ("url", "id"):
                        val = item.get(key)
                        if isinstance(val, str) and val.strip():
                            found.append(val.strip())
                    file_obj = item.get("file")
                    if isinstance(file_obj, dict) and isinstance(file_obj.get("id"), str):
                        found.append(file_obj["id"])
                elif isinstance(item, str) and item.strip():
                    found.append(item.strip())

        # embeds / sources sometimes carry generated media urls
        embeds = message.get("embeds")
        if isinstance(embeds, list):
            for item in embeds:
                if isinstance(item, str):
                    found.append(item)
                elif isinstance(item, dict):
                    for key in ("url", "id", "src", "href"):
                        val = item.get(key)
                        if isinstance(val, str) and val.strip():
                            found.append(val.strip())

    # 1) parent_message / previous messages in request payload
    for candidate in (
        form_data.get("parent_message"),
        metadata.get("parent_message"),
        form_data.get("user_message"),
        metadata.get("user_message"),
    ):
        add_from_message(candidate)

    messages = form_data.get("messages") or []
    if isinstance(messages, list):
        for message in messages:
            add_from_message(message)

    # 2) chat history from DB when chat_id is known
    chat_id = (
        metadata.get("chat_id")
        or form_data.get("chat_id")
        or (metadata.get("session_id") if isinstance(metadata.get("session_id"), str) else None)
    )
    parent_id = (
        metadata.get("parent_id")
        or metadata.get("parentId")
        or form_data.get("parent_id")
        or form_data.get("parentId")
    )
    # user_message may include parentId
    user_message = form_data.get("user_message") or metadata.get("user_message")
    if isinstance(user_message, dict):
        parent_id = parent_id or user_message.get("parentId") or user_message.get("parent_id")

    if chat_id and not str(chat_id).startswith(("local:", "channel:")):
        try:
            messages_map = await Chats.get_messages_map_by_chat_id(str(chat_id))
        except Exception as e:
            log.warning("follow-up history load failed chat_id=%s err=%s", chat_id, e)
            messages_map = None

        if isinstance(messages_map, dict) and messages_map:
            # Walk parent chain if parent_id known; else scan newest messages.
            chain: list[dict[str, Any]] = []
            if parent_id and parent_id in messages_map:
                current = messages_map.get(parent_id)
                visited = set()
                while isinstance(current, dict):
                    mid = current.get("id") or id(current)
                    if mid in visited:
                        break
                    visited.add(mid)
                    chain.append(current)
                    pid = current.get("parentId") or current.get("parent_id")
                    current = messages_map.get(pid) if pid else None
            else:
                # Fallback: all messages sorted by timestamp desc.
                chain = sorted(
                    [m for m in messages_map.values() if isinstance(m, dict)],
                    key=lambda m: m.get("timestamp") or m.get("created_at") or 0,
                    reverse=True,
                )

            for message in chain:
                before = len(found)
                add_from_message(message)
                # Prefer the newest image only for follow-up continuity.
                if len(found) > before:
                    break

    # normalize / de-dupe, prefer file ids / local file urls
    uniq: list[str] = []
    seen = set()
    for item in found:
        ref = item.strip()
        if not ref or ref in seen:
            continue
        # strip query fragments
        ref = ref.split("?")[0].split("#")[0]
        # convert full file content urls to file id where possible
        m = FILE_URL_RE.search(ref)
        if m:
            ref = m.group(1)
        if ref.startswith("data:image") or ref.startswith("http://") or ref.startswith("https://") or FILE_ID_RE.match(ref) or ref.startswith("/api/v1/files/"):
            seen.add(ref)
            uniq.append(ref)
    return uniq


def extract_input_images(
    form_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> list[str]:
    """Collect uploaded/local image refs from chat payload for image-edit mode."""
    metadata = metadata or {}
    found: list[str] = []

    def add(value: Any):
        if not value:
            return
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return
            if text.startswith("data:image") or text.startswith("http://") or text.startswith("https://"):
                found.append(text)
                return
            if text.startswith("/api/v1/files/"):
                found.append(text)
                return
            # bare file id
            if re.fullmatch(r"[0-9a-fA-F-]{16,}", text):
                found.append(text)
            return
        if isinstance(value, dict):
            # Common OpenWebUI shapes
            for key in ("url", "id", "image", "path", "content"):
                if key in value:
                    add(value.get(key))
            file_obj = value.get("file")
            if isinstance(file_obj, dict):
                add(file_obj.get("id"))
                add(file_obj.get("url"))
                meta = file_obj.get("meta") if isinstance(file_obj.get("meta"), dict) else {}
                ctype = str(meta.get("content_type") or value.get("content_type") or "")
                if ctype.startswith("image/") and file_obj.get("id"):
                    add(file_obj.get("id"))
            # content parts
            if isinstance(value.get("content"), list):
                for part in value["content"]:
                    add(part)
            return
        if isinstance(value, list):
            for item in value:
                add(item)

    # top-level files
    add(form_data.get("files"))
    add(metadata.get("files"))

    # user message containers
    for candidate in (
        form_data.get("user_message"),
        form_data.get("parent_message"),
        metadata.get("user_message"),
    ):
        if isinstance(candidate, dict):
            add(candidate.get("files"))
            add(candidate.get("content"))

    # messages array
    messages = form_data.get("messages") or []
    if isinstance(messages, list):
        for message in messages:
            if not isinstance(message, dict):
                continue
            add(message.get("files"))
            add(message.get("content"))
            add(message.get("images"))

    # de-dupe preserve order
    uniq: list[str] = []
    seen = set()
    for item in found:
        if item in seen:
            continue
        seen.add(item)
        uniq.append(item)
    return uniq


async def _handle_image_chat(
    request: Request,
    model_id: str,
    prompt: str,
    user,
    metadata: dict[str, Any],
    input_images: list[str] | None = None,
) -> dict[str, Any]:
    # Ensure image generation/edit is pointed at Artemisia with the same admin key.
    await _ensure_image_generation_config()

    input_images = input_images or []
    images = None
    label = "generated image"
    last_err: Exception | None = None

    async def _retry(op_name: str, fn, attempts: int = 3):
        nonlocal last_err
        delay = 1.5
        for attempt in range(1, attempts + 1):
            try:
                return await fn()
            except Exception as e:
                last_err = e
                msg = str(e)
                transient = any(
                    token in msg
                    for token in (
                        "HTTP 502",
                        "HTTP 503",
                        "HTTP 504",
                        "temporarily unavailable",
                        "Gateway time-out",
                        "Bad gateway",
                        "Service Temporarily Unavailable",
                        "Service Unavailable",
                    )
                )
                log.warning(
                    "%s failed model=%s attempt=%s/%s err=%s",
                    op_name,
                    model_id,
                    attempt,
                    attempts,
                    e,
                )
                if not transient or attempt >= attempts:
                    raise
                await asyncio.sleep(delay)
                delay = min(delay * 2, 8)

    if input_images:
        # 1) Prefer native image-edit endpoint.
        try:
            async def _edit():
                form = EditImageForm(
                    image=input_images[0] if len(input_images) == 1 else input_images,
                    prompt=prompt,
                    model=model_id,
                    n=1,
                    size=None,
                )
                return await image_edits(request, form, metadata=metadata, user=user)

            images = await _retry("image edit endpoint", _edit)
            label = "edited image"
        except Exception as e:
            last_err = e
            log.warning("image edit endpoint failed model=%s err=%s", model_id, e)

        # 2) Fallback: send source image bytes to generations as image field.
        if not images:
            try:
                async def _edit_via_gen():
                    return await _image_edit_via_generations(
                        request=request,
                        model_id=model_id,
                        prompt=prompt,
                        input_images=input_images,
                        user=user,
                        metadata=metadata,
                    )

                images = await _retry("image edit via generations", _edit_via_gen)
                label = "edited image"
            except Exception as e:
                last_err = e
                log.warning("image edit via generations failed model=%s err=%s", model_id, e)

        # 3) Last resort: prompt-only generation (not ideal, but better than total failure).
        if not images:
            async def _prompt_only():
                enriched = await _prompt_with_source_image_context(prompt, input_images, user)
                form = CreateImageForm(model=model_id, prompt=enriched, n=1, size=None)
                return await image_generations(request, form, metadata=metadata, user=user)

            images = await _retry("prompt-only image generation", _prompt_only)
            label = "edited image"
    else:
        async def _generate():
            form = CreateImageForm(model=model_id, prompt=prompt, n=1, size=None)
            return await image_generations(request, form, metadata=metadata, user=user)

        images = await _retry("image generation", _generate)
        label = "generated image"

    if not images:
        if last_err:
            raise HTTPException(status_code=502, detail=f"Image edit/generation failed: {last_err}")
        raise HTTPException(status_code=502, detail="Image generation returned no images.")

    urls = []
    for item in images:
        if isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    if not urls:
        raise HTTPException(status_code=502, detail="Image generation returned no image URLs.")

    content = "\n\n".join(f"![{label}]({url})" for url in urls)
    return chat_completion_payload(model_id, content)


async def _load_local_image_data_url(image_ref: str, user) -> str:
    if image_ref.startswith("data:image"):
        return image_ref

    file_id = image_ref
    if image_ref.startswith("/api/v1/files/"):
        file_id = image_ref.split("/api/v1/files/")[1].split("/content")[0]
    elif image_ref.startswith("http://") or image_ref.startswith("https://"):
        # remote URL — leave as-is for callers that can fetch it
        return image_ref

    file_response = await get_file_content_by_id(file_id, user)
    if isinstance(file_response, FileResponse):
        path = Path(file_response.path)
        raw = path.read_bytes()
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "image/jpeg"
        return f"data:{mime};base64,{base64.b64encode(raw).decode('utf-8')}"
    raise HTTPException(status_code=400, detail=f"Unable to load uploaded image: {image_ref}")


async def _image_edit_via_generations(
    request: Request,
    model_id: str,
    prompt: str,
    input_images: list[str],
    user,
    metadata: dict[str, Any],
) -> list[dict[str, str]]:
    """Edit-like request with source image bytes through image channel.

    NewAPI notes:
    - `/v1/images/edits` is not routed on channel 80 right now
    - multipart on `/v1/images/generations` may drop JSON body model and default to dall-e
    - so we send multipart image + put model in query string as belt-and-suspenders
    """
    base, key = await _openai_auth_from_config()
    if not key:
        raise HTTPException(status_code=500, detail="Missing Artemisia API key for image edit.")

    data_urls: list[str] = []
    for ref in input_images[:4]:
        data_urls.append(await _load_local_image_data_url(ref, user))

    edit_prompt = (
        f"{prompt.strip()}\n\n"
        "This is an IMAGE EDIT of the attached source image. "
        "Keep the person's head and face unchanged unless asked. "
        "Apply only the requested clothing/background changes."
    )

    form = aiohttp.FormData()
    form.add_field("model", model_id)
    form.add_field("prompt", edit_prompt)
    form.add_field("n", "1")
    form.add_field("size", "1024x1024")

    for idx, data_url in enumerate(data_urls):
        if not data_url.startswith("data:"):
            form.add_field("image_url" if idx == 0 else f"image_url_{idx}", data_url)
            continue
        header, b64 = data_url.split(",", 1)
        mime = header.split(";")[0].removeprefix("data:") or "image/jpeg"
        raw = base64.b64decode(b64)
        field_name = "image" if len(data_urls) == 1 else "image[]"
        form.add_field(
            field_name,
            raw,
            filename=f"source_{idx}.jpg",
            content_type=mime,
        )

    headers = {
        "Authorization": f"Bearer {key}",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    # Query model helps when body model is ignored for multipart.
    url = f"{base}/images/generations?model={model_id}"
    session = await get_session()
    timeout = aiohttp.ClientTimeout(total=max(AIOHTTP_CLIENT_TIMEOUT or 300, 600))
    async with session.post(url, data=form, headers=headers, ssl=AIOHTTP_CLIENT_SESSION_SSL, timeout=timeout) as r:
        body = await r.text()
        if r.status >= 400:
            raise HTTPException(
                status_code=400,
                detail=f"Image edit via generations failed ({r.status}): {body[:300]}",
            )
        try:
            res = await r.json(content_type=None)
        except Exception:
            res = json_loads_safe(body)

    out: list[dict[str, str]] = []
    for item in (res or {}).get("data") or []:
        if not isinstance(item, dict):
            continue
        if item.get("b64_json"):
            image_data = base64.b64decode(item["b64_json"])
            _, file_url = await upload_image(
                request,
                image_data,
                "image/png",
                {"model": model_id, "prompt": prompt, **(metadata or {})},
                user,
            )
            out.append({"url": file_url})
        elif item.get("url"):
            try:
                async with session.get(
                    item["url"], headers=headers, ssl=AIOHTTP_CLIENT_SESSION_SSL, timeout=timeout
                ) as ir:
                    if ir.status < 400:
                        image_data = await ir.read()
                        ctype = ir.headers.get("content-type") or "image/png"
                        _, file_url = await upload_image(
                            request,
                            image_data,
                            ctype,
                            {"model": model_id, "prompt": prompt, **(metadata or {})},
                            user,
                        )
                        out.append({"url": file_url})
                        continue
            except Exception:
                pass
            out.append({"url": item["url"]})
    if not out:
        raise HTTPException(status_code=502, detail="Image edit via generations returned no images.")
    return out


def json_loads_safe(text: str):
    import json

    try:
        return json.loads(text)
    except Exception:
        return {}


async def _prompt_with_source_image_context(prompt: str, input_images: list[str], user) -> str:
    refs = ", ".join(input_images[:3])
    return (
        f"{prompt.strip()}\n\n"
        "IMPORTANT: This is an IMAGE EDIT request. The user uploaded a source image. "
        "Preserve the person's identity/head/face unless asked otherwise, and apply only the "
        f"requested clothing/background changes. Source image ref(s): {refs}"
    )


async def _ensure_image_generation_config() -> None:
    values = await Config.get_many(
        "image_generation.enable",
        "image_generation.engine",
        "image_generation.model",
        "image_generation.openai.api_base_url",
        "image_generation.openai.api_key",
        "openai.api_base_urls",
        "openai.api_keys",
    )
    base_urls = values.get("openai.api_base_urls") or []
    api_keys = values.get("openai.api_keys") or []
    upstream = ""
    key = ""
    if base_urls and api_keys:
        upstream = str(base_urls[0]).rstrip("/")
        key = str(api_keys[0] or "")
    if not upstream:
        upstream = "https://artemisiahub.com/v1"
    if not key:
        key = str(values.get("image_generation.openai.api_key") or "")

    updates = {
        "image_generation.enable": True,
        "image_generation.prompt.enable": True,
        "image_generation.engine": "openai",
        "image_generation.model": values.get("image_generation.model") or "gpt-image-2",
        "image_generation.openai.api_base_url": upstream,
        "image_generation.openai.params": {},
        "images.edit.enable": True,
        "images.edit.engine": "openai",
        "images.edit.model": values.get("image_generation.model") or "gpt-image-2",
        "images.edit.openai.api_base_url": upstream,
    }
    if key:
        updates["image_generation.openai.api_key"] = key
        updates["images.edit.openai.api_key"] = key
    await Config.upsert(updates)


async def _openai_auth_from_config() -> tuple[str, str]:
    values = await Config.get_many(
        "openai.api_base_urls",
        "openai.api_keys",
        "image_generation.openai.api_base_url",
        "image_generation.openai.api_key",
    )
    base_urls = values.get("openai.api_base_urls") or []
    api_keys = values.get("openai.api_keys") or []
    if base_urls and api_keys and api_keys[0]:
        return str(base_urls[0]).rstrip("/"), str(api_keys[0])
    base = str(values.get("image_generation.openai.api_base_url") or "https://artemisiahub.com/v1").rstrip("/")
    key = str(values.get("image_generation.openai.api_key") or "")
    if not key:
        raise HTTPException(status_code=500, detail="No Artemisia API key configured for media generation.")
    return base, key


async def _handle_video_chat(
    request: Request,
    model_id: str,
    prompt: str,
    form_data: dict[str, Any],
    user,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    base, key = await _openai_auth_from_config()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "AerynMediaBridge/1.0",
    }

    # Default short clip for playground/testing. Clients can pass params.seconds.
    seconds = "5"
    params = form_data.get("params") if isinstance(form_data.get("params"), dict) else {}
    if params.get("seconds") is not None:
        seconds = str(params.get("seconds"))
    elif form_data.get("seconds") is not None:
        seconds = str(form_data.get("seconds"))

    payload = {
        "model": model_id,
        "prompt": prompt,
        "seconds": seconds,
    }

    session = await get_session()
    timeout = aiohttp.ClientTimeout(total=max(AIOHTTP_CLIENT_TIMEOUT or 300, 600))
    create_url = f"{base}/video/generations"
    async with session.post(
        create_url,
        json=payload,
        headers=headers,
        ssl=AIOHTTP_CLIENT_SESSION_SSL,
        timeout=timeout,
    ) as response:
        body = await response.text()
        if response.status >= 400:
            log.error("Video create failed (%s): %s", response.status, body[:500])
            raise HTTPException(
                status_code=400,
                detail=_extract_error_detail(body) or f"Video generation failed ({response.status})",
            )
        try:
            created = await response.json(content_type=None)
        except Exception:
            created = {}

    task_id = (
        (created or {}).get("task_id")
        or (created or {}).get("id")
        or ((created or {}).get("data") or {}).get("task_id")
        or ((created or {}).get("data") or {}).get("id")
    )
    event_emitter = await _video_event_emitter(metadata)
    if not task_id:
        # Some providers may return final media immediately.
        media_url = _extract_media_url(created)
        if media_url:
            local_video_url = await _store_generated_video(
                request=request,
                session=session,
                media_url=media_url,
                headers=headers,
                timeout=timeout,
                user=user,
                model_id=model_id,
                task_id="completed",
                metadata=metadata,
            )
            return chat_completion_payload(
                model_id,
                _video_chat_content(model_id, seconds, local_video_url),
            )
        raise HTTPException(status_code=502, detail=f"Video task id missing: {str(created)[:300]}")

    result = await _poll_video_task(
        session,
        base,
        headers,
        str(task_id),
        timeout,
        event_emitter=event_emitter,
    )
    media_url = _extract_media_url(result)
    if media_url:
        local_video_url = await _store_generated_video(
            request=request,
            session=session,
            media_url=media_url,
            headers=headers,
            timeout=timeout,
            user=user,
            model_id=model_id,
            task_id=str(task_id),
            metadata=metadata,
        )
        return chat_completion_payload(
            model_id,
            _video_chat_content(model_id, seconds, local_video_url),
        )

    # Fallback: return task status for debugging instead of empty success.
    status_text = _extract_task_status(result)
    raise HTTPException(
        status_code=502,
        detail=f"Video task finished without media URL (status={status_text}). Raw: {str(result)[:300]}",
    )


async def _poll_video_task(
    session: aiohttp.ClientSession,
    base: str,
    headers: dict[str, str],
    task_id: str,
    timeout: aiohttp.ClientTimeout,
    max_wait_s: int = 180,
    event_emitter: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
) -> dict[str, Any]:
    poll_urls = [
        f"{base}/video/generations/{task_id}",
        f"{base}/videos/{task_id}",
    ]
    deadline = time.time() + max_wait_s
    last: dict[str, Any] = {}
    last_progress: int | None = None
    while time.time() < deadline:
        for url in poll_urls:
            try:
                async with session.get(
                    url,
                    headers=headers,
                    ssl=AIOHTTP_CLIENT_SESSION_SSL,
                    timeout=timeout,
                ) as response:
                    body = await response.text()
                    if response.status >= 400:
                        continue
                    try:
                        last = await response.json(content_type=None)
                    except Exception:
                        continue
            except Exception as exc:
                log.debug("video poll error %s: %s", url, exc)
                continue

            media_url = _extract_media_url(last)
            status_text = (_extract_task_status(last) or "").lower()
            is_complete = _is_success_video_status(status_text)
            progress = _extract_task_progress(last)
            if progress is None and media_url and is_complete:
                progress = 100
            if progress is not None and progress != last_progress:
                last_progress = progress
                await _emit_video_progress(
                    event_emitter,
                    progress,
                    done=is_complete,
                )
            # Seedance exposes a video URL while status is still IN_PROGRESS.
            # Fetching it at that point returns 404, so only treat it as final
            # once the task status says the file is complete.
            if media_url and is_complete:
                return last
            if status_text in {"failed", "error", "cancelled", "canceled"}:
                raise HTTPException(
                    status_code=400,
                    detail=f"Video generation {status_text}: {str(last)[:300]}",
                )
            if is_complete:
                # completed but no media url extracted
                if last_progress != 100:
                    await _emit_video_progress(event_emitter, 100, done=True)
                return last
        await asyncio.sleep(2.5)
    return last


async def _video_event_emitter(
    metadata: dict[str, Any] | None,
) -> Callable[[dict[str, Any]], Awaitable[None]] | None:
    metadata = metadata or {}
    required = ("user_id", "chat_id", "message_id")
    if not all(metadata.get(key) for key in required):
        return None
    from open_webui.socket.main import get_event_emitter

    return await get_event_emitter(metadata)


async def _emit_video_progress(
    event_emitter: Callable[[dict[str, Any]], Awaitable[None]] | None,
    progress: int,
    *,
    done: bool,
) -> None:
    if not event_emitter:
        return
    progress = max(0, min(100, int(progress)))
    await event_emitter(
        {
            "type": "status",
            "data": {
                "description": f"Generating video: {progress}%",
                "progress": progress,
                "done": done,
            },
        }
    )


def _extract_task_progress(data: Any) -> int | None:
    if isinstance(data, list):
        for item in data:
            progress = _extract_task_progress(item)
            if progress is not None:
                return progress
        return None
    if not isinstance(data, dict):
        return None

    for key in ("progress", "percent", "percentage"):
        value = data.get(key)
        if isinstance(value, str):
            match = re.search(r"-?\d+(?:\.\d+)?", value)
            if match:
                return max(0, min(100, round(float(match.group(0)))))
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric = float(value)
            if 0 <= numeric <= 1 and not numeric.is_integer():
                numeric *= 100
            return max(0, min(100, round(numeric)))

    for key in ("data", "result", "output", "content", "video"):
        progress = _extract_task_progress(data.get(key))
        if progress is not None:
            return progress
    return None


def _is_success_video_status(status_text: str) -> bool:
    return status_text in {"succeeded", "success", "completed", "complete", "done"}


async def _store_generated_video(
    *,
    request: Request,
    session: aiohttp.ClientSession,
    media_url: str,
    headers: dict[str, str],
    timeout: aiohttp.ClientTimeout,
    user,
    model_id: str,
    task_id: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    download_headers = {key: value for key, value in headers.items() if key.lower() != "content-type"}
    async with session.get(
        media_url,
        headers=download_headers,
        ssl=AIOHTTP_CLIENT_SESSION_SSL,
        timeout=timeout,
    ) as response:
        body = await response.read()
        if response.status >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"Generated video download failed ({response.status}).",
            )
        content_type = str(response.headers.get("content-type") or "video/mp4").split(";", 1)[0]

    if not body:
        raise HTTPException(status_code=502, detail="Generated video download returned an empty file.")
    extension = mimetypes.guess_extension(content_type) or ".mp4"
    safe_task_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", task_id).strip("-") or "result"
    upload = UploadFile(
        file=io.BytesIO(body),
        filename=f"{model_id}-{safe_task_id}{extension}",
        headers={"content-type": content_type},
    )
    file_item = await upload_file_handler(
        request,
        file=upload,
        metadata={
            "source": "aeryn-video-generation",
            "model": model_id,
            "task_id": task_id,
            **({"chat_id": metadata.get("chat_id")} if metadata and metadata.get("chat_id") else {}),
        },
        process=False,
        user=user,
    )
    file_id = file_item.get("id") if isinstance(file_item, dict) else getattr(file_item, "id", None)
    if not file_id:
        raise HTTPException(status_code=502, detail="Generated video could not be stored in Aeryn.")
    return f"/api/v1/files/{file_id}/content"


def _video_chat_content(model_id: str, seconds: str, local_video_url: str) -> str:
    return f"Generated with `{model_id}` ({seconds}s)\n\n[generated video]({local_video_url})"


def _extract_error_detail(body: str) -> str:
    try:
        data = __import__("json").loads(body)
        if isinstance(data, dict):
            err = data.get("error") or data.get("detail") or data.get("message")
            if isinstance(err, dict):
                return str(err.get("message") or err)
            if err:
                return str(err)
    except Exception:
        pass
    return (body or "")[:300]


def _extract_task_status(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    for key in ("status", "state", "task_status"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    nested = data.get("data")
    if isinstance(nested, dict):
        return _extract_task_status(nested)
    return ""


def _extract_media_url(data: Any) -> str | None:
    if not data:
        return None
    if isinstance(data, str) and data.startswith("http"):
        return data
    if isinstance(data, list):
        for item in data:
            url = _extract_media_url(item)
            if url:
                return url
        return None
    if not isinstance(data, dict):
        return None

    for key in ("result_url", "url", "video_url", "content_url", "output_url", "file_url"):
        value = data.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value

    for key in ("video", "output", "result", "content", "data", "videos", "outputs"):
        if key in data:
            url = _extract_media_url(data.get(key))
            if url:
                return url
    return None
