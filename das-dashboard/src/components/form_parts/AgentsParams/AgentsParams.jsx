import {
  Box,
  Button,
  TextField,
  Typography,
  Switch,
  FormControlLabel
} from "@mui/material"
import { useRef } from "react"
import { useConfig } from "../../global_components/ConfigurationProvider"
import { useToast } from "../../global_components/ToastProvider"

export function ParamsForm() {

  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()

  const defaults = getDefault().params || {}

  const form = useRef({
    query: {
      max_answers: defaults?.query?.max_answers ?? 100,
      max_bundle_size: defaults?.query?.max_bundle_size ?? 1000,
      count_flag: defaults?.query?.count_flag ?? true,
      attention_update_flag: defaults?.query?.attention_update_flag ?? false,
      unique_assignment_flag: defaults?.query?.unique_assignment_flag ?? true,
      positive_importance_flag: defaults?.query?.positive_importance_flag ?? false,
      populate_metta_mapping: defaults?.query?.populate_metta_mapping ?? true,
      use_metta_as_query_tokens: defaults?.query?.use_metta_as_query_tokens ?? true
    },
    link_creation: {
      repeat_count: defaults?.link_creation?.repeat_count ?? 1,
      query_interval: defaults?.link_creation?.query_interval ?? 0,
      query_timeout: defaults?.link_creation?.query_timeout ?? 0
    },
    evolution: {
      elitism_rate: defaults?.evolution?.elitism_rate ?? 0.08,
      max_generations: defaults?.evolution?.max_generations ?? 10,
      population_size: defaults?.evolution?.population_size ?? 50,
      selection_rate: defaults?.evolution?.selection_rate ?? 0.1,
      total_attention_tokens: defaults?.evolution?.total_attention_tokens ?? 100000
    },
    context: {
      context: defaults?.context?.context ?? "context",
      use_cache: defaults?.context?.use_cache ?? true,
      enforce_cache_recreation: defaults?.context?.enforce_cache_recreation ?? false,
      initial_rent_rate: defaults?.context?.initial_rent_rate ?? 0.25,
      initial_spreading_rate_lowerbound: defaults?.context?.initial_spreading_rate_lowerbound ?? 0.5,
      initial_spreading_rate_upperbound: defaults?.context?.initial_spreading_rate_upperbound ?? 0.7
    }
  })

  const handleSave = () => {
    updateSection("params", structuredClone(form.current))
    showToast("Params saved successfully!")
  }

  const sectionBox = {
    border: "1px solid #eee",
    borderRadius: 2,
    p: 2,
    display: "flex",
    flexDirection: "column",
    gap: 2
  }

  const grid2 = {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 2
  }

  const numberProps = {
    slotProps: {
      htmlInput: { onWheel: (e) => e.target.blur() }
    }
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>

      <Typography variant="h6">
        Params Configuration
      </Typography>

      {/* QUERY */}
      <Box sx={sectionBox}>
        <Typography variant="subtitle2">Query</Typography>

        <Box sx={grid2}>
          <TextField
            label="Max Answers"
            type="number"
            defaultValue={form.current.query.max_answers}
            {...numberProps}
            onChange={e => form.current.query.max_answers = Number(e.target.value)}
          />
          <TextField
            label="Max Bundle Size"
            type="number"
            defaultValue={form.current.query.max_bundle_size}
            {...numberProps}
            onChange={e => form.current.query.max_bundle_size = Number(e.target.value)}
          />
        </Box>

        <Box sx={grid2}>
          <FormControlLabel control={<Switch defaultChecked={form.current.query.count_flag} onChange={e => form.current.query.count_flag = e.target.checked} />} label="Count Flag" />
          <FormControlLabel control={<Switch defaultChecked={form.current.query.attention_update_flag} onChange={e => form.current.query.attention_update_flag = e.target.checked} />} label="Attention Update" />
          <FormControlLabel control={<Switch defaultChecked={form.current.query.unique_assignment_flag} onChange={e => form.current.query.unique_assignment_flag = e.target.checked} />} label="Unique Assignment" />
          <FormControlLabel control={<Switch defaultChecked={form.current.query.positive_importance_flag} onChange={e => form.current.query.positive_importance_flag = e.target.checked} />} label="Positive Importance" />
          <FormControlLabel control={<Switch defaultChecked={form.current.query.populate_metta_mapping} onChange={e => form.current.query.populate_metta_mapping = e.target.checked} />} label="Metta Mapping" />
          <FormControlLabel control={<Switch defaultChecked={form.current.query.use_metta_as_query_tokens} onChange={e => form.current.query.use_metta_as_query_tokens = e.target.checked} />} label="Use Metta Tokens" />
        </Box>
      </Box>

      {/* LINK */}
      <Box sx={sectionBox}>
        <Typography variant="subtitle2">Link Creation</Typography>

        <Box sx={grid2}>
          <TextField label="Repeat Count" type="number" defaultValue={form.current.link_creation.repeat_count} {...numberProps} onChange={e => form.current.link_creation.repeat_count = Number(e.target.value)} />
          <TextField label="Query Interval" type="number" defaultValue={form.current.link_creation.query_interval} {...numberProps} onChange={e => form.current.link_creation.query_interval = Number(e.target.value)} />
          <TextField label="Query Timeout" type="number" defaultValue={form.current.link_creation.query_timeout} {...numberProps} onChange={e => form.current.link_creation.query_timeout = Number(e.target.value)} />
        </Box>
      </Box>

      {/* EVOLUTION */}
      <Box sx={sectionBox}>
        <Typography variant="subtitle2">Evolution</Typography>

        <Box sx={grid2}>
          <TextField label="Elitism Rate" type="number" defaultValue={form.current.evolution.elitism_rate} {...numberProps} onChange={e => form.current.evolution.elitism_rate = Number(e.target.value)} />
          <TextField label="Max Generations" type="number" defaultValue={form.current.evolution.max_generations} {...numberProps} onChange={e => form.current.evolution.max_generations = Number(e.target.value)} />
          <TextField label="Population Size" type="number" defaultValue={form.current.evolution.population_size} {...numberProps} onChange={e => form.current.evolution.population_size = Number(e.target.value)} />
          <TextField label="Selection Rate" type="number" defaultValue={form.current.evolution.selection_rate} {...numberProps} onChange={e => form.current.evolution.selection_rate = Number(e.target.value)} />
          <TextField label="Total Attention Tokens" type="number" defaultValue={form.current.evolution.total_attention_tokens} {...numberProps} onChange={e => form.current.evolution.total_attention_tokens = Number(e.target.value)} />
        </Box>
      </Box>

      {/* CONTEXT */}
      <Box sx={sectionBox}>
        <Typography variant="subtitle2">Context</Typography>

        <Box sx={grid2}>
          <TextField label="Context Name" defaultValue={form.current.context.context} onChange={e => form.current.context.context = e.target.value} />
          <TextField label="Initial Rent Rate" type="number" defaultValue={form.current.context.initial_rent_rate} {...numberProps} onChange={e => form.current.context.initial_rent_rate = Number(e.target.value)} />
          <TextField label="Spread Lowerbound" type="number" defaultValue={form.current.context.initial_spreading_rate_lowerbound} {...numberProps} onChange={e => form.current.context.initial_spreading_rate_lowerbound = Number(e.target.value)} />
          <TextField label="Spread Upperbound" type="number" defaultValue={form.current.context.initial_spreading_rate_upperbound} {...numberProps} onChange={e => form.current.context.initial_spreading_rate_upperbound = Number(e.target.value)} />

          <FormControlLabel control={<Switch defaultChecked={form.current.context.use_cache} onChange={e => form.current.context.use_cache = e.target.checked} />} label="Use Cache" />
          <FormControlLabel control={<Switch defaultChecked={form.current.context.enforce_cache_recreation} onChange={e => form.current.context.enforce_cache_recreation = e.target.checked} />} label="Force Cache Reset" />
        </Box>
      </Box>

      <Button variant="contained" color="success" onClick={handleSave}>
        Save params section
      </Button>

    </Box>
  )
}