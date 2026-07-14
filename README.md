# Aeryn

Local web chat gateway for [Artemisia Hub](https://artemisiahub.com).

Public repo: **[doubleVcheck/Aeryn](https://github.com/doubleVcheck/Aeryn)** (`master`)

## What it does

- Chat with Artemisia models in a browser
- Defaults to Artemisia Hub (`https://artemisiahub.com/v1`)
- Default model: `gpt-5.5`
- Image generation via `gpt-image-2`
- Video generation via `seedance-2.0` (progress + local file save)
- Stores generated media as local files under `/api/v1/files/<id>/content`
- Unlocks chat after an error so you can continue the same conversation
- No admin API key is shipped in public master

---

## How to use it (same way we tested)

### 1. Clone

```bash
git clone https://github.com/doubleVcheck/Aeryn.git
cd Aeryn
```

### 2. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r backend/requirements-min.txt
```

### 3. Clean local data (public install)

Do **not** copy admin DB/secrets.

```bash
mkdir -p backend/open_webui/data
```

### 4. Start Aeryn

```bash
source .venv/bin/activate
export PYTHONPATH="$(pwd)/backend"
export DATA_DIR="$(pwd)/backend/open_webui/data"
export FRONTEND_BUILD_DIR="$(pwd)/backend/open_webui/frontend"
export WEBUI_SECRET_KEY="$(openssl rand -hex 32)"
export HOST=127.0.0.1
export PORT=8080
bash backend/start.sh
```

Open:

```text
http://127.0.0.1:8080
```

Check health:

```bash
curl -s http://127.0.0.1:8080/health
# {"status":true}
```

### 5. Create a local account

1. Open the UI
2. Sign up / sign in (local Aeryn account)
3. Hard-refresh once after first login

### 6. Connect Artemisia

In Admin / connection settings (or first provider config), set:

| Field | Value |
| --- | --- |
| Base URL | `https://artemisiahub.com/v1` |
| API key | your Artemisia model key (`sk-...`) |
| Default model | `gpt-5.5` |
| Image model | `gpt-image-2` |

Then hard-refresh.

Expected:

- Model list includes Artemisia models
- Default selected model is `gpt-5.5`

If models are empty, the key is missing/invalid or the browser is stale.

### 7. Text chat

1. Select `gpt-5.5`
2. Send something short, e.g. `Reply with exactly: OK`
3. You should get a normal assistant reply

### 8. Image generation (`gpt-image-2`)

1. Switch model to `gpt-image-2`
2. Prompt example:

```text
tiny red circle logo on white, minimal flat
```

3. Wait for completion
4. Result appears as a local file, e.g.:

```text
/api/v1/files/<id>/content
```

Notes from live testing:

- Needs a key with image channel access
- Chat-only keys may not show/run `gpt-image-2`
- Upstream can occasionally 504; retry works

### 9. Video generation (`seedance-2.0`)

1. Switch model to `seedance-2.0`
2. Send a short video prompt
3. Watch progress (for example `0%` → `70%` → `100%`)
4. Finished video is saved locally as `/api/v1/files/<id>/content`

Important:

- Do not stop at the first temporary provider URL
- Wait for task success / completed
- Prefer Artemisia `result_url` for the final download

### 10. After an error, continue chatting

On current master:

- a failed turn is marked complete (`done: true`)
- active task state is cleared
- you can send another message in the same chat

If an old open tab still looks blocked, hard-refresh.

---

## Defaults

| Item | Value |
| --- | --- |
| Upstream | `https://artemisiahub.com/v1` |
| Default chat model | `gpt-5.5` |
| Pinned models | `gpt-5.5`, `gpt-image-2`, `seedance-2.0` |
| Bundled admin key | none |
| Media storage | local `/api/v1/files/...` |

---

## Useful API paths

```text
GET  /health
GET  /api/models
POST /api/chat/completions
POST /api/v1/images/generations
GET  /api/v1/files/<id>/content
```

---

## Public install rules

1. Every user uses **their own** Artemisia key
2. Do not ship or copy admin secrets
3. Do not commit:
   - API keys
   - `backend/open_webui/data/`
   - `.webui_secret_key`

Do not copy from an admin machine:

```text
backend/open_webui/data/
.webui_secret_key
any local secret/env launcher files
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Empty model list | Set Artemisia base + key, hard-refresh |
| No image/video models | Key/plan is probably chat-only |
| Image 504 | Upstream timeout; retry |
| Chat stuck after one error | Use current master; hard-refresh old sessions |
| Port 8080 busy | Stop the other process or change `PORT` |
| Broken after copying admin data | Delete local data dir and start clean |

---

## Security

Never commit secrets, databases, or local credential files.

---

## License

See `LICENSE` and related notice files.
