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

export default function AtomDbBrokerPanel() {
  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("atomdb")

  const form = useRef((() => {
    const fullEndpoint = getDefault("agents.atomdb.endpoint") || "0.0.0.0:40000"
    const fullRange = getDefault("agents.atomdb.ports_range") || "42000:42999"

    return {
      endpoint_ip: fullEndpoint.split(":")[0] || "0.0.0.0",
      endpoint_port: Number(fullEndpoint.split(":")[1]) || 40000,
      ports_range_start: Number(fullRange.split(":")[0]) || 42000,
      ports_range_end: Number(fullRange.split(":")[1]) || 42999
    }
  })())

    const handleSave = () => {
    updateField("agents.atomdb", {
            endpoint: `${form.current.endpoint_ip}:${form.current.endpoint_port}`,
            ports_range: `${form.current.ports_range_start}:${form.current.ports_range_end}`
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

        <FieldGrid sx={{ mt: 2 }}>
          <TextField
            label="Port range start"
            fullWidth
            type="number"
            size="small"
            defaultValue={form.current.ports_range_start}
            onChange={(e) => { form.current.ports_range_start = Number(e.target.value) }}
          />
          <TextField
            label="Port range end"
            fullWidth
            type="number"
            size="small"
            defaultValue={form.current.ports_range_end}
            onChange={(e) => { form.current.ports_range_end = Number(e.target.value) }}
          />
        </FieldGrid>
      </ConfigSection>

      <SaveButton variant="contained" color="success" onClick={handleSave}>
        Apply {agent.label} settings
      </SaveButton>
    </AgentContent>
  )
}