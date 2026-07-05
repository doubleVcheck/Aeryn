# Zane Agent OSS Base Research

Date: 2026-07-05

## Decision

Use OpenCode as the base for a first-party Zane coding agent.

The Zane project should keep the existing wrapper bridge for compatibility, but the native CLI/TUI/desktop app should be a Zane-branded OpenCode fork with a first-class ZaneLLM provider.

## Why OpenCode

- MIT license.
- Ships a real terminal agent and a desktop app in one repo.
- Has model/provider dialogs, sessions, terminal integration, permissions, agents, plugins, and server APIs already.
- Uses AI SDK providers and supports custom OpenAI-compatible providers.
- Internally supports config-provided providers and per-model request overrides, so a single ZaneLLM endpoint can serve every Zane model.
- The UI/product layer is already mature enough to brand, instead of rebuilding the whole app.

Pinned research snapshot:

- Repo: `https://github.com/anomalyco/opencode`
- Local clone: `/tmp/zanellm-oss-research/opencode`
- Commit: `b7e4f1e`
- Version observed: `1.17.13`

## What To Change In The Fork

1. Rename product surfaces to zanecode or Zane.
2. Add a built-in `zanellm` provider.
3. Read Zane settings from:
   - `~/.config/zane-cli/config.json`
   - `~/.config/zane-cli/credentials.env`
   - `ZANELLM_BASE_URL`
   - `ZANELLM_API_KEY`
   - `ZANELLM_MODEL`
   - `ZANELLM_REASONING`
4. Auto-discover models from `GET <base>/zanellm/v1/models`.
5. Generate OpenCode model entries from fetched Zane models.
6. Add safer model capability inference:
   - Claude/Anthropic family
   - OpenAI/GPT family
   - Gemini
   - Grok/xAI
   - DeepSeek
   - GLM/Z.ai
   - Qwen
   - OpenRouter/gateway-routed models
7. Import Pi-style OpenAI-compatible reasoning compatibility where OpenCode is too generic:
   - `reasoning_effort`
   - `reasoning: { effort }`
   - `thinking: { type }`
   - `enable_thinking`
   - `chat_template_kwargs`
8. Brand the TUI and desktop app matte black with Zane logo/assets.
9. Keep upstream MIT license notices.

## Why Not T3 Code As The Base

T3 Code is a clean web/desktop GUI, but it is mostly a wrapper/orchestrator over other CLIs such as Codex, Claude, Cursor, and OpenCode. That repeats the same problem the bridge already has: every model picker and provider behavior depends on another tool's private config.

Useful as UI reference, not the core Zane agent.

Pinned research snapshot:

- Repo: `https://github.com/pingdotgg/t3code`
- Local clone: `/tmp/zanellm-oss-research/t3code`
- Commit: `6009720`

## Why Not Pi As The Base

Pi has the cleanest provider compatibility ideas and a strong hackable agent core. It is MIT and worth borrowing from, especially for OpenAI-compatible reasoning formats.

It does not currently give us a polished desktop app and terminal product layer. Using it as the main base means building more UI ourselves, which already failed the quality bar.

Pinned research snapshot:

- Repo: `https://github.com/earendil-works/pi`
- Local clone: `/tmp/zanellm-oss-research/pi`
- Commit: `ee24a9e`

## Why Not Crush As The Base

Crush has a strong TUI aesthetic, but its current license is FSL-1.1-MIT, not straight MIT today. That is a poor fit for a publishable fork that should be cleanly reusable now.

Use it only for UI inspiration.

Pinned research snapshot:

- Repo: `https://github.com/charmbracelet/crush`
- Local clone: `/tmp/zanellm-oss-research/crush`

## Next Implementation Step

Create a `zanecode` source fork from OpenCode, then patch only the minimum surfaces needed first:

1. CLI command and package identity.
2. ZaneLLM provider and model discovery.
3. TUI branding.
4. Desktop branding.
5. Build/run verification.

Do not revive the deleted scratch app.

## Current Fork Location

- Source fork: `integrations/zanecode`
- Launcher: `integrations/zanecode/bin/zanecode`
- Bridge aliases: `zanecode` and `zane code`

`zaneoc` remains the compatibility wrapper around the user's installed upstream OpenCode. `zanecode` is the native first-party zanecode CLI/TUI path.

## Prototype Patch

Patch file:

- `integrations/zane-cli/patches/opencode-zanellm-model-discovery.patch`

Applied and tested against the temporary OpenCode clone at `/tmp/zanellm-oss-research/opencode`.

Verified:

- `bun install` at OpenCode repo root.
- `bun typecheck` from `packages/opencode`.
- `OPENCODE_CONFIG_CONTENT` with a `zanellm` OpenAI-compatible provider and no manual `models` block now auto-fetches models from `http://127.0.0.1:8080/zanellm/v1/models`.
- The discovered model list removes bad ANSI suffix artifacts such as `[1m]`.

Sample discovered models:

- `zanellm/claude-sonnet-5`
- `zanellm/gpt-5.5`
- `zanellm/grok-4.3-fast`
- `zanellm/deepseek-*` when present upstream
