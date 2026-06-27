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

export const elitismRateInput = {
  min: 0,
  max: 1,
  step: 0.01,
}

export const selectionRateInput = {
  min: 0,
  max: 1,
  step: 0.1,
}

export const initialRentTakeInput = {
  min: 0,
  max: 1,
  step: 0.05
}

export const spreadLowerInput = {
  min: 0,
  max: 1,
  step: 0.1
}

export const spreadUpperInput = {
  min: 0,
  max: 1,
  step: 0.1
}

export function field(rules) {
  return { slotProps: { htmlInput: rules } }
}

export const ipv4Field = field(ipv4Input)
export const portField = field(portInput)
export const pathField = field(pathInput)
export const idField = field(idInput)
export const elitismRateField = field(elitismRateInput)
export const selectionRateField = field(selectionRateInput)
export const initialRentField = field(initialRentTakeInput)
export const spreadLowerField = field(spreadLowerInput)
export const spreadUpperField = field(spreadLowerField)

export const numberField = {
  slotProps: {
    htmlInput: {
      ...nonNegativeInput,
      onWheel: (event) => event.target.blur()
    }
  }
}
