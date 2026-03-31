import { Box, Button, TextField, Typography } from "@mui/material"
import { useRef } from "react"

export function BrokersForm({ onSectionSave }) {
  const form = useRef({
    attentionPort: "40001",

    contextPort: "40006",
    contextRange: "46000:46999",

    atomdbPort: "40007",
    atomdbRange: "47000:47999"
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

    const section = {
      attention: {
        endpoint: `localhost:${data.attentionPort}`
      },
      context: {
        endpoint: `localhost:${data.contextPort}`,
        ports_range: data.contextRange
      },
      atomdb: {
        endpoint: `localhost:${data.atomdbPort}`,
        ports_range: data.atomdbRange
      }
    }

    onSectionSave("brokers", section)
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6">Brokers Configuration</Typography>

      <TextField
        label="Attention Broker Port"
        type="number"
        onChange={(e) => (form.current.attentionPort = e.target.value)}
        defaultValue={40001}
      />

      <TextField
        label="Context Broker Port"
        type="number"
        onChange={(e) => (form.current.contextPort = e.target.value)}
        defaultValue={40006}
      />
      <TextField
        label="Context Broker Range"
        helperText={"Port range must be in 'start:end' format"}
        onChange={(e) => (form.current.contextRange = e.target.value)}
        defaultValue={"46000:46999"} 
      />

      <TextField
        label="AtomDB Broker Port"
        type="number"
        onChange={(e) => (form.current.atomdbPort = e.target.value)}
        defaultValue={40007}
      />
      <TextField
        label="AtomDB Broker Range"
        helperText={"Port range must be in 'start:end' format"}
        onChange={(e) => (form.current.atomdbRange = e.target.value)}
        defaultValue={"47000:47999"} 
      />

      <Button variant="contained" color="success" onClick={handleSave}>
        Save brokers section
      </Button>
    </Box>
  )
}