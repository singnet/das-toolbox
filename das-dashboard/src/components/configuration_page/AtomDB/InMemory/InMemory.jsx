import { Button } from "@mui/material";
import { useConfig } from "../../../global_providers/ConfigurationProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useRef } from "react";
import { ActionButtonContainer } from "../AtomDBStyled";
import { SaveButton } from "../../Agents/Agents.styled";

export function InMemoryOptions() {

  const { updateField } = useConfig()
  const { showToast } = useToast()

  const section = useRef({
    type: "inmemorydb"
  })

  const handleSave = () => {
    updateField(
      "atomdb",
      structuredClone(section.current)
    )
    showToast({ message: "AtomDB settings applied", severity: "success" })
  }

  return (
    <ActionButtonContainer>
      <SaveButton 
        variant="contained" 
        color="success" 
        onClick={handleSave} 
      >
        Save AtomDB Section
      </SaveButton>
    </ActionButtonContainer>
  )
}