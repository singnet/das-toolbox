import { TextField } from "@mui/material"
import { FieldGrid } from "../Agents.styled"

const numberProps = {
  slotProps: {
    htmlInput: { onWheel: (e) => e.target.blur() }
  }
}

export default function EvolutionParams({ formRef }) {
  return (
    <FieldGrid>
      <TextField
        label="Population Size"
        type="number"
        size="small"
        defaultValue={formRef.current.population_size}
        {...numberProps}
        onChange={(e) => {
          formRef.current.population_size = Number(e.target.value)
        }}
      />
      <TextField
        label="Max Generations"
        type="number"
        size="small"
        defaultValue={formRef.current.max_generations}
        {...numberProps}
        onChange={(e) => {
          formRef.current.max_generations = Number(e.target.value)
        }}
      />
      <TextField
        label="Elitism Rate"
        type="number"
        size="small"
        defaultValue={formRef.current.elitism_rate}
        {...numberProps}
        onChange={(e) => {
          formRef.current.elitism_rate = Number(e.target.value)
        }}
      />
      <TextField
        label="Selection Rate"
        type="number"
        size="small"
        defaultValue={formRef.current.selection_rate}
        {...numberProps}
        onChange={(e) => {
          formRef.current.selection_rate = Number(e.target.value)
        }}
      />
    </FieldGrid>
  )
}