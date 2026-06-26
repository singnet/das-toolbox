import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { buildAgentPayload, getAgentParam, initAgentConnection } from "../configFormUtils"
import { ConfigForm } from "../ConfigForm"
import { AGENT_COMPONENTS, getAgentByKey } from "./agentRegistry"
import { AgentConnectionFields } from "./AgentConnectionFields"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  SaveButton
} from "./Agents.styled"

export default function InferenceAgentPanel() {
  const { updateField, getDefaults } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("inference")

  const form = useRef({
    ...initAgentConnection(getDefaults(), "inference"),
    inference_request_timeout: getAgentParam(getDefaults(), "inference", "inference_request_timeout", 86400),
    repeat_count: getAgentParam(getDefaults(), "inference", "repeat_count", 5),
    max_answers: getAgentParam(getDefaults(), "inference", "max_answers", 150)
  })

  const handleSave = () => {
    updateField("agents.inference", buildAgentPayload(form.current))
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
