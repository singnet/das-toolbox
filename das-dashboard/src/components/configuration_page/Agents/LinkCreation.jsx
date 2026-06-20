import { useRef } from "react"
import { TextField } from "@mui/material"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { buildAgentPayload, getAgentParam, initAgentConnection } from "../configFormUtils"
import { getAgentByKey, AGENT_COMPONENTS } from "./agentRegistry"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  FieldGrid,
  SaveButton
} from "./Agents.styled"

export default function LinkCreationAgentPanel() {
  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("link_creation")

  const form = useRef({
    ...initAgentConnection(getDefault, "link_creation"),
    max_answers: getAgentParam(getDefault, "link_creation", "max_answers", 10),
    repeat_count: getAgentParam(getDefault, "link_creation", "repeat_count", 1),
    context: getAgentParam(getDefault, "link_creation", "context", "context") || "context",
    attention_update: getAgentParam(getDefault, "link_creation", "attention_update", 0),
    attention_correlation: getAgentParam(getDefault, "link_creation", "attention_correlation", 0),
    query_interval: getAgentParam(getDefault, "link_creation", "query_interval", 0),
    query_timeout: getAgentParam(getDefault, "link_creation", "query_timeout", 0),
    positive_importance_flag: getAgentParam(getDefault, "link_creation", "positive_importance_flag", true),
    use_metta_as_query_tokens: getAgentParam(getDefault, "link_creation", "use_metta_as_query_tokens", false)
  })

  const handleSave = () => {
    updateField("agents.link_creation", buildAgentPayload(form.current))
    showToast({ message: `${agent.label} settings applied`, severity: "success" })
  }

  const ParamsComponent = AGENT_COMPONENTS[agent.paramsKey]

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

      {ParamsComponent && (
        <ConfigSection>
          <ConfigSectionTitle>Parameters</ConfigSectionTitle>
          <ParamsComponent formRef={form} />
        </ConfigSection>
      )}

      <SaveButton variant="contained" color="success" onClick={handleSave}>
        Apply {agent.label} settings
      </SaveButton>
    </AgentContent>
  )
}
