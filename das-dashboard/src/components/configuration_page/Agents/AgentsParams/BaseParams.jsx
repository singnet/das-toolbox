import { useState } from "react"
import { TextField, Switch, FormControlLabel, Slider, Box, Typography } from "@mui/material"
import { FieldGrid, SwitchGrid } from "../Agents.styled"
import { numberField } from "../../formValidation"
import { palette } from "../../../../pages/setup_das/SetupDasStyled"

export default function BaseQueryParams({ formRef }) {
  const [focusStrictness, setFocusStrictness] = useState(
    Number(formRef.current.attention_focus_strictness) || 0
  )

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
          label="Max Bundle Size"
          type="number"
          size="small"
          required
          defaultValue={formRef.current.max_bundle_size}
          {...numberField}
          onChange={(e) => {
            formRef.current.max_bundle_size = Number(e.target.value)
          }}
        />
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
        <Box sx={{ gridColumn: "1 / -1" }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
            <Typography sx={{ fontSize: 13, color: palette.textSecondary }}>
              Attention Focus Strictness
            </Typography>
            <Typography sx={{ fontSize: 13, fontWeight: 600, color: palette.textPrimary }}>
              {focusStrictness.toFixed(1)}
            </Typography>
          </Box>
          <Slider
            size="small"
            value={focusStrictness}
            min={0}
            max={1}
            step={0.1}
            onChange={(_, value) => {
              setFocusStrictness(value)
              formRef.current.attention_focus_strictness = value
            }}
            sx={{
              color: palette.accent,
              "& .MuiSlider-rail": { opacity: 0.35 }
            }}
          />
        </Box>
      </FieldGrid>

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
              defaultChecked={formRef.current.use_link_template_cache} 
              onChange={(e) => { formRef.current.use_link_template_cache = e.target.checked }} 
            />
          }
          label="Use Link Template Cache"
        />
        <FormControlLabel
          control={
            <Switch 
              defaultChecked={formRef.current.populate_metta_mapping} 
              onChange={(e) => { formRef.current.populate_metta_mapping = e.target.checked }} 
            />
          }
          label="Metta Mapping"
        />
        <FormControlLabel
          control={
            <Switch 
              defaultChecked={formRef.current.use_metta_as_query_tokens} 
              onChange={(e) => { formRef.current.use_metta_as_query_tokens = e.target.checked }} 
            />
          }
          label="Use Metta Tokens"
        />
        <FormControlLabel
          control={
            <Switch 
              defaultChecked={formRef.current.allow_incomplete_chain_path} 
              onChange={(e) => { formRef.current.allow_incomplete_chain_path = e.target.checked }} 
            />
          }
          label="Allow Incomplete Chain Path"
        />
      </SwitchGrid>
    </>
  )
}
