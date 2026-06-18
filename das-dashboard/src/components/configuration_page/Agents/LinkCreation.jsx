import { useRef } from "react"
import { TextField } from "@mui/material"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
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

  const form = useRef((() => {
    const prefix = "agents.link_creation.params."
    const fullEndpoint = getDefault("agents.link_creation.endpoint") || "0.0.0.0:40000"
    const fullRange = getDefault("agents.link_creation.ports_range") || "42000:42999"

    return {
      endpoint_ip: fullEndpoint.split(":")[0] || "0.0.0.0",
      endpoint_port: Number(fullEndpoint.split(":")[1]) || 40000,
      ports_range_start: Number(fullRange.split(":")[0]) || 42000,
      ports_range_end: Number(fullRange.split(":")[1]) || 42999,
      max_answers: getDefault(`${prefix}max_answers`) ?? 10,
      repeat_count: getDefault(`${prefix}repeat_count`) ?? 1,
      context: getDefault(`${prefix}context`) || "context",
      attention_update: getDefault(`${prefix}attention_update`) ?? 0,
      attention_correlation: getDefault(`${prefix}attention_correlation`) ?? 0,
      query_interval: getDefault(`${prefix}query_interval`) ?? 0,
      query_timeout: getDefault(`${prefix}query_timeout`) ?? 0,
      positive_importance_flag: getDefault(`${prefix}positive_importance_flag`) ?? true,
      use_metta_as_query_tokens: getDefault(`${prefix}use_metta_as_query_tokens`) ?? false
    }
  })())

    const handleSave = () => {
    updateField("agents.link_creation", {
        endpoint: `${form.current.endpoint_ip}:${form.current.endpoint_port}`,
        ports_range: `${form.current.ports_range_start}:${form.current.ports_range_end}`,
        max_answers: form.current.max_answers,
        repeat_count: form.current.repeat_count,
        context: form.current.context,
        attention_update: form.current.attention_update,
        attention_correlation: form.current.attention_correlation,
        query_interval: form.current.query_interval,
        query_timeout: form.current.query_timeout,
        positive_importance_flag: form.current.positive_importance_flag,
        use_metta_as_query_tokens: form.current.use_metta_as_query_tokens
    })

    showToast({
        message: `${agent.label} settings applied`,
        severity: "success"
    })
    }

  const SpecificParamComponent = AGENT_COMPONENTS[agent.paramsKey]

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

      {SpecificParamComponent && (
        <ConfigSection>
          <ConfigSectionTitle>Parameters</ConfigSectionTitle>
          <SpecificParamComponent formRef={form} />
        </ConfigSection>
      )}

      <SaveButton variant="contained" color="success" onClick={handleSave}>
        Apply {agent.label} settings
      </SaveButton>
    </AgentContent>
  )
}