import { TextField } from "@mui/material"
import { FieldGrid } from "../Agents.styled"
import { numberField } from "../../formValidation"

export default function InferenceParams({ formRef }) {
  return (
    <FieldGrid>
      <TextField
        label="Request Timeout"
        type="number"
        size="small"
        required
        defaultValue={formRef.current.inference_request_timeout}
        {...numberField}
        onChange={(e) => {
          formRef.current.inference_request_timeout = Number(e.target.value)
        }}
      />
      <TextField
        label="Repeat Count"
        type="number"
        size="small"
        required
        defaultValue={formRef.current.repeat_count}
        {...numberField}
        onChange={(e) => {
          formRef.current.repeat_count = Number(e.target.value)
        }}
      />
      <TextField
        label="Max Answers"
        type="number"
        size="small"
        required
        defaultValue={formRef.current.max_answers}
        {...numberField}
        onChange={(e) => {
          formRef.current.max_answers = Number(e.target.value)
        }}
      />
    </FieldGrid>
  )
}
