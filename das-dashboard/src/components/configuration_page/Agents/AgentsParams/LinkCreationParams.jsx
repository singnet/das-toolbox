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
} from "../Agents.styled"

import { useRef, useState } from "react"
import {
  TextField,
  Switch,
  FormControlLabel
} from "@mui/material"

import { useConfig } from "../../../global_providers/ConfigurationProvider"

const numberProps = {
  slotProps: {
    htmlInput: { onWheel: (e) => e.target.blur() }
  }
}

export default function LinkCreationParams({ params, onChange }) {
  return (
    <FieldGrid>
      <TextField
        label="Repeat Count"
        type="number"
        defaultValue={params.repeat_count}
        {...numberProps}
        onChange={(e) => onChange("repeat_count", Number(e.target.value))}
      />
      <TextField
        label="Query Interval"
        type="number"
        defaultValue={params.query_interval}
        {...numberProps}
        onChange={(e) => onChange("query_interval", Number(e.target.value))}
      />
      <TextField
        label="Query Timeout"
        type="number"
        defaultValue={params.query_timeout}
        {...numberProps}
        onChange={(e) => onChange("query_timeout", Number(e.target.value))}
      />
    </FieldGrid>
  )
}