import { Box, Button, TextField, Typography, Switch, FormControlLabel } from "@mui/material"
import { useRef } from "react"

export function ParamsForm({ onSectionSave }) {
  const form = useRef({
    query: {
      max_answers: 100,
      max_bundle_size: 1000,
      count_flag: true,
      attention_update_flag: false,
      unique_assignment_flag: true,
      positive_importance_flag: false,
      populate_metta_mapping: true,
      use_metta_as_query_tokens: true
    },
    link_creation: {
      repeat_count: 1,
      query_interval: 0,
      query_timeout: 0
    },
    evolution: {
      elitism_rate: 0.08,
      max_generations: 10,
      population_size: 50,
      selection_rate: 0.1,
      total_attention_tokens: 100000
    },
    context: {
      context: "context",
      use_cache: true,
      enforce_cache_recreation: false,
      initial_rent_rate: 0.25,
      initial_spreading_rate_lowerbound: 0.5,
      initial_spreading_rate_upperbound: 0.7
    }
  })

  const handleSave = () => {
    onSectionSave("params", form.current)
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h6">Params Configuration</Typography>


      <Typography variant="subtitle2">Query</Typography>

      <TextField
        label="Max Answers"
        type="number"
        defaultValue={100}
        onChange={(e) => form.current.query.max_answers = Number(e.target.value)}
      />

      <TextField
        label="Max Bundle Size"
        type="number"
        defaultValue={1000}
        onChange={(e) => form.current.query.max_bundle_size = Number(e.target.value)}
      />

      <FormControlLabel
        control={
          <Switch
            defaultChecked
            onChange={(e) => form.current.query.count_flag = e.target.checked}
          />
        }
        label="Count Flag"
      />

      <FormControlLabel
        control={
          <Switch
            onChange={(e) => form.current.query.attention_update_flag = e.target.checked}
          />
        }
        label="Attention Update Flag"
      />

      <FormControlLabel
        control={
          <Switch
            defaultChecked
            onChange={(e) => form.current.query.unique_assignment_flag = e.target.checked}
          />
        }
        label="Unique Assignment Flag"
      />

      <FormControlLabel
        control={
          <Switch
            onChange={(e) => form.current.query.positive_importance_flag = e.target.checked}
          />
        }
        label="Positive Importance Flag"
      />

      <FormControlLabel
        control={
          <Switch
            defaultChecked
            onChange={(e) => form.current.query.populate_metta_mapping = e.target.checked}
          />
        }
        label="Populate Metta Mapping"
      />

      <FormControlLabel
        control={
          <Switch
            defaultChecked
            onChange={(e) => form.current.query.use_metta_as_query_tokens = e.target.checked}
          />
        }
        label="Use Metta as Query Tokens"
      />


      <Typography variant="subtitle2">Link Creation</Typography>

      <TextField
        label="Repeat Count"
        type="number"
        defaultValue={1}
        onChange={(e) => form.current.link_creation.repeat_count = Number(e.target.value)}
      />

      <TextField
        label="Query Interval"
        type="number"
        defaultValue={0}
        onChange={(e) => form.current.link_creation.query_interval = Number(e.target.value)}
      />

      <TextField
        label="Query Timeout"
        type="number"
        defaultValue={0}
        onChange={(e) => form.current.link_creation.query_timeout = Number(e.target.value)}
      />

      {/* EVOLUTION */}
      <Typography variant="subtitle2">Evolution</Typography>

      <TextField
        label="Elitism Rate"
        type="number"
        defaultValue={0.08}
        onChange={(e) => form.current.evolution.elitism_rate = Number(e.target.value)}
      />

      <TextField
        label="Max Generations"
        type="number"
        defaultValue={10}
        onChange={(e) => form.current.evolution.max_generations = Number(e.target.value)}
      />

      <TextField
        label="Population Size"
        type="number"
        defaultValue={50}
        onChange={(e) => form.current.evolution.population_size = Number(e.target.value)}
      />

      <TextField
        label="Selection Rate"
        type="number"
        defaultValue={0.1}
        onChange={(e) => form.current.evolution.selection_rate = Number(e.target.value)}
      />

      <TextField
        label="Total Attention Tokens"
        type="number"
        defaultValue={100000}
        onChange={(e) => form.current.evolution.total_attention_tokens = Number(e.target.value)}
      />

      {/* CONTEXT */}
      <Typography variant="subtitle2">Context</Typography>

      <TextField
        label="Context Name"
        defaultValue="context"
        onChange={(e) => form.current.context.context = e.target.value}
      />

      <FormControlLabel
        control={
          <Switch
            defaultChecked
            onChange={(e) => form.current.context.use_cache = e.target.checked}
          />
        }
        label="Use Cache"
      />

      <FormControlLabel
        control={
          <Switch
            onChange={(e) => form.current.context.enforce_cache_recreation = e.target.checked}
          />
        }
        label="Enforce Cache Recreation"
      />

      <TextField
        label="Initial Rent Rate"
        type="number"
        defaultValue={0.25}
        onChange={(e) => form.current.context.initial_rent_rate = Number(e.target.value)}
      />

      <TextField
        label="Spreading Rate Lowerbound"
        type="number"
        defaultValue={0.5}
        onChange={(e) => form.current.context.initial_spreading_rate_lowerbound = Number(e.target.value)}
      />

      <TextField
        label="Spreading Rate Upperbound"
        type="number"
        defaultValue={0.7}
        onChange={(e) => form.current.context.initial_spreading_rate_upperbound = Number(e.target.value)}
      />

      <Button variant="contained" color="success" onClick={handleSave}>
        Save params section
      </Button>
    </Box>
  )
}