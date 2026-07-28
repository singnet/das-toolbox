import { TextField } from "@mui/material"
import { FieldGrid } from "./Agents.styled"
import { parsePortValue } from "../configFormUtils"
import { ipv4Field, portField } from "../formValidation"

export function AgentConnectionFields({ form, withPortRange = true, onChange }) {
  return (
    <>
      <FieldGrid>
        <TextField
          label="IP Address"
          fullWidth
          size="small"
          required
          defaultValue={form.current.endpoint_ip}
          onChange={(e) => {
            form.current.endpoint_ip = e.target.value
            onChange?.()
          }}
          {...ipv4Field}
        />
        <TextField
          label="Port"
          fullWidth
          type="number"
          size="small"
          required
          defaultValue={form.current.endpoint_port}
          onChange={(e) => { form.current.endpoint_port = parsePortValue(e.target.value) }}
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
            onChange={(e) => { form.current.ports_range_start = parsePortValue(e.target.value) }}
            {...portField}
          />
          <TextField
            label="Port range end"
            fullWidth
            type="number"
            size="small"
            required
            defaultValue={form.current.ports_range_end}
            onChange={(e) => { form.current.ports_range_end = parsePortValue(e.target.value) }}
            {...portField}
          />
        </FieldGrid>
      )}
    </>
  )
}
