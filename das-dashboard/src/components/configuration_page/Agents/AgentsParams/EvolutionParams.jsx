import { TextField } from "@mui/material"
import { FieldGrid } from "../Agents.styled"
import { idField, numberField, elitismRateField, selectionRateInput } from "../../formValidation"

export default function EvolutionParams({ formRef }) {
  return (
    <FieldGrid>
      <TextField
        label="Population Size"
        type="number"
        size="small"
        required
        defaultValue={formRef.current.population_size}
        {...numberField}
        onChange={(e) => {
          formRef.current.population_size = Number(e.target.value)
        }}
      />
      <TextField
        label="Max Generations"
        type="number"
        size="small"
        required
        defaultValue={formRef.current.max_generations}
        {...numberField}
        onChange={(e) => {
          formRef.current.max_generations = Number(e.target.value)
        }}
      />
      <TextField
        label="Elitism Rate"
        type="number"
        size="small"
        required
        defaultValue={formRef.current.elitism_rate}
        {...elitismRateField}
        onChange={(e) => {
          formRef.current.elitism_rate = Number(e.target.value)
        }}
      />
      <TextField
        label="Selection Rate"
        type="number"
        size="small"
        required
        defaultValue={formRef.current.selection_rate}
        {...numberField}
        onChange={(e) => {
          formRef.current.selection_rate = Number(e.target.value)
        }}
      />
    </FieldGrid>
  )
}
