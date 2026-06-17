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

export default function QueryParams({ params, onChange }) {
  return (
    <>
      <FieldGrid>
        <TextField
          label="Max Answers"
          type="number"
          defaultValue={params.max_answers}
          {...numberProps}
          onChange={(e) => onChange("max_answers", Number(e.target.value))}
        />
        <TextField
          label="Max Bundle Size"
          type="number"
          defaultValue={params.max_bundle_size}
          {...numberProps}
          onChange={(e) => onChange("max_bundle_size", Number(e.target.value))}
        />
      </FieldGrid>

      <SwitchGrid sx={{ mt: 2 }}>
        <FormControlLabel
          control={<Switch defaultChecked={params.count_flag} onChange={(e) => onChange("count_flag", e.target.checked)} />}
          label="Count Flag"
        />
        <FormControlLabel
          control={<Switch defaultChecked={params.attention_update_flag} onChange={(e) => onChange("attention_update_flag", e.target.checked)} />}
          label="Attention Update"
        />
        <FormControlLabel
          control={<Switch defaultChecked={params.unique_assignment_flag} onChange={(e) => onChange("unique_assignment_flag", e.target.checked)} />}
          label="Unique Assignment"
        />
        <FormControlLabel
          control={<Switch defaultChecked={params.positive_importance_flag} onChange={(e) => onChange("positive_importance_flag", e.target.checked)} />}
          label="Positive Importance"
        />
        <FormControlLabel
          control={<Switch defaultChecked={params.populate_metta_mapping} onChange={(e) => onChange("populate_metta_mapping", e.target.checked)} />}
          label="Metta Mapping"
        />
        <FormControlLabel
          control={<Switch defaultChecked={params.use_metta_as_query_tokens} onChange={(e) => onChange("use_metta_as_query_tokens", e.target.checked)} />}
          label="Use Metta Tokens"
        />
      </SwitchGrid>
    </>
  )
}