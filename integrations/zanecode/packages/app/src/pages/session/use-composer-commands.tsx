import { useCommand, type CommandOption } from "@/context/command"
import { useLanguage } from "@/context/language"
import { useLocal } from "@/context/local"
import { useSettings } from "@/context/settings"
import { useDialog } from "@opencode-ai/ui/context/dialog"
import { getCursorPosition, setCursorPosition } from "@/components/prompt-input/editor-dom"
import { useSessionLayout } from "./session-layout"
import { createSessionOwnership } from "./session-ownership"

const withCategory = (category: string) => {
  return (option: Omit<CommandOption, "category">): CommandOption => ({
    ...option,
    category,
  })
}

export const useComposerCommands = () => {
  const command = useCommand()
  const dialog = useDialog()
  const language = useLanguage()
  const local = useLocal()
  const settings = useSettings()
  const { sessionKey } = useSessionLayout()
  const sessionOwnership = createSessionOwnership(sessionKey)
  const modelCommand = withCategory(language.t("command.category.model"))
  const agentCommand = withCategory(language.t("command.category.agent"))
  const hasVariants = () => local.model.variant.list().length > 0
  const setVariant = (preferred: string[]) => {
    const variants = local.model.variant.list()
    const selected = preferred.find((item) => variants.includes(item))
    if (selected) {
      local.model.variant.set(selected)
      return
    }
    local.model.variant.set(variants[0])
  }
  const setStrongestVariant = () => {
    const variants = local.model.variant.list()
    const order = ["none", "minimal", "low", "medium", "high", "xhigh", "max", "thinking"]
    const ranked = [...variants].sort((a, b) => order.indexOf(b) - order.indexOf(a))
    local.model.variant.set(ranked[0])
  }

  const chooseModel = async () => {
    const owner = sessionOwnership.capture()
    const editor = document.querySelector<HTMLElement>('[data-component="prompt-input"]')
    const selection = window.getSelection()
    const cursor =
      editor && selection?.rangeCount && editor.contains(selection.anchorNode) ? getCursorPosition(editor) : null
    const restoreComposer = () => {
      // Kobalte restores focus during its teardown effect; defer past it so the
      // composer keeps focus and the caret returns to where the user left it.
      requestAnimationFrame(() => {
        const editor = document.querySelector<HTMLElement>('[data-component="prompt-input"]')
        if (!editor) return
        editor.focus()
        if (cursor !== null) setCursorPosition(editor, cursor)
      })
    }
    const { DialogSelectModel } = await import("@/components/dialog-select-model")
    owner.run(() => {
      void dialog.show(() => <DialogSelectModel model={local.model} />, restoreComposer)
    })
  }

  command.register("composer", () => [
    modelCommand({
      id: "model.choose",
      title: language.t("command.model.choose"),
      description: language.t("command.model.choose.description"),
      keybind: "mod+'",
      slash: "model",
      onSelect: chooseModel,
    }),
    modelCommand({
      id: "model.variant.cycle",
      title: language.t("command.model.variant.cycle"),
      description: language.t("command.model.variant.cycle.description"),
      keybind: "shift+mod+d",
      slash: "thinking",
      onSelect: () => local.model.variant.cycle(),
    }),
    modelCommand({
      id: "model.variant.fast",
      title: "Fast thinking",
      description: "Use the lightest available thinking effort",
      slash: "fast",
      disabled: !hasVariants(),
      onSelect: () => setVariant(["none", "minimal", "low", "medium"]),
    }),
    modelCommand({
      id: "model.variant.ultra",
      title: "Ultra thinking",
      description: "Use a high thinking effort",
      slash: "ultra",
      disabled: !hasVariants(),
      onSelect: () => setVariant(["high", "xhigh", "max", "medium"]),
    }),
    modelCommand({
      id: "model.variant.ultracode",
      title: "Ultracode thinking",
      description: "Use the strongest available thinking effort",
      slash: "ultracode",
      disabled: !hasVariants(),
      onSelect: setStrongestVariant,
    }),
    agentCommand({
      id: "agent.cycle",
      title: language.t("command.agent.cycle"),
      description: language.t("command.agent.cycle.description"),
      keybind: "mod+.",
      slash: "agent",
      disabled: !settings.visibility.customAgents(),
      onSelect: () => local.agent.move(1),
    }),
    agentCommand({
      id: "agent.cycle.reverse",
      title: language.t("command.agent.cycle.reverse"),
      description: language.t("command.agent.cycle.reverse.description"),
      keybind: "shift+mod+.",
      disabled: !settings.visibility.customAgents(),
      onSelect: () => local.agent.move(-1),
    }),
  ])
}
