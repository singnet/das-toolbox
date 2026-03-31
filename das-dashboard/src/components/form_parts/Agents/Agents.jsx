import { Box, Button, TextField, Typography } from "@mui/material"
import { useRef } from "react"

export function AgentsForm({ onSectionSave }) {
  const form = useRef({
    queryPort: "40002",
    queryRange: "42000:42999",

    linkPort: "40003",
    linkRange: "43000:43999",

    inferencePort: "40004",
    inferenceRange: "44000:44999",

    evolutionPort: "40005",
    evolutionRange: "45000:45999"
  })

  const isValidRange = (range) => {
    const match = range.match(/^(\d+):(\d+)$/)
    if (!match) return false

    const start = Number(match[1])
    const end = Number(match[2])

    return start < end && start >= 1 && end <= 65535
  }

  const handleSave = () => {
    const data = form.current

    const ranges = [
      data.queryRange,
      data.linkRange,
      data.inferenceRange,
      data.evolutionRange
    ]

    const section = {
      query: {
        endpoint: `localhost:${data.queryPort}`,
        ports_range: data.queryRange
      },
      link_creation: {
        endpoint: `localhost:${data.linkPort}`,
        ports_range: data.linkRange
      },
      inference: {
        endpoint: `localhost:${data.inferencePort}`,
        ports_range: data.inferenceRange
      },
      evolution: {
        endpoint: `localhost:${data.evolutionPort}`,
        ports_range: data.evolutionRange
      }
    }

    onSectionSave("agents", section)
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6">Agents Configuration</Typography>

      <TextField
        label="Query Port"
        type="number"
        onChange={(e) => (form.current.queryPort = e.target.value)}
        defaultValue={40002}
      />
      <TextField
        label="Query Ports Range (start:end)"
        onChange={(e) => (form.current.queryRange = e.target.value)}
        defaultValue={"42000:42999"}
      />

      <TextField
        label="Link Creation Port"
        type="number"
        onChange={(e) => (form.current.linkPort = e.target.value)}
        defaultValue={40003}
      />
      <TextField
        label="Link Creation Ports Range"
        onChange={(e) => (form.current.linkRange = e.target.value)}
        defaultValue={"43000:43999"}
      />

      <TextField
        label="Inference Port"
        type="number"
        onChange={(e) => (form.current.inferencePort = e.target.value)}
        defaultValue={40004}
      />
      <TextField
        label="Inference Ports Range"
        onChange={(e) => (form.current.inferenceRange = e.target.value)}
        defaultValue={"44000:44999"}
      />

      <TextField
        label="Evolution Port"
        type="number"
        onChange={(e) => (form.current.evolutionPort = e.target.value)}
        defaultValue={40005}
      />
      <TextField
        label="Evolution Ports Range"
        onChange={(e) => (form.current.evolutionRange = e.target.value)}
        defaultValue={"45000:45999"}
      />

      <Button variant="contained" color="success" onClick={handleSave}>
        Save agents section
      </Button>
    </Box>
  )
}