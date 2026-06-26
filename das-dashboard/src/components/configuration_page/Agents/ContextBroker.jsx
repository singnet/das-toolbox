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

export default function ContextBrokerPanel() {
  const { updateField, getDefaults } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("context")

  const form = useRef({
    ...initAgentConnection(getDefaults(), "context"),
    context: getAgentParam(getDefaults(), "context", "context", "context") || "context",
    initial_rent_rate: getAgentParam(getDefaults(), "context", "initial_rent_rate", 0.75),
    initial_spreading_rate_lowerbound: getAgentParam(getDefaults(), "context", "initial_spreading_rate_lowerbound", 0.1),
    initial_spreading_rate_upperbound: getAgentParam(getDefaults(), "context", "initial_spreading_rate_upperbound", 0.1),
    use_cache: getAgentParam(getDefaults(), "context", "use_cache", true),
    enforce_cache_recreation: getAgentParam(getDefaults(), "context", "enforce_cache_recreation", false)
  })

  const handleSave = () => {
    updateField("agents.context", buildAgentPayload(form.current))
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
            <ConfigSectionTitle>Parameters</ConfigSectionTitle>
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
