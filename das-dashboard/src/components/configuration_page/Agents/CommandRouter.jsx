import { useRef, useState } from "react"
import { TextField } from "@mui/material"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { buildAgentPayload, initCommandRouterForm, parsePortValue } from "../configFormUtils"
import { ConfigForm } from "../ConfigForm"
import { getAgentByKey } from "./agentRegistry"
import { AgentConnectionFields } from "./AgentConnectionFields"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  FieldGrid,
  SaveButton
} from "./Agents.styled"
import { portField } from "../formValidation"

export default function CommandRouterPanel() {
  const { updateField, getDefaults } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("command_router")

  const form = useRef(initCommandRouterForm(getDefaults()))
  const [, refreshView] = useState(0)

  const handleSave = () => {
    updateField("agents.command_router", buildAgentPayload(form.current))
    showToast({ message: `${agent.label} settings applied`, severity: "success" })
  }

  return (
    <AgentContent>
      <AgentContentHeader>
        <AgentTitle>{agent.label}</AgentTitle>
      </AgentContentHeader>

      <ConfigForm onSubmit={handleSave}>
        <ConfigSection>
          <ConfigSectionTitle>Connection</ConfigSectionTitle>
          <AgentConnectionFields form={form} onChange={() => refreshView((n) => n + 1)} />
          <FieldGrid sx={{ mt: 2 }}>
            <TextField
              label="HTTP API endpoint"
              fullWidth
              size="small"
              value={form.current.endpoint_ip ?? ""}
              InputProps={{ readOnly: true }}
              helperText="Uses the same host as the connection above"
            />
            <TextField
              label="HTTP API port"
              fullWidth
              type="number"
              size="small"
              required
              defaultValue={form.current.http_api_port}
              onChange={(event) => {
                form.current.http_api_port = parsePortValue(event.target.value)
              }}
              {...portField}
            />
          </FieldGrid>
        </ConfigSection>

        <SaveButton variant="contained" color="success" type="submit">
          Apply {agent.label} settings
        </SaveButton>
      </ConfigForm>
    </AgentContent>
  )
}
