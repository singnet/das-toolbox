import { useRef, useState } from "react"
import {
  TextField,
  Switch,
  FormControlLabel
} from "@mui/material"

import { useConfig } from "../../global_providers/ConfigurationProvider"
import { useToast } from "../../global_providers/ToastProvider"

import { AGENT_GROUPS, getAgentByKey } from "./agentRegistry"
import {
  AgentsLayout,
  AgentNav,
  AgentNavGroupLabel,
  AgentNavItem,
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  AgentDescription,
  ConfigSection,
  ConfigSectionTitle,
  FieldGrid,
  SwitchGrid,
  SaveButton
} from "./Agents.styled"

import QueryParams from "./AgentsParams/QueryParams"
import EvolutionParams from "./AgentsParams/EvolutionParams"
import ContextParams from "./AgentsParams/ContextParams"
import LinkCreationParams from "./AgentsParams/LinkCreationParams"

function getEndpoint(endpoint = "0.0.0.0:40000") {
  return endpoint.split(":")[0] || ""
}

function getPort(endpoint = "0.0.0.0:40000") {
  return endpoint.split(":")[1] || ""
}

function getRangeStart(range = "42000:42999") {
  return range.split(":")[0] || ""
}

function getRangeEnd(range = "42000:42999") {
  return range.split(":")[1] || ""
}

function ConnectionFields({ data, hasPortRange, onPortChange, onRangeStartChange, onRangeEndChange }) {
  return (
    <>
      <TextField
        label="IP Address"
        fullWidth
        type="text"
        defaultValue={getEndpoint(data.endpoint)}
        onChange={(e) => onPortChange(e.target.value)}
        sx={{ mb: hasPortRange ? 2 : 2 }}
      />

      <TextField
        label="Port"
        fullWidth
        type="number"
        defaultValue={getPort(data.endpoint)}
        onChange={(e) => onPortChange(e.target.value)}
        sx={{ mb: hasPortRange ? 2 : 2 }}
      />

      {hasPortRange && (
        <FieldGrid>
          <TextField
            label="Port range start"
            fullWidth
            type="number"
            defaultValue={getRangeStart(data.ports_range)}
            onChange={(e) => onRangeStartChange(e.target.value)}
          />
          <TextField
            label="Port range end"
            fullWidth
            type="number"
            defaultValue={getRangeEnd(data.ports_range)}
            onChange={(e) => onRangeEndChange(e.target.value)}
          />
        </FieldGrid>
      )}
    </>
  )
}

function ParamsPanel({ paramsKey, paramsRef }) {
  if (!paramsKey) return null

  const params = paramsRef.current

  const onChange = (field, value) => {
    params[field] = value
  }

  return (
    <ConfigSection>
      <ConfigSectionTitle>Parameters</ConfigSectionTitle>

      {paramsKey === "query" && <QueryParams params={params} onChange={onChange} />}
      {paramsKey === "link_creation" && <LinkCreationParams params={params} onChange={onChange} />}
      {paramsKey === "evolution" && <EvolutionParams params={params} onChange={onChange} />}
      {paramsKey === "context" && <ContextParams params={params} onChange={onChange} />}
    </ConfigSection>
  )
}

function AgentPanel({ agentKey }) {
  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()

  const agent = getAgentByKey(agentKey)
  const defaults = getDefault()

  const sectionDefaults = defaults[agent.configSection]?.[agent.key] || {}
  const paramsDefaults = agent.paramsKey
    ? defaults.params?.[agent.paramsKey] || {}
    : null

  const connectionRef = useRef(structuredClone(sectionDefaults))
  const paramsRef = useRef(paramsDefaults ? structuredClone(paramsDefaults) : null)

  const updateEndpoint = (value) => {
    connectionRef.current.endpoint = `${value}:port`
  }

  const updatePort = (value) => {
    connectionRef.current.endpoint = `localhost:${value}`
  }

  const updateRangeStart = (value) => {
    const [, end] = (connectionRef.current.ports_range || ":").split(":")
    connectionRef.current.ports_range = `${value}:${end || ""}`
  }

  const updateRangeEnd = (value) => {
    const [start] = (connectionRef.current.ports_range || ":").split(":")
    connectionRef.current.ports_range = `${start || ""}:${value}`
  }

  const handleSave = () => {
    const fullSection = structuredClone(defaults[agent.configSection] || {})
    fullSection[agent.key] = structuredClone(connectionRef.current)
    updateSection(agent.configSection, fullSection)

    if (agent.paramsKey && paramsRef.current) {
      const fullParams = structuredClone(defaults.params || {})
      fullParams[agent.paramsKey] = structuredClone(paramsRef.current)
      updateSection("params", fullParams)
    }

    showToast({ message: `${agent.label} saved successfully!`, severity: "success" })
  }

  return (
    <AgentContent key={agentKey}>

      <AgentContentHeader>
        <AgentTitle>{agent.label}</AgentTitle>
      </AgentContentHeader>

      <ConfigSection>
        <ConfigSectionTitle>Connection</ConfigSectionTitle>
        <ConnectionFields
          data={connectionRef.current}
          hasPortRange={agent.hasPortRange}
          onPortChange={updatePort}
          onRangeStartChange={updateRangeStart}
          onRangeEndChange={updateRangeEnd}
        />
      </ConfigSection>

      {agent.paramsKey && paramsRef.current && (
        <ParamsPanel paramsKey={agent.paramsKey} paramsRef={paramsRef} />
      )}

      <SaveButton onClick={handleSave}>
        Apply {agent.label} settings
      </SaveButton>

    </AgentContent>
  )
}

export function AgentsForm({ activeAgent, onAgentChange }) {
  const selectedAgent = activeAgent || "query"

  return (
    <AgentsLayout>

      <AgentNav>

        {AGENT_GROUPS.map((group) => (
          <div key={group.label}>

            <AgentNavGroupLabel>{group.label}</AgentNavGroupLabel>

            {group.items.map((item) => {

              return (
                <AgentNavItem
                  key={item.key}
                  active={selectedAgent === item.key}
                  onClick={() => onAgentChange(item.key)}
                >
                  {item.label}
                </AgentNavItem>
              )
            })}

          </div>
        ))}

      </AgentNav>

      <AgentPanel key={selectedAgent} agentKey={selectedAgent} />

    </AgentsLayout>
  )
}
