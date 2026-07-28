import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { buildAgentPayload, getAgentParam, initAgentConnection } from "../configFormUtils"
import { ConfigForm } from "../ConfigForm"
import { getAgentByKey, AGENT_COMPONENTS } from "./agentRegistry"
import { AgentConnectionFields } from "./AgentConnectionFields"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  SaveButton
} from "./Agents.styled"

export default function LinkCreationAgentPanel() {
  const { updateField, getDefaults } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("link_creation")

  const form = useRef({
    ...initAgentConnection(getDefaults(), "link_creation"),
    max_answers: getAgentParam(getDefaults(), "link_creation", "max_answers", 10),
    repeat_count: getAgentParam(getDefaults(), "link_creation", "repeat_count", 1),
    context: getAgentParam(getDefaults(), "link_creation", "context", "context") || "context",
    attention_update: getAgentParam(getDefaults(), "link_creation", "attention_update", 0),
    attention_correlation: getAgentParam(getDefaults(), "link_creation", "attention_correlation", 0),
    query_interval: getAgentParam(getDefaults(), "link_creation", "query_interval", 0),
    query_timeout: getAgentParam(getDefaults(), "link_creation", "query_timeout", 0),
    positive_importance_flag: getAgentParam(getDefaults(), "link_creation", "positive_importance_flag", true),
    use_metta_as_query_tokens: getAgentParam(getDefaults(), "link_creation", "use_metta_as_query_tokens", false)
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

      <ConfigForm onSubmit={handleSave}>
        <ConfigSection>
          <ConfigSectionTitle>Connection</ConfigSectionTitle>
          <AgentConnectionFields form={form} />
        </ConfigSection>

        {ParamsComponent && (
          <ConfigSection>
            <ConfigSectionTitle>Default values for request parameters</ConfigSectionTitle>
            <ParamsComponent formRef={form} />
          </ConfigSection>
        )}

        <SaveButton variant="contained" color="success" type="submit">
          Apply {agent.label} settings
        </SaveButton>
      </ConfigForm>
    </AgentContent>
  )
}
