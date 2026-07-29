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

export default function QueryAgentPanel() {
  const { updateField, getDefaults } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("query")

  const form = useRef({
    ...initAgentConnection(getDefaults(), "query"),
    positive_importance_flag: getAgentParam(getDefaults(), "query", "positive_importance_flag", false),
    disregard_importance_flag: getAgentParam(getDefaults(), "query", "disregard_importance_flag", false),
    unique_value_flag: getAgentParam(getDefaults(), "query", "unique_value_flag", false),
    count_flag: getAgentParam(getDefaults(), "query", "count_flag", false)
  })

  const handleSave = () => {
    updateField("agents.query", buildAgentPayload(form.current))
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
