import { Button } from "@mui/material";
import { useConfig } from "../../../global_providers/ConfigurationProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useRef } from "react";
import { ActionButtonContainer } from "../AtomDBStyled";

export function InMemoryOptions({ onSave }){

    const { updateSection } = useConfig()
    const { showToast } = useToast()

    return (
        <ActionButtonContainer>
            <Button 
              variant="contained" 
              color="success" 
              onClick={() => {}} 
            >
              Save AtomDB Section
            </Button>
        </ActionButtonContainer>
    )
}