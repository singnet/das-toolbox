import { useRef } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import { ActionButtonContainer } from "../AtomDBStyled"
import { SaveButton } from "../../Agents/Agents.styled"

export function InMemoryOptions() {
  const { updateField } = useConfig()
  const { showToast } = useToast()

  const form = useRef({
    atomdb_type: "inmemorydb"
  })

  const handleSave = () => {
    updateField("atomdb", structuredClone(form.current))
    showToast({ message: "AtomDB settings applied", severity: "success" })
  }

  return (
    <ActionButtonContainer>
      <SaveButton variant="contained" color="success" onClick={handleSave}>
        Apply AtomDB settings
      </SaveButton>
    </ActionButtonContainer>
  )
}
