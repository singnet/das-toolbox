import { Box, Button, TextField, Typography } from "@mui/material"
import { useRef } from "react"
import { useConfig } from "../../global_components/ConfigurationProvider"
import { useToast } from "../../global_components/ToastProvider"

export function AgentsForm() {

  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()

  const defaults = getDefault().agents || {}

  const section = useRef({
    query: {
      endpoint: defaults?.query?.endpoint || "localhost:40002",
      ports_range: defaults?.query?.ports_range || "42000:42999"
    },
    link_creation: {
      endpoint: defaults?.link_creation?.endpoint || "localhost:40003",
      ports_range: defaults?.link_creation?.ports_range || "43000:43999"
    },
    inference: {
      endpoint: defaults?.inference?.endpoint || "localhost:40004",
      ports_range: defaults?.inference?.ports_range || "44000:44999"
    },
    evolution: {
      endpoint: defaults?.evolution?.endpoint || "localhost:40005",
      ports_range: defaults?.evolution?.ports_range || "45000:45999"
    }
  })

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

  const getPort = (endpoint) => endpoint.split(":")[1]
  const getStart = (range) => range.split(":")[0]
  const getEnd = (range) => range.split(":")[1]

  const SectionBlock = ({ title, name }) => (
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

    </Box>
  )

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      
      <Typography variant="h6">Agents Configuration</Typography>

      <SectionBlock title="Query" name="query" />
      <SectionBlock title="Link Creation" name="link_creation" />
      <SectionBlock title="Inference" name="inference" />
      <SectionBlock title="Evolution" name="evolution" />

      <Button
        variant="contained"
        color="success"
        onClick={() => {
          updateSection("agents", structuredClone(section.current))
          showToast("Agents saved successfully!")
        }}
      >
        Save agents section
      </Button>
    </Box>
  )
}