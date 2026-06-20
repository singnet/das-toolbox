import { TextField } from "@mui/material"
import { FieldGrid } from "../Agents.styled"

const numberProps = {
  slotProps: {
    htmlInput: { onWheel: (e) => e.target.blur() }
  }
}

export default function InferenceParams({ formRef }) {
  return (
    <FieldGrid>
      <TextField
        label="Request Timeout"
        type="number"
        size="small"
        defaultValue={formRef.current.inference_request_timeout}
        {...numberProps}
        onChange={(e) => {
          formRef.current.inference_request_timeout = Number(e.target.value)
        }}
      />
      <TextField
        label="Repeat Count"
        type="number"
        size="small"
        defaultValue={formRef.current.repeat_count}
        {...numberProps}
        onChange={(e) => {
          formRef.current.repeat_count = Number(e.target.value)
        }}
      />
      <TextField
        label="Max Answers"
        type="number"
        size="small"
        defaultValue={formRef.current.max_answers}
        {...numberProps}
        onChange={(e) => {
          formRef.current.max_answers = Number(e.target.value)
        }}
      />
    </FieldGrid>
  )
}
