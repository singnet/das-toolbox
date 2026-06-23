import { TextField } from "@mui/material"
import { FieldGrid } from "./Agents.styled"
import { portField } from "../formValidation"

export function AgentConnectionFields({ form, withPortRange = true }) {
  return (
    <>
      <FieldGrid>
        <TextField
          label="IP Address"
          fullWidth
          size="small"
          required
          defaultValue={form.current.endpoint_ip}
          onChange={(e) => { form.current.endpoint_ip = e.target.value }}
        />
        <TextField
          label="Port"
          fullWidth
          type="number"
          size="small"
          required
          defaultValue={form.current.endpoint_port}
          onChange={(e) => { form.current.endpoint_port = Number(e.target.value) }}
          {...portField}
        />
      </FieldGrid>

      {withPortRange && (
        <FieldGrid sx={{ mt: 2 }}>
          <TextField
            label="Port range start"
            fullWidth
            type="number"
            size="small"
            required
            defaultValue={form.current.ports_range_start}
            onChange={(e) => { form.current.ports_range_start = Number(e.target.value) }}
            {...portField}
          />
          <TextField
            label="Port range end"
            fullWidth
            type="number"
            size="small"
            required
            defaultValue={form.current.ports_range_end}
            onChange={(e) => { form.current.ports_range_end = Number(e.target.value) }}
            {...portField}
          />
        </FieldGrid>
      )}
    </>
  )
}
