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

export default function EvolutionAgentPanel() {
  const { updateField, getDefaults } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("evolution")

  const form = useRef({
    ...initAgentConnection(getDefaults(), "evolution"),
    population_size: getAgentParam(getDefaults(), "evolution", "population_size", 1000),
    max_generations: getAgentParam(getDefaults(), "evolution", "max_generations", 100),
    elitism_rate: getAgentParam(getDefaults(), "evolution", "elitism_rate", 0.01),
    selection_rate: getAgentParam(getDefaults(), "evolution", "selection_rate", 0.1)
  })

  const handleSave = () => {
    updateField("agents.evolution", buildAgentPayload(form.current))
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
