import { useRef } from "react"
import { TextField } from "@mui/material"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { buildAgentPayload, splitEndpoint } from "../configFormUtils"
import { getAgentByKey } from "./agentRegistry"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  FieldGrid,
  SaveButton
} from "./Agents.styled"

export default function AttentionBrokerPanel() {
  const { updateField, getDefaultSection } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("attention")

  const endpoint = splitEndpoint(getDefaultSection("agents.attention")?.endpoint, "0.0.0.0", 40001)

  const form = useRef({
    endpoint_ip: endpoint.host,
    endpoint_port: endpoint.port
  })

  const handleSave = () => {
    updateField("agents.attention", buildAgentPayload(form.current, { withPortRange: false }))
    showToast({ message: `${agent.label} settings applied`, severity: "success" })
  }

  return (
    <AgentContent>
      <AgentContentHeader>
        <AgentTitle>{agent.label}</AgentTitle>
      </AgentContentHeader>

      <ConfigSection>
        <ConfigSectionTitle>Connection</ConfigSectionTitle>
        <FieldGrid>
          <TextField
            label="IP Address"
            fullWidth
            size="small"
            defaultValue={form.current.endpoint_ip}
            onChange={(e) => { form.current.endpoint_ip = e.target.value }}
          />
          <TextField
            label="Port"
            fullWidth
            type="number"
            size="small"
            defaultValue={form.current.endpoint_port}
            onChange={(e) => { form.current.endpoint_port = Number(e.target.value) }}
          />
        </FieldGrid>
      </ConfigSection>

      <SaveButton variant="contained" color="success" onClick={handleSave}>
        Apply {agent.label} settings
      </SaveButton>
    </AgentContent>
  )
}
