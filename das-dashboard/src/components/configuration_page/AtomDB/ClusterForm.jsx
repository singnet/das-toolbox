import { Box, Button, TextField, Typography, IconButton } from "@mui/material"
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline"
import { useEffect, useRef, useState } from "react"
import { ipv4Field } from "../formValidation"

function createEmptyNode() {
  return { context: "default", username: "", ip: "" }
}

function seedNodes(initialNodes) {
  if (Array.isArray(initialNodes) && initialNodes.length > 0) {
    return structuredClone(initialNodes)
  }

  return [createEmptyNode()]
}

export function ClusterForm({ type, initialNodes = [], onChange }) {
  const nodes = useRef(seedNodes(initialNodes))
  const [count, setCount] = useState(nodes.current.length)

  const syncNodes = () => {
    onChange(structuredClone(nodes.current))
  }

  useEffect(() => {
    syncNodes()
  }, [])

  const updateNode = (index, field, value) => {
    const current = nodes.current[index] || createEmptyNode()

    nodes.current[index] = {
      ...current,
      [field]: value
    }

    syncNodes()
  }

  const addServer = () => {
    nodes.current.push(createEmptyNode())
    setCount(nodes.current.length)
    syncNodes()
  }

  const removeServer = (index) => {
    nodes.current.splice(index, 1)
    setCount(Math.max(nodes.current.length, 0))
    syncNodes()
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
        {type === "mongo" ? "MongoDB Cluster Nodes" : "Redis Cluster Nodes"}
      </Typography>

      <Box sx={{ maxHeight: "280px", overflowY: "auto", pr: 0.5 }}>
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
              gridTemplateColumns: "40px 1fr 1fr auto",
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
              required
              defaultValue={nodes.current[i]?.username ?? ""}
              onChange={(e) => {
                updateNode(i, "username", e.target.value)
              }}
            />

            <TextField
              fullWidth
              label="IP Address"
              size="small"
              margin="none"
              required
              defaultValue={nodes.current[i]?.ip ?? ""}
              onChange={(e) => {
                updateNode(i, "ip", e.target.value)
              }}
              {...ipv4Field}
            />

            <IconButton
              size="small"
              color="error"
              aria-label="Remove node"
              onClick={() => removeServer(i)}
            >
              <DeleteOutlineIcon fontSize="small" />
            </IconButton>
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
