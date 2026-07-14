from __future__ import annotations

import asyncio
from types import SimpleNamespace

from open_webui.utils import media_chat


class _FakeResponse:
    def __init__(
        self,
        payload: dict | None = None,
        *,
        status: int = 200,
        body: bytes = b"",
        content_type: str = "application/json",
    ):
        self.payload = payload or {}
        self.status = status
        self._body = body
        self.headers = {"content-type": content_type}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def text(self):
        import json

        return json.dumps(self.payload)

    async def json(self, content_type=None):
        return self.payload

    async def read(self):
        return self._body


class _PollingSession:
    def __init__(self, payloads: list[dict]):
        self.payloads = list(payloads)

    def get(self, *args, **kwargs):
        if not self.payloads:
            raise AssertionError("unexpected extra poll")
        return _FakeResponse(self.payloads.pop(0))


class _DownloadSession:
    def __init__(self, body: bytes = b"fake-mp4-bytes"):
        self.body = body
        self.requested_urls: list[str] = []

    def get(self, url, *args, **kwargs):
        self.requested_urls.append(url)
        return _FakeResponse(body=self.body, content_type="video/mp4")


def test_poll_video_task_emits_real_provider_percentages(monkeypatch):
    responses = [
        {
            "code": "success",
            "data": {
                "status": "NOT_START",
                "progress": "0%",
                "data": {"status": "pending"},
            },
        },
        {
            "code": "success",
            "data": {
                "status": "IN_PROGRESS",
                "progress": "70%",
                "data": {
                    "status": "processing",
                    "progress": 70,
                    # The real provider exposes this URL before the file is ready.
                    # Aeryn must keep polling instead of downloading the 404 placeholder.
                    "url": "https://provider.invalid/api/video/abc123",
                },
            },
        },
        {
            "code": "success",
            "data": {
                "status": "SUCCESS",
                "progress": "100%",
                "result_url": "https://artemisiahub.com/v1/videos/task-123/content",
                "data": {
                    "status": "completed",
                    "progress": 100,
                    "url": "https://provider.invalid/api/video/abc123",
                },
            },
        },
    ]
    events: list[dict] = []

    async def emit(event: dict):
        events.append(event)

    async def no_sleep(_seconds: float):
        return None

    monkeypatch.setattr(asyncio, "sleep", no_sleep)

    result = asyncio.run(
        media_chat._poll_video_task(
            _PollingSession(responses),
            "https://artemisiahub.com/v1",
            {"Authorization": "Bearer test"},
            "task-123",
            SimpleNamespace(),
            max_wait_s=30,
            event_emitter=emit,
        )
    )

    assert media_chat._extract_media_url(result) == "https://artemisiahub.com/v1/videos/task-123/content"
    progress_events = [event for event in events if event.get("type") == "status"]
    assert [event["data"]["progress"] for event in progress_events] == [0, 70, 100]
    assert progress_events[-1]["data"]["done"] is True
    assert all("%" in event["data"]["description"] for event in progress_events)


def test_store_generated_video_returns_only_local_aeryn_file_url(monkeypatch):
    source_url = "https://provider.invalid/api/video/abc123"
    session = _DownloadSession()

    async def fake_upload_file_handler(*args, **kwargs):
        upload = kwargs["file"]
        assert upload.filename.endswith(".mp4")
        assert upload.content_type == "video/mp4"
        assert upload.file.read() == b"fake-mp4-bytes"
        return {"id": "local-video-file-id"}

    monkeypatch.setattr(media_chat, "upload_file_handler", fake_upload_file_handler, raising=False)

    local_url = asyncio.run(
        media_chat._store_generated_video(
            request=SimpleNamespace(),
            session=session,
            media_url=source_url,
            headers={"Authorization": "Bearer test"},
            timeout=SimpleNamespace(),
            user=SimpleNamespace(id="user-1"),
            model_id="seedance-2.0",
            task_id="task-123",
        )
    )

    assert session.requested_urls == [source_url]
    assert local_url == "/api/v1/files/local-video-file-id/content"
    assert "provider.invalid" not in local_url


def test_video_chat_content_never_exposes_upstream_hostname():
    content = media_chat._video_chat_content(
        model_id="seedance-2.0",
        seconds="5",
        local_video_url="/api/v1/files/local-video-file-id/content",
    )

    assert "seedance-2.0" in content
    assert "/api/v1/files/local-video-file-id/content" in content
    assert "sora2" not in content.lower()
    assert "provider" not in content.lower()
