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

export default function ContextParams({ params, onChange }) {
  return (
    <>
      <FieldGrid>
        <TextField
          label="Context Name"
          defaultValue={params.context}
          onChange={(e) => onChange("context", e.target.value)}
        />
        <TextField
          label="Initial Rent Rate"
          type="number"
          defaultValue={params.initial_rent_rate}
          {...numberProps}
          onChange={(e) => onChange("initial_rent_rate", Number(e.target.value))}
        />
        <TextField
          label="Spread Lowerbound"
          type="number"
          defaultValue={params.initial_spreading_rate_lowerbound}
          {...numberProps}
          onChange={(e) => onChange("initial_spreading_rate_lowerbound", Number(e.target.value))}
        />
        <TextField
          label="Spread Upperbound"
          type="number"
          defaultValue={params.initial_spreading_rate_upperbound}
          {...numberProps}
          onChange={(e) => onChange("initial_spreading_rate_upperbound", Number(e.target.value))}
        />
      </FieldGrid>

      <SwitchGrid sx={{ mt: 2 }}>
        <FormControlLabel
          control={<Switch defaultChecked={params.use_cache} onChange={(e) => onChange("use_cache", e.target.checked)} />}
          label="Use Cache"
        />
        <FormControlLabel
          control={<Switch defaultChecked={params.enforce_cache_recreation} onChange={(e) => onChange("enforce_cache_recreation", e.target.checked)} />}
          label="Force Cache Reset"
        />
      </SwitchGrid>
    </>
  )
}