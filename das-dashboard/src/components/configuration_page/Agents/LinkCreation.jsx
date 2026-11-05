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
    unique_assignment_flag: getAgentParam(getDefaults(), "link_creation", "unique_assignment_flag", false),
    positive_importance_flag: getAgentParam(getDefaults(), "link_creation", "positive_importance_flag", false),
    disregard_importance_flag: getAgentParam(getDefaults(), "link_creation", "disregard_importance_flag", false),
    unique_value_flag: getAgentParam(getDefaults(), "link_creation", "unique_value_flag", false),
    max_successful_creation_per_round: getAgentParam(getDefaults(), "link_creation", "max_successful_creation_per_round", 10),
    max_unproductive_visits_per_round: getAgentParam(getDefaults(), "link_creation", "max_unproductive_visits_per_round", 500),
    max_visit_attempts_per_round: getAgentParam(getDefaults(), "link_creation", "max_visit_attempts_per_round", 20),
    max_rounds: getAgentParam(getDefaults(), "link_creation", "max_rounds", 5),
    link_creation_strength_threshold: getAgentParam(getDefaults(), "link_creation", "link_creation_strength_threshold", 0.1)
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
