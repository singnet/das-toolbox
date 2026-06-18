import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
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

  const form = useRef((() => {
    const prefix = "agents.base_query.params."
    
    return {
      max_answers: getDefault(`${prefix}max_answers`) ?? 0,
      max_bundle_size: getDefault(`${prefix}max_bundle_size`) ?? 1000,
      attention_update: getDefault(`${prefix}attention_update`) ?? 0,
      attention_correlation: getDefault(`${prefix}attention_correlation`) ?? 0,
      unique_assignment_flag: getDefault(`${prefix}unique_assignment_flag`) ?? false,
      use_link_template_cache: getDefault(`${prefix}use_link_template_cache`) ?? false,
      populate_metta_mapping: getDefault(`${prefix}populate_metta_mapping`) ?? false,
      use_metta_as_query_tokens: getDefault(`${prefix}use_metta_as_query_tokens`) ?? false,
      allow_incomplete_chain_path: getDefault(`${prefix}allow_incomplete_chain_path`) ?? false
    }
  })())

  const handleSave = () => {
    const currentAgentsState = getDefault("agents") || {}
    const mergedPayload = structuredClone(currentAgentsState)

    Object.keys(form.current).forEach((key) => {
      const val = form.current[key]
      if (val !== undefined && val !== null) {
        mergedPayload[`base_query.params.${key}`] = val
      }
    })

    updateField("agents", mergedPayload)
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