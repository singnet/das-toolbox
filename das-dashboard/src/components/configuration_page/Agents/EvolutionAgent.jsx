import { useRef } from "react"
import { TextField } from "@mui/material"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"
import { buildAgentPayload, getAgentParam, initAgentConnection } from "../configFormUtils"
import { getAgentByKey, AGENT_COMPONENTS } from "./agentRegistry"
import {
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  ConfigSection,
  ConfigSectionTitle,
  FieldGrid,
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

      <ConfigSection>
        <ConfigSectionTitle>Connection</ConfigSectionTitle>
        <FieldGrid>
          <TextField
            label="IP Address"
            fullWidth
            size="small"
            defaultValue={form.current.endpoint_ip}
            onChange={(e) => { form.current.endpoint_ip = e.target.value }}
          />
          <TextField
            label="Port"
            fullWidth
            type="number"
            size="small"
            defaultValue={form.current.endpoint_port}
            onChange={(e) => { form.current.endpoint_port = Number(e.target.value) }}
          />
        </FieldGrid>

        <FieldGrid sx={{ mt: 2 }}>
          <TextField
            label="Port range start"
            fullWidth
            type="number"
            size="small"
            defaultValue={form.current.ports_range_start}
            onChange={(e) => { form.current.ports_range_start = Number(e.target.value) }}
          />
          <TextField
            label="Port range end"
            fullWidth
            type="number"
            size="small"
            defaultValue={form.current.ports_range_end}
            onChange={(e) => { form.current.ports_range_end = Number(e.target.value) }}
          />
        </FieldGrid>
      </ConfigSection>

      {ParamsComponent && (
        <ConfigSection>
          <ConfigSectionTitle>Parameters</ConfigSectionTitle>
          <ParamsComponent formRef={form} />
        </ConfigSection>
      )}

      <SaveButton variant="contained" color="success" onClick={handleSave}>
        Apply {agent.label} settings
      </SaveButton>
    </AgentContent>
  )
}
