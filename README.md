<img width="500" height="540" alt="aeryn-logo-Photoroom" src="https://github.com/user-attachments/assets/d9bfe5d9-a4c6-4ec9-bf98-e654f54f47ff" />

# ZaneCode

ZaneCode is the Zane AI workspace. It gives you one account-backed setup for chat, desktop, terminal, and coding CLIs.

## What You Get

- **ZaneChat**: web chat and local AI gateway.
<img width="1919" height="924" alt="image" src="https://github.com/user-attachments/assets/dd9b7569-28f9-4226-83d2-5fc99eb082d5" />

- **ZaneApp**: desktop app for coding sessions.
<img width="1920" height="1048" alt="image" src="https://github.com/user-attachments/assets/93001f18-b001-4874-9eb1-a40a970aba5c" />

- **ZaneCLI**: terminal UI through `zanecli` and `zanecode`
<img width="1908" height="951" alt="image" src="https://github.com/user-attachments/assets/d68f1d1b-cf6b-4ac3-8d0e-ff808342515a" />

- **CLI wrappers**: run popular coding CLIs through your Zane models with commands like `zanecc`, `zanegpt`, `zaneoc`, `zaneh`, and `zanegrokcli`.
Example from **zanegpt**:

<img width="1913" height="413" alt="image" src="https://github.com/user-attachments/assets/ebe79d76-b176-437c-9275-2f26480222c9" />

## How It Works

ZaneCode connects to your artemisiahub.com account with an access token from your profile.

1. Open `https://artemisiahub.com`.
2. Sign in and go to your profile.
3. Create or copy an access token.
4. Run the ZaneCode installer.
5. Paste the token only into the local secure prompt when asked.

The setup then creates or reuses your model API token, syncs ModelSquare provider groups and models, configures ZaneChat, and writes local CLI/app config.

Your artemisiahub access token is not committed to the repo. Local credentials live under:

```text
~/.config/zane-cli/credentials.env
~/.config/zane-cli/config.json
```

## Install

```bash
git clone https://github.com/zephyrzane/zanecode.git
cd zanecode
./integrations/zane-cli/bin/zane install
zane setup --upstream-base https://artemisiahub.com/v1
zanechat
```

`zane setup` prompts for the current user's artemisiahub access token and creates or reuses that user's model API token. The public build defaults to Artemisia Hub models (`https://artemisiahub.com/v1`, default chat model `gpt-5.5`, pinned `gpt-5.5` / `gpt-image-2` / `seedance-2.0`) but does not include a default admin API key. Do not copy an admin installation's `backend/open_webui/data`, `.webui_secret_key`, launcher environment, or `~/.config/zane-cli` directory into a user installation.

If `zane` is not available yet from your shell, run the local installer directly:

```bash
./integrations/zane-cli/bin/zane install
```

## Main Commands

```bash
zanechat       # start ZaneChat web UI and gateway
zaneapp        # start ZaneApp
zanecli        # start ZaneCLI
zanecode       # alias for ZaneCLI
zaneupdate     # refresh models from artemisiahub ModelSquare
zane models    # list models exposed by the local gateway
zane use MODEL # set the default model for wrappers
zane status    # show local bridge status
```

## Use Zane Models In Other CLIs

ZaneCode installs wrapper commands so you can keep using familiar terminal tools while routing them through ZaneLLM.

```bash
zanegpt        # Codex-style CLI through Zane
zanecodex      # Codex-style CLI through Zane
zanecc         # Claude Code through Zane
zaneoc         # open coding sessions through Zane
zaneh          # Hermes through Zane
zanehermes     # Hermes through Zane
zanegrokcli    # Grok CLI through Zane
```

The original tools stay untouched. The `zane*` commands use your local Zane config and model list.

## Refresh Models

When artemisiahub ModelSquare adds, removes, or renames models, run:

```bash
zaneupdate
```

This refreshes provider groups, removes stale local model entries, and updates ZaneChat/ZaneCLI/ZaneApp model catalogs.

## Local Gateway

ZaneCode exposes local compatible endpoints for apps and CLIs:

```text
OpenAI-compatible:      http://127.0.0.1:8080/zanellm/v1
OpenAI Responses-style: http://127.0.0.1:8080/openai
Anthropic-compatible:   http://127.0.0.1:8080/anthropic
```

Use these with the locally generated API key from ZaneCode config when a tool asks for a base URL and key.

## Project Names

- **ZaneChat** is the web UI and gateway.
- **ZaneApp** is the desktop app.
- **ZaneCLI** is the terminal UI.
- **ZaneCode** is the full package that installs and connects all of them.

## Security

Do not commit API keys, access tokens, local databases, generated app data, or files from `~/.config/zane-cli`.
