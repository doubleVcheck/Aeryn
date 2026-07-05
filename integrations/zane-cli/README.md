# Zane CLI Bridge

This package does not replace Claude Code, Codex CLI, Hermes, Goose, Gemini CLI, Cursor, or other installed CLIs.
It installs Zane-prefixed wrapper commands that launch those tools with ZaneLLM endpoint settings.

Normal commands stay normal:

```bash
claude
codex
gemini
opencode
hermes
```

Zane-powered commands:

```bash
zanei        # install/reinstall Zane wrapper links
zanechat     # ZaneChat web server through artemisiahub
zanecli      # Zane first-party CLI/TUI through ZaneLLM
zanecode     # Alias for zanecli
zaneapp      # Zane App desktop UI through ZaneLLM
zaned        # disable Zane wrapper links, keep zane manager
zanecc        # Claude Code through ZaneLLM Anthropic-compatible API
zanegpt       # Codex CLI through ZaneLLM OpenAI/Responses-compatible API
zanegrok      # Grok Build CLI through a generated ZaneLLM Grok model profile
zanegrokcli   # Claude-Code style Grok run through ZaneLLM Anthropic-compatible API
zanexai       # Alias for zanegrok
zanecodex     # Codex CLI through ZaneLLM OpenAI/Responses-compatible API
zaneoc        # compatible coding CLI through ZaneLLM OpenAI-compatible API
zaneopencode  # compatible coding CLI through ZaneLLM OpenAI-compatible API
zanea         # Aider through ZaneLLM OpenAI-compatible API
zaneaider     # Aider through ZaneLLM OpenAI-compatible API
zanecontinue  # Continue CLI through a generated ZaneLLM config
zanecn        # Short Continue CLI wrapper
zaneh         # Hermes through an isolated ZaneLLM Hermes profile
zanehermes    # Hermes through an isolated ZaneLLM Hermes profile
zanegoose     # Goose through OpenAI-compatible env vars, when goose is installed
```

Install local command shims:

```bash
cd /path/to/zanechat
node integrations/zane-cli/bin/zane install
zane setup
```

After `~/.local/bin` is on `PATH`, use:

```bash
zanechat
zane status
zane models
zane use claude-sonnet-5
zane apps
zanecli --help
zanecode --help
zaneapp
zane cli --help
zane code --help
zanecc --help
zanecodex --help
```

Change the default model for every Zane wrapper:

```bash
zane models
zane models grok
zane use grok-4.3-fast
zane use claude-sonnet-5
```

`zane use <model-id>` writes the default to `~/.config/zane-cli/config.json`.
New wrapper sessions use that model automatically. Existing running sessions keep the model they started with.

Disable the app wrappers while keeping the manager command:

```bash
zane restore
```

Short aliases:

```bash
zanei
zane i
zaned
zanedisable
zane d
zane disable
```

`zane restore` removes the Zane app wrapper links it installed and restores any backed-up `zane*` files.
It keeps the `zane` manager link, so you can run this later:

```bash
zane install
```

To fully remove the manager link too:

```bash
zane restore --remove-manager
zane delete
```

It does not remove `~/.config/zane-cli/credentials.env` by default. To remove generated bridge config too:

```bash
zane restore --purge-config
```

First run setup:

```bash
zanecode
```

If no token is configured, `zanecode` prompts locally for an artemisiahub access token. That token is used locally to reuse or create a `zanecode` model API token, fetch the real `sk-` key, store credentials in `~/.config/zane-cli/credentials.env` with `0600` permissions, configure ZaneChat's OpenAI-compatible provider as `https://artemisiahub.com/v1`, and set up `zanecli` and `zaneapp` to use the local ZaneChat gateway.

The management token and the model API key are different:

- `ZANE_ARTEMISIA_ACCESS_TOKEN`: artemisiahub access token.
- `ZANELLM_API_KEY`: generated or reused model API key used by ZaneChat, Zane CLI, Zane App, and wrapper CLIs.

You can run setup explicitly:

```bash
zane setup
zane setup --force
zane setup --upstream-base https://artemisiahub.com/v1
zane setup --force --account-id 1
zane setup --force --account-id 1 --token-name zanecode
```

Refresh models after artemisiahub ModelSquare changes:

```bash
zaneupdate
zane update
zane update --json
```

This uses the stored artemisiahub access token, refreshes provider groups and model lists, removes stale local groups/models from Zane config, and rewrites the ZaneChat provider config. It does not delete remote artemisiahub tokens.

Configuration is read from:

- `~/.config/zane-cli/config.json`
- `~/.config/zane-cli/credentials.env`
- environment overrides: `ZANELLM_BASE_URL`, `ZANE_UPSTREAM_BASE_URL`, `ZANELLM_MODEL`, `ZANELLM_REASONING`, `ZANELLM_API_KEY`, `ZANE_ARTEMISIA_ACCESS_TOKEN`, `ZANE_ARTEMISIA_ACCOUNT_ID`

Universal app settings:

- OpenAI-compatible base URL: `http://127.0.0.1:8080/zanellm/v1`
- OpenAI Responses base URL: `http://127.0.0.1:8080/openai`
- Anthropic-compatible base URL: `http://127.0.0.1:8080/anthropic`
- artemisiahub upstream base URL: `https://artemisiahub.com/v1`
- Model names: run `zane models`

Model pickers:

- `zanecli` / `zanecode` / `zane cli` / `zane code`: native Zane CLI/TUI. It reads ZaneLLM settings automatically and discovers models from `GET /zanellm/v1/models`.
- `zaneapp` / `zane app`: native desktop app. It starts the Electron app with the same ZaneLLM config and model catalog.
- `zanegpt` / `zanecodex`: generates a Codex model catalog from `zane models`, so `/model` inside Codex shows ZaneLLM models.
- `zaneopencode`: generates a compatible config with every ZaneLLM model.
- `zanecontinue`: generates a Continue config with every ZaneLLM model.
- `zanecc`, `zaneh`, `zaneaider`, `zanegrok`, `zanegrokcli`, and `zanegoose`: use the default from `zane use <model-id>` unless you pass that tool's own model flag.
- For one-off sessions, use the upstream flag when supported, for example `zanegpt -m grok-4.3-fast`.

Grok:

- `zanegrok` uses the official Grok Build CLI when `grok` is installed, otherwise it falls back to `npx @xai-official/grok`.
- It writes only a managed `[model.zanellm_grok]` block to `~/.grok/config.toml`.
- `zanegrokcli` uses Claude Code directly with a Grok model from `zane models grok`, avoiding API keys on command-line args.

Gemini CLI and Cursor currently do not expose complete OpenAI-compatible endpoint overrides for their full agent surfaces. The wrapper reports that clearly instead of silently launching them against their original backends.

Native zanecode:

```bash
zanechat
zanecli
zanecode
zane cli
zane code
zaneapp
zane app
zanecli models zanellm
zanecli run --print-logs "explain this project"
```

`zanecli` is the first-party CLI path. `zanecode` remains an alias. `zaneapp` is the first-party desktop UI path. `zaneoc` remains an upstream compatibility wrapper.
