<img width="500" height="540" alt="aeryn-logo-Photoroom" src="https://github.com/user-attachments/assets/d9bfe5d9-a4c6-4ec9-bf98-e654f54f47ff" />

# Aeryn / ZaneCode

Aeryn is the Zane AI workspace. One [Artemisia Hub](https://artemisiahub.com) account powers chat, image/video generation, desktop, terminal, and coding CLIs.

Public repo: **[doubleVcheck/Aeryn](https://github.com/doubleVcheck/Aeryn)** (`master`)

---

## Quick start (new instructions)

### 0) Requirements

- Linux/macOS (or WSL2 on Windows)
- Git
- Node.js 18+ (for the `zane` installer/CLI)
- Python 3.11+ recommended for ZaneChat backend
- An [artemisiahub.com](https://artemisiahub.com) account

### 1) Get your Artemisia access token

1. Open https://artemisiahub.com and sign in
2. Go to your **profile**
3. Create or copy an **access token**
4. Keep it ready — you will paste it only into the local setup prompt (never commit it)

### 2) Clone and install

```bash
git clone https://github.com/doubleVcheck/Aeryn.git
cd Aeryn
./integrations/zane-cli/bin/zane install
```

This installs wrapper commands into `~/.local/bin` (make sure that is on your `PATH`).

### 3) Configure your account (required for every user)

```bash
zane setup --upstream-base https://artemisiahub.com/v1
```

What this does:

- Prompts for **your** Artemisia access token
- Creates or reuses **your** model API token
- Points ZaneChat at Artemisia Hub (`https://artemisiahub.com/v1`)
- Writes local config only under:

```text
~/.config/zane-cli/credentials.env
~/.config/zane-cli/config.json
```

Optional non-interactive form:

```bash
zane setup --upstream-base https://artemisiahub.com/v1 --account-id 1 --token-name aeryn
```

### 4) Start chat

```bash
zanechat
```

Open the printed local URL (default `http://127.0.0.1:8080`).

First UI check:

1. Hard-refresh the browser
2. Confirm models load (default **gpt-5.5**)
3. Send a short chat message
4. Optionally switch to **gpt-image-2** or **seedance-2.0** for media

### 5) Refresh models later

When Artemisia ModelSquare changes models:

```bash
zaneupdate
# or
zane update
```

Then hard-refresh ZaneChat.

---

## What you get

- **ZaneChat (Aeryn)** — web chat + local AI gateway  
  <img width="1919" height="924" alt="image" src="https://github.com/user-attachments/assets/dd9b7569-28f9-4226-83d2-5fc99eb082d5" />

- **ZaneApp** — desktop coding app  
  <img width="1920" height="1048" alt="image" src="https://github.com/user-attachments/assets/93001f18-b001-4874-9eb1-a40a970aba5c" />

- **ZaneCLI** — terminal UI (`zanecli` / `zanecode`)  
  <img width="1908" height="951" alt="image" src="https://github.com/user-attachments/assets/d68f1d1b-cf6b-4ac3-8d0e-ff808342515a" />

- **CLI wrappers** — use familiar tools through Zane models  
  Example **zanegpt**:  
  <img width="1913" height="413" alt="image" src="https://github.com/user-attachments/assets/ebe79d76-b176-437c-9275-2f26480222c9" />

---

## Defaults on public master

| Setting | Value |
| --- | --- |
| Upstream | `https://artemisiahub.com/v1` |
| Default chat model | `gpt-5.5` |
| Pinned models | `gpt-5.5`, `gpt-image-2`, `seedance-2.0` |
| API key in repo | **None** (each user runs `zane setup`) |
| First-run model catalog | Seeded so the picker is not empty before key setup |

### Media in the normal model picker

| Model | Action |
| --- | --- |
| `gpt-5.5` | Standard chat (default) |
| `gpt-image-2` | Image generation / edit |
| `seedance-2.0` | Video generation with progress |

Generated media is stored as local Aeryn files:

```text
/api/v1/files/<id>/content
```

### Chat unlock after errors

If a generation fails, the failed turn is marked complete and active tasks are cleared so you can send another message in the same chat.

---

## Full command reference

### Core

```bash
zane install          # install wrappers (alias: zane i / zanei)
zane setup            # configure Artemisia account/token
zane status           # show local bridge status
zane doctor           # check wrappers + gateway model fetch
zane update           # refresh ModelSquare models (alias: zaneupdate)
zane models [filter]  # list models from ZaneLLM
zane use <model-id>   # set default model for wrappers
zane usage [--json]   # show Artemisia profile/token usage
zane apps             # show endpoints + supported app setup
zane restore          # restore / cleanup wrappers
zane delete           # remove wrapper links
```

### Launchers

```bash
zanechat              # web UI + gateway
zaneapp               # desktop app
zanecli / zanecode    # terminal UI
```

### Coding CLI wrappers (through Zane models)

```bash
zanegpt / zanecodex   # Codex-style
zanecc                # Claude Code
zaneoc / zaneopencode # OpenCode-compatible
zaneh / zanehermes    # Hermes
zanegrok / zanexai    # Grok
zanegrokcli           # Claude-style Grok run
zanea / zaneaider     # Aider
zanecontinue / zanecn # Continue CLI
zanegoose             # Goose (if installed)
```

---

## Local gateway endpoints

Default base: `http://127.0.0.1:8080`

```text
OpenAI-compatible:      http://127.0.0.1:8080/zanellm/v1
OpenAI Responses-style: http://127.0.0.1:8080/openai
Anthropic-compatible:   http://127.0.0.1:8080/anthropic
```

Use the local key written by `zane setup` when a tool asks for base URL + API key.

---

## Public install rules (important)

1. Public `master` has **no** bundled admin API key  
2. Every machine/user must run **their own** `zane setup`  
3. Do **not** copy from an admin machine:
   - `backend/open_webui/data/`
   - `.webui_secret_key`
   - launcher/env secret files
   - `~/.config/zane-cli/`
4. Never commit tokens, DB files, or credentials

---

## Verify install

```bash
zane status
zane doctor
zane models
```

Expected:

- Status shows Artemisia upstream configured
- Models list includes at least your plan’s chat models
- With a full Artemisia key: `gpt-5.5`, often `gpt-image-2` / `seedance-2.0`
- GPT-only keys may show chat models only (no image/video)

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Empty model picker | Run `zane setup`, then `zaneupdate`, hard-refresh browser |
| “Not authenticated” / 401 on models | Token missing/invalid — re-run `zane setup` |
| Chat blocked after one error | Current master unlocks after errors; hard-refresh old stuck sessions |
| Image/video models missing | Your Artemisia plan/key may be chat-only |
| `zane: command not found` | Add `~/.local/bin` to PATH, or re-run `./integrations/zane-cli/bin/zane install` |
| Port already in use | Stop other ZaneChat/Aeryn process on 8080, or set a different port in your env/start script |
| Copied admin data and broken install | Delete local `backend/open_webui/data` + re-run clean `zane setup` |

---

## Project names

| Name | Meaning |
| --- | --- |
| **Aeryn** | Product / this repo |
| **ZaneChat** | Web UI + gateway |
| **ZaneApp** | Desktop app |
| **ZaneCLI** | Terminal UI |
| **ZaneCode** | Full package that installs/connects everything |

---

## Security

Do not commit:

- Artemisia access tokens or model API keys
- `backend/open_webui/data/` (includes `webui.db`)
- `.webui_secret_key`
- anything under `~/.config/zane-cli/`

---

## License

See `LICENSE` and related notice files in this repository.
