import { TextAttributes } from "@opentui/core"
import { useTheme } from "../context/theme"

export function Logo() {
  const { theme } = useTheme()

  return (
    <box flexDirection="column" alignItems="center" gap={1}>
      <text fg={theme.text} attributes={TextAttributes.BOLD} selectable={false}>
        Zane
      </text>
      <text fg={theme.textMuted} selectable={false}>
        Use AI from wherever you are
      </text>
    </box>
  )
}
