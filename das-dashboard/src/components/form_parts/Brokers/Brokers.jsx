import { Box, Button, TextField, Typography } from "@mui/material"
import { useRef } from "react"
import { useConfig } from "../../global_components/ConfigurationProvider"
import { useToast } from "../../global_components/ToastProvider"

export function BrokersForm() {

  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()

  const defaults = getDefault().brokers || {}

  const section = useRef({
    attention: {
      endpoint: defaults?.attention?.endpoint || "localhost:40001"
    },
    context: {
      endpoint: defaults?.context?.endpoint || "localhost:40006",
      ports_range: defaults?.context?.ports_range || "46000:46999"
    },
    atomdb: {
      endpoint: defaults?.atomdb?.endpoint || "localhost:40007",
      ports_range: defaults?.atomdb?.ports_range || "47000:47999"
    }
  })

  const getPort = (endpoint) => endpoint.split(":")[1]
  const getStart = (range) => range.split(":")[0]
  const getEnd = (range) => range.split(":")[1]

  const updateEndpoint = (key, value) => {
    section.current[key].endpoint = `localhost:${value}`
  }

  const updateRangeStart = (key, value) => {
    const [, end] = section.current[key].ports_range.split(":")
    section.current[key].ports_range = `${value}:${end}`
  }

  const updateRangeEnd = (key, value) => {
    const [start] = section.current[key].ports_range.split(":")
    section.current[key].ports_range = `${start}:${value}`
  }

  const SectionBlock = ({ title, name, hasRange = false }) => (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mt: 1 }}>
        {title}
      </Typography>

      <TextField
        label={`${title} Port`}
        fullWidth
        defaultValue={getPort(section.current[name].endpoint)}
        onChange={e => updateEndpoint(name, e.target.value)}
      />

      {hasRange && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 1
          }}
        >
          <TextField
            label="Port range start"
            fullWidth
            defaultValue={getStart(section.current[name].ports_range)}
            onChange={e => updateRangeStart(name, e.target.value)}
          />

          <TextField
            label="Port range end"
            fullWidth
            defaultValue={getEnd(section.current[name].ports_range)}
            onChange={e => updateRangeEnd(name, e.target.value)}
          />
        </Box>
      )}

    </Box>
  )

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>

      <Typography variant="h6">Brokers Configuration</Typography>

      <SectionBlock title="Attention" name="attention" />
      <SectionBlock title="Context" name="context" hasRange />
      <SectionBlock title="AtomDB" name="atomdb" hasRange />

      <Button
        variant="contained"
        color="success"
        onClick={() =>{
          updateSection("brokers", structuredClone(section.current))
          showToast("Brokers saved successfully!")
        }}
      >
        Save brokers section
      </Button>
    </Box>
  )
}