import { Box, Button, TextField, Typography } from "@mui/material"
import { useRef } from "react"

export function EnvironmentForm({ onSectionSave }) {
  const form = useRef({
    jupyterPort: "40019"
  })

  const handleSave = () => {
    const section = {
      jupyter: {
        endpoint: `localhost:${form.current.jupyterPort}`
      }
    }

    onSectionSave("environment", section)
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6">Environment Configuration</Typography>

      <TextField
        label="Jupyter Notebook Port"
        type="number"
        defaultValue="40019"
        onChange={(e) => (form.current.jupyterPort = e.target.value)}
      />

      <Button variant="contained" color="success" onClick={handleSave}>
        Save environment section
      </Button>
    </Box>
  )
}