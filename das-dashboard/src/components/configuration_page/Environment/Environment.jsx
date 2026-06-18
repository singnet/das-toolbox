import { Box, Button, TextField, Typography } from "@mui/material"
import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { SaveButton } from "../Agents/Agents.styled"

export function EnvironmentForm() {

  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()

  const currentEndpoint = getDefault("environment.jupyter.endpoint") || "localhost:40019"

  const form = useRef({
    jupyter_port: Number(currentEndpoint.split(":")[1]) || 40019
  })

  const handleSave = () => {
    updateField("environment", {
      jupyter_endpoint: `localhost:${form.current.jupyter_port}`
    })
    showToast({ message: "Environment saved successfully!", severity: "success" })
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6">Environment Configuration</Typography>

      <TextField
        label="Jupyter Notebook Port"
        type="number"
        size="small"
        defaultValue={form.current.jupyter_port}
        onChange={(e) => {
          form.current.jupyter_port = Number(e.target.value)
        }}
      />

      <SaveButton variant="contained" color="success" onClick={handleSave}>
        Save environment section
      </SaveButton>
    </Box>
  )
}