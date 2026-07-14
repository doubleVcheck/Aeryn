# Aeryn

Local AI chat gateway for [Artemisia Hub](https://artemisiahub.com).

- Public users: this repo **`master`** — https://github.com/doubleVcheck/Aeryn  
- Admin / full ops tree (reference): https://github.com/zephyrzane/Aeryn/tree/aeryn-admin  

This README is for **public master**.

---

## What you get

- Browser chat UI
- Artemisia models by default
- Default chat model: `gpt-5.5`
- Image generation: `gpt-image-2`
- Video generation: `seedance-2.0` (progress + local file save)
- Local file storage for generated media: `/api/v1/files/<id>/content`
- Chat stays usable after an error (failed turn is closed; you can continue)
- No admin API key is included in public master

---

## How it works

Aeryn talks to your Artemisia Hub account.

1. Open https://artemisiahub.com and sign in  
2. Open your profile  
3. Create or copy an access token / model API key  
4. Install and start Aeryn locally  
5. Put the key only into your local config (never commit it)

Local secrets stay on your machine, for example under a local data dir / env.  
Do not commit keys, databases, or secret files.

---

## Install and run (public)

Same practical flow we used while testing public master.

### 1) Clone

```bash
git clone https://github.com/doubleVcheck/Aeryn.git
cd Aeryn
```

### 2) Python env

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r backend/requirements-min.txt
```

### 3) Clean data dir

Public installs start empty. Do **not** copy admin data/secrets.

```bash
mkdir -p backend/open_webui/data
```

### 4) Start

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

Health:

```bash
curl -s http://127.0.0.1:8080/health
# {"status":true}
```

### 5) Create a local account

1. Open the UI  
2. Sign up / sign in  
3. Hard-refresh once  

### 6) Connect Artemisia

In connection / admin provider settings:

| Field | Value |
| --- | --- |
| Base URL | `https://artemisiahub.com/v1` |
| API key | your Artemisia model key (`sk-...`) |
| Default model | `gpt-5.5` |
| Image model | `gpt-image-2` |

Hard-refresh again.

Expected:

- model list loads from Artemisia  
- default model is `gpt-5.5`  

If models are empty, key/base is wrong or the browser is stale.

---

## How to use it (like we did here)

### Text chat

1. Select `gpt-5.5`  
2. Send a short prompt, e.g. `Reply with exactly: OK`  
3. You get a normal assistant reply  

### Image generation

1. Select `gpt-image-2`  
2. Prompt example:

```text
tiny red circle logo on white, minimal flat
```

3. Wait until complete  
4. Result is a local file:

```text
/api/v1/files/<id>/content
```

Notes from testing:

- needs an Artemisia key with image access  
- chat-only keys may not include `gpt-image-2`  
- occasional upstream 504 → retry  

### Video generation

1. Select `seedance-2.0`  
2. Send a short video prompt  
3. Progress updates while the task runs (example: `0%` → `70%` → `100%`)  
4. Final video is saved as:

```text
/api/v1/files/<id>/content
```

Important:

- do not treat the first temporary provider URL as finished  
- wait for success / completed  
- prefer Artemisia `result_url` for download  

### After an error

On current master:

- failed assistant turn is marked done  
- active tasks are cleared  
- you can send another message in the same chat  

If an old tab still looks stuck, hard-refresh.

---

## Defaults (public master)

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

Local compatible gateway routes (when enabled):

```text
http://127.0.0.1:8080/openai
http://127.0.0.1:8080/anthropic
```

---

## Public vs admin

| | Public `master` | Admin branch |
| --- | --- | --- |
| Audience | general users | operators / full workspace |
| Reference | this README | https://github.com/zephyrzane/Aeryn/tree/aeryn-admin |
| Admin API key | not included | local-only, never commit |
| Data dir | clean per install | local ops data stays off git |

Do not copy from admin machines into public installs:

```text
backend/open_webui/data/
.webui_secret_key
local secret/env launcher files
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Empty model list | Set Artemisia base + key, hard-refresh |
| No image/video models | Key/plan is probably chat-only |
| Image 504 | Upstream timeout; retry |
| Chat blocked after one error | Use current master; hard-refresh old sessions |
| Port 8080 busy | Stop other process or change `PORT` |
| Broken after copying admin data | Delete local data dir and start clean |

---

## Security

Never commit:

- Artemisia tokens / model API keys  
- `backend/open_webui/data/` (includes `webui.db`)  
- `.webui_secret_key`  
- any local credential files  

---

## License

See `LICENSE` and related notice files.
