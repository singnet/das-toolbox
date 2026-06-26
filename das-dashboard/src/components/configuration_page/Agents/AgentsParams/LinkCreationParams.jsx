import { TextField, Switch, FormControlLabel } from "@mui/material"
import { FieldGrid, SwitchGrid } from "../Agents.styled"
import { idField, numberField } from "../../formValidation"

export default function LinkCreationParams({ formRef }) {
  return (
    <>
      <FieldGrid>
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
          label="Context"
          size="small"
          required
          defaultValue={formRef.current.context}
          onChange={(e) => {
            formRef.current.context = e.target.value
          }}
          {...idField}
        />
      </FieldGrid>

      <FieldGrid sx={{ mt: 2 }}>
        <TextField
          label="Attention Update"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.attention_update}
          {...numberField}
          onChange={(e) => {
            formRef.current.attention_update = Number(e.target.value)
          }}
        />
        <TextField
          label="Attention Correlation"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.attention_correlation}
          {...numberField}
          onChange={(e) => {
            formRef.current.attention_correlation = Number(e.target.value)
          }}
        />
      </FieldGrid>

      <FieldGrid sx={{ mt: 2 }}>
        <TextField
          label="Query Interval"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.query_interval}
          {...numberField}
          onChange={(e) => {
            formRef.current.query_interval = Number(e.target.value)
          }}
        />
        <TextField
          label="Query Timeout"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.query_timeout}
          {...numberField}
          onChange={(e) => {
            formRef.current.query_timeout = Number(e.target.value)
          }}
        />
      </FieldGrid>

      <SwitchGrid sx={{ mt: 2 }}>
        <FormControlLabel
          control={
            <Switch 
              defaultChecked={formRef.current.positive_importance_flag} 
              onChange={(e) => { formRef.current.positive_importance_flag = e.target.checked }} 
            />
          }
          label="Positive Importance"
        />
        <FormControlLabel
          control={
            <Switch 
              defaultChecked={formRef.current.use_metta_as_query_tokens} 
              onChange={(e) => { formRef.current.use_metta_as_query_tokens = e.target.checked }} 
            />
          }
          label="Use MeTTa as Query Tokens"
        />
      </SwitchGrid>
    </>
  )
}
