import { useRef } from "react"
import { TextField } from "@mui/material"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
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
  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("attention")

  const form = useRef((() => {
    const fullEndpoint = getDefault("agents.attention.endpoint") || "0.0.0.0:40000"

    return {
      endpoint_ip: fullEndpoint.split(":")[0] || "0.0.0.0",
      endpoint_port: Number(fullEndpoint.split(":")[1]) || 40000
    }
  })())

    const handleSave = () => {
    updateField("agents.attention", {
        endpoint: `${form.current.endpoint_ip}:${form.current.endpoint_port}`
    })

    showToast({
        message: `${agent.label} settings applied`,
        severity: "success"
    })
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