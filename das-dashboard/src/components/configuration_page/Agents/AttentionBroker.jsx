import { useRef } from "react"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { buildAgentPayload, splitEndpoint } from "../configFormUtils"
import { ConfigForm } from "../ConfigForm"
import { getAgentByKey } from "./agentRegistry"
import { AgentConnectionFields } from "./AgentConnectionFields"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  SaveButton
} from "./Agents.styled"

export default function AttentionBrokerPanel() {
  const { updateField, getDefaultSection } = useConfig()
  const { showToast } = useToast()
  const agent = getAgentByKey("attention")

  const endpoint = splitEndpoint(getDefaultSection("agents.attention")?.endpoint, "0.0.0.0", 40001)

  const form = useRef({
    endpoint_ip: endpoint.host,
    endpoint_port: endpoint.port
  })

  const handleSave = () => {
    updateField("agents.attention", buildAgentPayload(form.current, { withPortRange: false }))
    showToast({ message: `${agent.label} settings applied`, severity: "success" })
  }

  return (
    <AgentContent>
      <AgentContentHeader>
        <AgentTitle>{agent.label}</AgentTitle>
      </AgentContentHeader>

      <ConfigForm onSubmit={handleSave}>
        <ConfigSection>
          <ConfigSectionTitle>Connection</ConfigSectionTitle>
          <AgentConnectionFields form={form} withPortRange={false} />
        </ConfigSection>

        <SaveButton variant="contained" color="success" type="submit">
          Apply {agent.label} settings
        </SaveButton>
      </ConfigForm>
    </AgentContent>
  )
}
