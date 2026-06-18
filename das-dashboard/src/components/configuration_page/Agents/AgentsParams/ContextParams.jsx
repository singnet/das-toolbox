import { TextField, Switch, FormControlLabel } from "@mui/material"
import { FieldGrid, SwitchGrid } from "../Agents.styled"

const numberProps = {
  slotProps: {
    htmlInput: { onWheel: (e) => e.target.blur() }
  }
}

export default function ContextParams({ formRef }) {
  return (
    <>
      <FieldGrid>
        <TextField
          label="Context Name"
          size="small"
          defaultValue={formRef.current.context}
          onChange={(e) => {
            formRef.current.context = e.target.value
          }}
        />
        <TextField
          label="Initial Rent Rate"
          type="number"
          size="small"
          defaultValue={formRef.current.initial_rent_rate}
          {...numberProps}
          onChange={(e) => {
            formRef.current.initial_rent_rate = Number(e.target.value)
          }}
        />
        <TextField
          label="Spread Lowerbound"
          type="number"
          size="small"
          defaultValue={formRef.current.initial_spreading_rate_lowerbound}
          {...numberProps}
          onChange={(e) => {
            formRef.current.initial_spreading_rate_lowerbound = Number(e.target.value)
          }}
        />
        <TextField
          label="Spread Upperbound"
          type="number"
          size="small"
          defaultValue={formRef.current.initial_spreading_rate_upperbound}
          {...numberProps}
          onChange={(e) => {
            formRef.current.initial_spreading_rate_upperbound = Number(e.target.value)
          }}
        />
      </FieldGrid>

      <SwitchGrid sx={{ mt: 2 }}>
        <FormControlLabel
          control={
            <Switch 
              defaultChecked={formRef.current.use_cache} 
              onChange={(e) => { formRef.current.use_cache = e.target.checked }} 
            />
          }
          label="Use Cache"
        />
        <FormControlLabel
          control={
            <Switch 
              defaultChecked={formRef.current.enforce_cache_recreation} 
              onChange={(e) => { formRef.current.enforce_cache_recreation = e.target.checked }} 
            />
          }
          label="Force Cache Reset"
        />
      </SwitchGrid>
    </>
  )
}