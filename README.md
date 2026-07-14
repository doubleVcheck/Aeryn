<img width="500" height="540" alt="aeryn-logo-Photoroom" src="https://github.com/user-attachments/assets/d9bfe5d9-a4c6-4ec9-bf98-e654f54f47ff" />

# Aeryn / ZaneCode

Aeryn is the Zane AI workspace (ZaneCode package). One Artemisia Hub account powers chat, image/video generation, desktop, terminal, and coding CLIs.

Public repo: [doubleVcheck/Aeryn](https://github.com/doubleVcheck/Aeryn) (`master`)

## What You Get

- **ZaneChat (Aeryn)**: web chat + local AI gateway.
<img width="1919" height="924" alt="image" src="https://github.com/user-attachments/assets/dd9b7569-28f9-4226-83d2-5fc99eb082d5" />

- **ZaneApp**: desktop app for coding sessions.
<img width="1920" height="1048" alt="image" src="https://github.com/user-attachments/assets/93001f18-b001-4874-9eb1-a40a970aba5c" />

- **ZaneCLI**: terminal UI through `zanecli` and `zanecode`
<img width="1908" height="951" alt="image" src="https://github.com/user-attachments/assets/d68f1d1b-cf6b-4ac3-8d0e-ff808342515a" />

- **CLI wrappers**: route popular coding CLIs through your Zane models (`zanecc`, `zanegpt`, `zaneoc`, `zaneh`, `zanegrokcli`, …).
Example from **zanegpt**:
<img width="1913" height="413" alt="image" src="https://github.com/user-attachments/assets/ebe79d76-b176-437c-9275-2f26480222c9" />

## Latest Features (master)

- **Artemisia Hub by default**
  - Upstream: `https://artemisiahub.com/v1`
  - Default chat model: `gpt-5.5`
  - Pinned models: `gpt-5.5`, `gpt-image-2`, `seedance-2.0`
  - Static first-run catalog so the model picker is not empty before setup
- **Media chat in the normal model picker**
  - `gpt-image-*` → image generation (saved as local `/api/v1/files/...` assets)
  - `seedance-*` → video generation with progress status + durable local video storage
- **Chat unlock after errors**
  - A failed turn marks the assistant message `done` and clears active tasks so you can keep chatting
- **Per-user credentials only**
  - No admin API key ships in the public build
  - Each install runs `zane setup` with that user’s Artemisia access token

## How It Works

Aeryn connects to your [artemisiahub.com](https://artemisiahub.com) account with an access token from your profile.

1. Open `https://artemisiahub.com`
2. Sign in → profile
3. Create or copy an **access token**
4. Install Aeryn / ZaneCode
5. Paste the token only into the local secure prompt when asked

Setup then:

1. Creates or reuses your model API token
2. Points ZaneChat at Artemisia Hub
3. Loads ModelSquare models (when a key is present)
4. Writes local CLI/app config under `~/.config/zane-cli/`

Your Artemisia access token is **not** committed to the repo. Local credentials live at:

```text
~/.config/zane-cli/credentials.env
~/.config/zane-cli/config.json
```

## Install (public)

```bash
git clone https://github.com/doubleVcheck/Aeryn.git
cd Aeryn
./integrations/zane-cli/bin/zane install
zane setup --upstream-base https://artemisiahub.com/v1
zanechat
```

If `zane` is not on your PATH yet:

```bash
./integrations/zane-cli/bin/zane install
```

### Important public vs admin rules

- Public `master` does **not** include a default admin API key
- Do **not** copy an admin install’s:
  - `backend/open_webui/data/`
  - `.webui_secret_key`
  - launcher env / secrets files
  - `~/.config/zane-cli/`
- Each user must run `zane setup` with **their own** Artemisia token

## Main Commands

```bash
zanechat       # start ZaneChat web UI and gateway
zaneapp        # start ZaneApp
zanecli        # start ZaneCLI
zanecode       # alias for ZaneCLI
zaneupdate     # refresh models from Artemisia ModelSquare
zane models    # list models exposed by the local gateway
zane use MODEL # set the default model for wrappers
zane status    # show local bridge status
```

## Media Models In Chat

Pick these like any chat model:

| Model | What it does |
| --- | --- |
| `gpt-image-2` | Image generation / edit via media chat bridge |
| `seedance-2.0` | Video generation with progress events + local file save |
| `gpt-5.5` (default) | Standard chat |

Generated media is stored as Aeryn files (`/api/v1/files/<id>/content`), not as temporary remote-only URLs.

## Use Zane Models In Other CLIs

```bash
zanegpt        # Codex-style CLI through Zane
zanecodex      # Codex-style CLI through Zane
zanecc         # Claude Code through Zane
zaneoc         # open coding sessions through Zane
zaneh          # Hermes through Zane
zanehermes     # Hermes through Zane
zanegrokcli    # Grok CLI through Zane
```

Original tools stay untouched. The `zane*` commands use your local Zane config and model list.

## Refresh Models

When Artemisia ModelSquare adds, removes, or renames models:

```bash
zaneupdate
```

This refreshes provider groups, removes stale local model entries, and updates ZaneChat / ZaneCLI / ZaneApp catalogs.

## Local Gateway

Compatible endpoints for apps and CLIs (default port 8080):

```text
OpenAI-compatible:      http://127.0.0.1:8080/zanellm/v1
OpenAI Responses-style: http://127.0.0.1:8080/openai
Anthropic-compatible:   http://127.0.0.1:8080/anthropic
```

Use the locally generated API key from ZaneCode config when a tool asks for a base URL + key.

## Project Names

- **Aeryn** — this product / repo name
- **ZaneChat** — web UI and gateway
- **ZaneApp** — desktop app
- **ZaneCLI** — terminal UI
- **ZaneCode** — full package that installs and connects all of them

## Security

Do **not** commit:

- API keys / access tokens
- local databases (`backend/open_webui/data/`)
- `.webui_secret_key`
- generated app data
- anything under `~/.config/zane-cli`

## Troubleshooting

- **Empty model list** → run `zane setup`, then hard-refresh the UI
- **Chat stuck after one error** → current master marks failed turns `done` and clears tasks; hard-refresh if you still have an old session open
- **Image/video models missing** → ensure your Artemisia key includes those channels; GPT-only keys may list chat models only
- **Do not reuse admin data dirs** on public installs

## License

See `LICENSE` and related notice files in this repository.
