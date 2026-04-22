import { Button } from "@mui/material";
import { useConfig } from "../../global_components/ConfigurationProvider";
import { useToast } from "../../global_components/ToastProvider";
import { useRef } from "react";

export function InMemoryOptions({ onSave }){

    const { updateSection } = useConfig()
    const { showToast } = useToast()

    const section = useRef({
        "type": "inmemorydb"
    })

    return (
        <Button variant="contained" color="success" onClick={
        () => {
            updateSection("atomdb", structuredClone(section.current))
            showToast("AtomDB saved successfully!")
        }
        } 
        sx={{ mt: 2 }
        }>
              Save AtomDB Section
        </Button>
    )

}