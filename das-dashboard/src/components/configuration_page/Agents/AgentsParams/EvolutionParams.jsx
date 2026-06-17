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

export default function EvolutionParams({ params, onChange }) {
  return (
    <FieldGrid>
      <TextField
        label="Elitism Rate"
        type="number"
        defaultValue={params.elitism_rate}
        {...numberProps}
        onChange={(e) => onChange("elitism_rate", Number(e.target.value))}
      />
      <TextField
        label="Max Generations"
        type="number"
        defaultValue={params.max_generations}
        {...numberProps}
        onChange={(e) => onChange("max_generations", Number(e.target.value))}
      />
      <TextField
        label="Population Size"
        type="number"
        defaultValue={params.population_size}
        {...numberProps}
        onChange={(e) => onChange("population_size", Number(e.target.value))}
      />
      <TextField
        label="Selection Rate"
        type="number"
        defaultValue={params.selection_rate}
        {...numberProps}
        onChange={(e) => onChange("selection_rate", Number(e.target.value))}
      />
      <TextField
        label="Total Attention Tokens"
        type="number"
        defaultValue={params.total_attention_tokens}
        {...numberProps}
        onChange={(e) => onChange("total_attention_tokens", Number(e.target.value))}
      />
    </FieldGrid>
  )
}