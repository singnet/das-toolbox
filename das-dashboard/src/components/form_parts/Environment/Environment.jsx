import { Box, Button, TextField, Typography } from "@mui/material"
import { useRef } from "react"
import { useConfig } from "../../global_components/ConfigurationProvider"
import { useToast } from "../../global_components/ToastProvider"

export function EnvironmentForm({ onSectionSave }) {

  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()
  const defaults = getDefault()

  const section = useRef({
    jupyter: {
      endpoint: `localhost:40019`
    }
  })

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6">Environment Configuration</Typography>

      <TextField
        label="Jupyter Notebook Port"
        type="number"
        defaultValue={ defaults.environment.jupyter.endpoint.split(":")[1] || "40019"}
        onChange={(e) => (form.current.jupyterPort = e.target.value)}
      />

      <Button variant="contained" color="success" onClick={() => {
        updateSection("environment", structuredClone(section.current))
        showToast("Environment saved successfully!")
      }}>
        Save environment section
      </Button>
    </Box>
  )
}