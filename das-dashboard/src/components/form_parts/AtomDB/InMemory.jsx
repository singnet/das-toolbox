import { Button } from "@mui/material";

export function InMemoryOptions({ onSave }){

    const section = {
        "type": "inmemorydb"
    }

    return (
        <Button variant="contained" color="success" onClick={() => onSave(section)} sx={{ mt: 2 }}>
              Save AtomDB Section
        </Button>
    )

}