import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { getAgentParam } from "../configFormUtils"
import { getAgentByKey, AGENT_COMPONENTS } from "./agentRegistry"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  SaveButton
} from "./Agents.styled"

export default function BaseParametersPanel() {
  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("base_query")

  const form = useRef({
    max_answers: getAgentParam(getDefault, "base_query", "max_answers", 0),
    max_bundle_size: getAgentParam(getDefault, "base_query", "max_bundle_size", 1000),
    attention_update: getAgentParam(getDefault, "base_query", "attention_update", 0),
    attention_correlation: getAgentParam(getDefault, "base_query", "attention_correlation", 0),
    unique_assignment_flag: getAgentParam(getDefault, "base_query", "unique_assignment_flag", false),
    use_link_template_cache: getAgentParam(getDefault, "base_query", "use_link_template_cache", false),
    populate_metta_mapping: getAgentParam(getDefault, "base_query", "populate_metta_mapping", false),
    use_metta_as_query_tokens: getAgentParam(getDefault, "base_query", "use_metta_as_query_tokens", false),
    allow_incomplete_chain_path: getAgentParam(getDefault, "base_query", "allow_incomplete_chain_path", false)
  })

  const handleSave = () => {
    updateField("agents.base_query", structuredClone(form.current))
    showToast({ message: `${agent.label} settings applied`, severity: "success" })
  }

  const SpecificParamComponent = AGENT_COMPONENTS[agent.paramsKey]

  return (
    <AgentContent>
      <AgentContentHeader>
        <AgentTitle>{agent.label}</AgentTitle>
      </AgentContentHeader>

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