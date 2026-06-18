import { Switch, FormControlLabel } from "@mui/material"
import { SwitchGrid } from "../Agents.styled"

export default function QueryParams({ formRef }) {
  return (
    <SwitchGrid>
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
        label="Unique Value Flag"
      />
      <FormControlLabel
        control={
          <Switch 
            defaultChecked={formRef.current.count_flag} 
            onChange={(e) => { formRef.current.count_flag = e.target.checked }} 
          />
        }
        label="Count Flag"
      />
    </SwitchGrid>
  )
}