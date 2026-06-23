import { Box, TextField, Typography } from "@mui/material"
import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { splitEndpoint } from "../configFormUtils"
import { ConfigForm } from "../ConfigForm"
import { portField } from "../formValidation"
import { SaveButton } from "../Agents/Agents.styled"

export function EnvironmentForm() {
  const { updateField, getDefaultSection } = useConfig()
  const { showToast } = useToast()

  const envDefaults = getDefaultSection("environment") || {}
  const jupyter = splitEndpoint(envDefaults.jupyter_endpoint, "localhost", 40019)

  const form = useRef({
    jupyter_port: jupyter.port
  })

  const handleSave = () => {
    updateField("environment", {
      jupyter_endpoint: `${jupyter.host}:${form.current.jupyter_port}`
    })
    showToast({ message: "Environment settings applied", severity: "success" })
  }

  return (
    <ConfigForm onSubmit={handleSave}>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Typography variant="h6">Environment Configuration</Typography>

        <TextField
          label="Jupyter Notebook Port"
          type="number"
          size="small"
          required
          defaultValue={form.current.jupyter_port}
          onChange={(e) => {
            form.current.jupyter_port = Number(e.target.value)
          }}
          {...portField}
        />

        <SaveButton variant="contained" color="success" type="submit">
          Apply environment settings
        </SaveButton>
      </Box>
    </ConfigForm>
  )
}
