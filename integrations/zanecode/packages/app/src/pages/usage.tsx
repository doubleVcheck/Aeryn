import { Icon } from "@opencode-ai/ui/icon"
import { useNavigate } from "@solidjs/router"
import { createMemo, createResource, For, Match, Show, Switch } from "solid-js"

type UsageResponse = {
  configured: boolean
  message?: string
  account?: {
    base_url: string
    user_id?: string | null
    profile_url?: string | null
    token_list_url?: string | null
    models_url?: string | null
    profile?: Record<string, unknown> | null
    tokens?: Record<string, unknown>[] | null
    models?: unknown
  } | null
  provider?: {
    provider: string
    base_url: string
    usage_url: string
    usage: Record<string, unknown>
  } | null
}

const usageEndpoints = ["http://127.0.0.1:8080/api/v1/zane/usage", "http://localhost:8080/api/v1/zane/usage"]

async function fetchUsage(): Promise<UsageResponse> {
  let lastError: unknown
  for (const endpoint of usageEndpoints) {
    try {
      const response = await fetch(endpoint)
      const body = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(typeof body?.detail === "string" ? body.detail : response.statusText)
      return body
    } catch (error) {
      lastError = error
    }
  }
  throw lastError instanceof Error ? lastError : new Error("ZaneChat usage endpoint is unavailable")
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

function usageRoot(usage: Record<string, unknown> | undefined) {
  if (!usage) return {}
  if (isRecord(usage.data)) return usage.data
  return usage
}

function numberFrom(root: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = root[key]
    if (typeof value === "number" && Number.isFinite(value)) return value
    if (typeof value === "string" && value.trim() !== "") {
      const parsed = Number(value)
      if (Number.isFinite(parsed)) return parsed
    }
  }
}

function boolFrom(root: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = root[key]
    if (typeof value === "boolean") return value
    if (typeof value === "string") return ["true", "1", "yes"].includes(value.toLowerCase())
  }
  return false
}

function formatNumber(value: number | undefined) {
  if (value === undefined) return "Not reported"
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)
}

function formatPercent(value: number | undefined) {
  if (value === undefined) return "Not reported"
  return `${Math.max(0, Math.min(100, value)).toFixed(0)}%`
}

function modelRows(root: Record<string, unknown>, tokens?: Record<string, unknown>[] | null) {
  if (Array.isArray(tokens) && tokens.length > 0) {
    return tokens.map((item, index) => ({
      id: String(item.name ?? item.token_name ?? item.id ?? `token-${index + 1}`),
      group: String(item.group ?? ""),
      used: numberFrom(item, ["used_quota", "total_used", "used", "quota_used"]),
      limit: numberFrom(item, ["remain_quota", "total_available", "available_quota", "quota", "quota_limit"]),
    }))
  }
  const raw = root.model_limits ?? root.models ?? root.model_usage ?? root.model_stats
  if (Array.isArray(raw)) {
    return raw
      .filter(isRecord)
      .map((item, index) => ({
        id: String(item.model ?? item.model_id ?? item.name ?? `model-${index + 1}`),
        group: "",
        used: numberFrom(item, ["used_quota", "used", "total_quota", "quota_used", "usage"]),
        limit: numberFrom(item, ["quota_limit", "limit", "max_quota", "granted_quota"]),
      }))
  }
  if (isRecord(raw)) {
    return Object.entries(raw).map(([id, value]) => {
      const item = isRecord(value) ? value : { used: value }
      return {
        id,
        group: "",
        used: numberFrom(item, ["used_quota", "used", "total_quota", "quota_used", "usage"]),
        limit: numberFrom(item, ["quota_limit", "limit", "max_quota", "granted_quota"]),
      }
    })
  }
  return []
}

export default function UsagePage() {
  const navigate = useNavigate()
  const [usage, { refetch }] = createResource(fetchUsage)
  const accountRoot = createMemo(() => usageRoot(usage()?.account?.profile ?? undefined))
  const providerRoot = createMemo(() => usageRoot(usage()?.provider?.usage ?? undefined))
  const root = createMemo(() => (Object.keys(accountRoot()).length > 0 ? accountRoot() : providerRoot()))
  const granted = createMemo(() => numberFrom(root(), ["quota", "granted_quota", "total_granted", "total_quota", "quota_limit"]))
  const used = createMemo(() => numberFrom(root(), ["used_quota", "total_used", "used", "used_amount", "quota_used"]))
  const available = createMemo(() => numberFrom(root(), ["total_available", "available_quota", "remaining_quota", "remain_quota", "balance"]))
  const requests = createMemo(() => numberFrom(root(), ["request_count", "requests", "total_requests"]))
  const unlimited = createMemo(() => boolFrom(root(), ["unlimited_quota", "unlimited"]))
  const percent = createMemo(() => {
    if (unlimited()) return undefined
    const total = granted()
    const spent = used()
    if (!total || spent === undefined) return undefined
    return (spent / total) * 100
  })
  const rows = createMemo(() => modelRows(root(), usage()?.account?.tokens).slice(0, 20))
  const accountName = createMemo(() => {
    const profile = accountRoot()
    const name = String(profile.display_name ?? profile.username ?? profile.name ?? "").trim()
    const email = String(profile.email ?? "").trim()
    if (name && email) return `${name} <${email}>`
    return name || email || "artemisiahub profile"
  })

  return (
    <div class="zane-usage-page">
      <header class="zane-usage-header">
        <button type="button" onClick={() => navigate("/")} aria-label="Back to home">
          <Icon name="arrow-left" size="small" />
        </button>
        <div>
          <p>Zane usage</p>
          <h1>artemisiahub profile</h1>
        </div>
        <button type="button" onClick={() => void refetch()}>
          <Icon name="status" size="small" />
          <span>Refresh</span>
        </button>
      </header>

      <Switch>
        <Match when={usage.loading}>
          <div class="zane-usage-state">Loading usage from ZaneChat...</div>
        </Match>
        <Match when={usage.error}>
          <div class="zane-usage-state">
            <b>Usage unavailable</b>
            <span>{usage.error instanceof Error ? usage.error.message : "Could not fetch usage data."}</span>
          </div>
        </Match>
        <Match when={usage()}>
          {(payload) => (
            <Show
              when={payload().configured && (payload().account || payload().provider)}
              fallback={
                <div class="zane-usage-state">
                  <b>Not configured yet</b>
                  <span>{payload().message ?? "Run zanecode once and enter your artemisiahub access token."}</span>
                </div>
              }
            >
              <>
                  <section class="zane-usage-summary">
                    <div>
                      <span>Used</span>
                      <strong>{formatNumber(used())}</strong>
                    </div>
                    <div>
                      <span>Available</span>
                      <strong>{unlimited() ? "Unlimited" : formatNumber(available())}</strong>
                    </div>
                    <div>
                      <span>Granted</span>
                      <strong>{unlimited() ? "Unlimited" : formatNumber(granted())}</strong>
                    </div>
                    <div>
                      <span>Utilization</span>
                      <strong>{unlimited() ? "Unlimited" : formatPercent(percent())}</strong>
                    </div>
                    <div>
                      <span>Requests</span>
                      <strong>{formatNumber(requests())}</strong>
                    </div>
                  </section>

                  <section class="zane-usage-meter" aria-label="Usage utilization">
                    <div>
                      <span style={{ width: `${unlimited() ? 100 : Math.max(0, Math.min(100, percent() ?? 0))}%` }} />
                    </div>
                    <p>
                      {usage()?.account ? accountName() : (usage()?.provider?.provider ?? "provider")} via{" "}
                      {usage()?.account?.base_url ?? usage()?.provider?.base_url ?? ""}
                    </p>
                  </section>

                  <section class="zane-usage-table">
                    <div class="zane-usage-table-header">
                      <span>{usage()?.account?.tokens ? "Account tokens" : "Model limits"}</span>
                      <small>{rows().length > 0 ? `${rows().length} shown` : "No rows reported"}</small>
                    </div>
                    <Show
                      when={rows().length > 0}
                      fallback={<div class="zane-usage-empty">artemisiahub did not return token or per-model usage rows.</div>}
                    >
                      <For each={rows()}>
                        {(row) => (
                          <div class="zane-usage-row">
                            <span>{row.group ? `${row.id} (${row.group})` : row.id}</span>
                            <span>{formatNumber(row.used)}</span>
                            <span>{formatNumber(row.limit)}</span>
                          </div>
                        )}
                      </For>
                    </Show>
                  </section>
              </>
            </Show>
          )}
        </Match>
      </Switch>
    </div>
  )
}
