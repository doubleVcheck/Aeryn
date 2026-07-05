# ZaneCode

ZaneCode is the Zane AI workspace:

- **ZaneChat**: the web chat and local gateway.
- **Zane CLI**: terminal/TUI access through `zanecli` and `zanecode`.
- **Zane App**: desktop app access through `zaneapp`.
- **Zane wrappers**: `zanegpt`, `zanecc`, `zaneoc`, `zaneh`, and other launcher commands that route coding CLIs through ZaneLLM.

The setup flow uses a local **artemisiahub access token** to create or reuse provider API tokens, sync available models, configure ZaneChat, and keep CLI/app model catalogs current. Secrets are stored locally under `~/.config/zane-cli` and are not meant to be committed.

## Quick Start

```bash
git clone https://github.com/zephyrzane/zanecode.git
cd zanecode
zane install
zanecode
```

On first run, `zanecode` prompts locally for an artemisiahub access token. The token is not printed in the terminal.

## Main Commands

```bash
zanechat       # start ZaneChat web UI and gateway
zanecli        # start the Zane terminal UI
zanecode       # alias for zanecli
zaneapp        # start the desktop app
zaneupdate     # refresh ModelSquare provider groups and models
zane models    # list models exposed by the local gateway
zane use MODEL # set the default model for wrappers
zane status    # show local bridge status
```

## Wrapped CLIs

```bash
zanegpt        # Codex CLI through ZaneLLM
zanecodex      # Codex CLI through ZaneLLM
zanecc         # Claude Code through ZaneLLM
zaneoc         # compatible coding CLI through ZaneLLM
zaneh          # Hermes through ZaneLLM
zanegrokcli    # Grok-style coding session through ZaneLLM
```

## Refresh Models

When artemisiahub ModelSquare adds or removes models:

```bash
zaneupdate
```

This updates local provider groups, removes stale local model entries, rewrites the ZaneChat provider config, and reports skipped groups such as providers with no available models.

## Local Files

ZaneCode keeps generated credentials and bridge state outside the repo:

```text
~/.config/zane-cli/credentials.env
~/.config/zane-cli/config.json
```

Do not commit API keys, access tokens, local databases, or generated app data.

## Attribution

ZaneCode is maintained by Zephyr Zane and builds on Open WebUI and opencode-derived components.
