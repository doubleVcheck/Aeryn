const reset = "\x1b[0m"
const bold = "\x1b[1m"
const dim = "\x1b[90m"

function wordmark(pad = "") {
  return [`${pad}${bold}zanecode${reset}`, `${pad}${dim}Use AI from wherever you are${reset}`]
}

export function sessionEpilogue(input: { title: string; sessionID?: string }) {
  const weak = (text: string) => `${dim}${text.padEnd(10, " ")}${reset}`
  return [
    ...wordmark("  "),
    "",
    `  ${weak("Session")}${bold}${input.title}${reset}`,
    `  ${weak("Continue")}${bold}zanecode -s ${input.sessionID}${reset}`,
    "",
  ].join("\n")
}
