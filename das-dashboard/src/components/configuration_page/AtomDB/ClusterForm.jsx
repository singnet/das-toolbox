import { Box, Button, TextField, Typography } from "@mui/material"
import { useState, useRef } from "react"

export function ClusterForm({ type, onChange }) {
  const nodes = useRef([])
  const [count, setCount] = useState(3)

  const updateNode = (index, field, value) => {
    const current = nodes.current[index] || {
      username: "",
      ip: ""
    }

    nodes.current[index] = {
      ...current,
      [field]: value
    }

    onChange(structuredClone(nodes.current))
  }

  const addServer = () => {
    setCount(prev => prev + 1)
  }

  return (
    <Box
      sx={{
        p: 2,
        bgcolor: "#f5f5f5",
        borderRadius: 2,
        width: "100%",
        boxSizing: "border-box"
      }}
    >
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
        {type === "mongo"
          ? "MongoDB Cluster Nodes"
          : "Redis Cluster Nodes"}
      </Typography>

      <Box sx={{ maxDeep: "280px", overflowY: "auto", pr: 0.5 }}>
        {Array.from({ length: count }).map((_, i) => (
          <Box
            key={i}
            sx={{
              mb: 1,
              p: 1.5,
              border: "1px dashed #ccc",
              borderRadius: 1,
              bgcolor: "#ffffff",
              display: "grid",
              gridTemplateColumns: "40px 1fr 1fr",
              gap: 1.5,
              alignItems: "center"
            }}
          >
            <Typography variant="caption" sx={{ fontWeight: 600, color: "#666" }}>
              #{i + 1}
            </Typography>

            <TextField
              fullWidth
              label="Username"
              size="small"
              margin="none"
              defaultValue=""
              onChange={(e) => {
                updateNode(i, "username", e.target.value)
              }}
            />

            <TextField
              fullWidth
              label="IP Address"
              size="small"
              margin="none"
              defaultValue=""
              onChange={(e) => {
                updateNode(i, "ip", e.target.value)
              }}
            />
          </Box>
        ))}
      </Box>

      <Button
        variant="outlined"
        size="small"
        onClick={addServer}
        sx={{ mt: 1, width: "100%", py: 0.5, fontSize: "0.75rem" }}
      >
        + Add Another Server
      </Button>
    </Box>
  )
}