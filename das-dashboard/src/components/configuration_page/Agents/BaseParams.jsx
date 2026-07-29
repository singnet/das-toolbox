import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { getAgentParam } from "../configFormUtils"
import { ConfigForm } from "../ConfigForm"
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
  const { updateField, getDefaults } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("base_query")

  const form = useRef({
    max_answers: getAgentParam(getDefaults(), "base_query", "max_answers", 0),
    max_bundle_size: getAgentParam(getDefaults(), "base_query", "max_bundle_size", 1000),
    attention_update: getAgentParam(getDefaults(), "base_query", "attention_update", 0),
    attention_correlation: getAgentParam(getDefaults(), "base_query", "attention_correlation", 0),
    attention_focus_strictness: getAgentParam(getDefaults(), "base_query", "attention_focus_strictness", 0.0),
    unique_assignment_flag: getAgentParam(getDefaults(), "base_query", "unique_assignment_flag", false),
    use_link_template_cache: getAgentParam(getDefaults(), "base_query", "use_link_template_cache", false),
    populate_metta_mapping: getAgentParam(getDefaults(), "base_query", "populate_metta_mapping", false),
    use_metta_as_query_tokens: getAgentParam(getDefaults(), "base_query", "use_metta_as_query_tokens", false),
    allow_incomplete_chain_path: getAgentParam(getDefaults(), "base_query", "allow_incomplete_chain_path", false)
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

      <ConfigForm onSubmit={handleSave}>
        {SpecificParamComponent && (
          <ConfigSection>
            <ConfigSectionTitle>Default values for request parameters</ConfigSectionTitle>
            <SpecificParamComponent formRef={form} />
          </ConfigSection>
        )}

        <SaveButton variant="contained" color="success" type="submit">
          Apply {agent.label} settings
        </SaveButton>
      </ConfigForm>
    </AgentContent>
  )
}