import { Box, TextField, Typography } from "@mui/material"
import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { splitEndpoint, parsePortValue } from "../configFormUtils"
import { ConfigForm } from "../ConfigForm"
import { portField } from "../formValidation"
import { SaveButton } from "../Agents/Agents.styled"

export function VaultForm() {
  const { updateField, getDefaultSection } = useConfig()
  const { showToast } = useToast()

  const vaultDefaults = getDefaultSection("vault") || {}
  const vault = splitEndpoint(vaultDefaults.endpoint, "localhost", 8200)

  const form = useRef({
    vault_port: vault.port
  })

  const handleSave = () => {
    updateField("vault", {
      endpoint: `${vault.host}:${form.current.vault_port}`
    })
    showToast({ message: "Vault settings applied", severity: "success" })
  }

  return (
    <ConfigForm onSubmit={handleSave}>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Typography variant="h6">Vault Configuration</Typography>

        <TextField
          label="Vault (OpenBao) Port"
          type="number"
          size="small"
          required
          defaultValue={form.current.vault_port}
          onChange={(e) => {
            form.current.vault_port = parsePortValue(e.target.value)
          }}
          {...portField}
        />

        <SaveButton variant="contained" color="success" type="submit">
          Apply vault settings
        </SaveButton>
      </Box>
    </ConfigForm>
  )
}
