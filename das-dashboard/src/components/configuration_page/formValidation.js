export const ipv4Input = {
  pattern: "((25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})",
  title: "Enter a valid IPv4 address"
}

export const portInput = {
  min: 1,
  max: 65535,
  step: 1
}

export const nonNegativeInput = {
  min: 0,
  step: 1
}

export const pathInput = {
  minLength: 1,
  title: "Enter a file or directory path"
}

export const idInput = {
  pattern: "[a-zA-Z0-9_-]+",
  minLength: 1,
  title: "Use letters, numbers, dashes, or underscores"
}

export function field(rules) {
  return { slotProps: { htmlInput: rules } }
}

export const ipv4Field = field(ipv4Input)
export const portField = field(portInput)
export const pathField = field(pathInput)
export const idField = field(idInput)

export const numberField = {
  slotProps: {
    htmlInput: {
      ...nonNegativeInput,
      onWheel: (event) => event.target.blur()
    }
  }
}
