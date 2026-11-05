import { TextField, Switch, FormControlLabel } from "@mui/material"
import { FieldGrid, SwitchGrid } from "../Agents.styled"
import { field, numberField } from "../../formValidation"

const strengthThresholdField = field({ min: 0, step: 0.01 })

export default function LinkCreationParams({ formRef }) {
  return (
    <>
      <SwitchGrid sx={{ mt: 2 }}>
        <FormControlLabel
          control={
            <Switch
              defaultChecked={formRef.current.unique_assignment_flag}
              onChange={(e) => { formRef.current.unique_assignment_flag = e.target.checked }}
            />
          }
          label="Unique Assignment"
        />
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
              defaultChecked={formRef.current.disregard_importance_flag}
              onChange={(e) => { formRef.current.disregard_importance_flag = e.target.checked }}
            />
          }
          label="Disregard Importance"
        />
        <FormControlLabel
          control={
            <Switch
              defaultChecked={formRef.current.unique_value_flag}
              onChange={(e) => { formRef.current.unique_value_flag = e.target.checked }}
            />
          }
          label="Unique Value"
        />
      </SwitchGrid>

      <FieldGrid sx={{ mt: 2 }}>
        <TextField
          label="Max Successful Creation per Round"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.max_successful_creation_per_round}
          {...numberField}
          onChange={(e) => {
            formRef.current.max_successful_creation_per_round = Number(e.target.value)
          }}
        />
        <TextField
          label="Max Unproductive Visits per Round"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.max_unproductive_visits_per_round}
          {...numberField}
          onChange={(e) => {
            formRef.current.max_unproductive_visits_per_round = Number(e.target.value)
          }}
        />
        <TextField
          label="Max Visit Attempts per Round"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.max_visit_attempts_per_round}
          {...numberField}
          onChange={(e) => {
            formRef.current.max_visit_attempts_per_round = Number(e.target.value)
          }}
        />
        <TextField
          label="Max Rounds"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.max_rounds}
          {...numberField}
          onChange={(e) => {
            formRef.current.max_rounds = Number(e.target.value)
          }}
        />
        <TextField
          label="Link Creation Strength Threshold"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.link_creation_strength_threshold}
          {...strengthThresholdField}
          onChange={(e) => {
            formRef.current.link_creation_strength_threshold = Number(e.target.value)
          }}
        />
      </FieldGrid>
    </>
  )
}
