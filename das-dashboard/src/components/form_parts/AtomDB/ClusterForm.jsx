import { Box, Button, TextField, Typography } from "@mui/material";
import { useState, useRef } from "react";

export function ClusterForm({ onChange }) {
  const nodes = useRef([]);
  const [count, setCount] = useState(3);

  const updateNode = (index, field, value) => {
    const current = nodes.current[index] || {};

    nodes.current[index] = {
      username: field === "username" ? value : current.username || "",
      ip: field === "ip" ? value : current.ip || "",
    };

    onChange(nodes.current);
  };

  const addServer = () => setCount((prev) => prev + 1);

  return (
    <Box sx={{ mt: 2, p: 2, bgcolor: "#f5f5f5", borderRadius: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Cluster Nodes Configuration
      </Typography>

      {Array.from({ length: count }).map((_, i) => (
        <Box key={i} sx={{ mb: 3, p: 2, border: "1px dashed #ccc" }}>
          <Typography variant="caption">Server #{i + 1}</Typography>


          <TextField
            fullWidth
            label="Username"
            margin="dense"
            defaultValue=""
            onChange={(e) => {
              let value = e.target.value
                .trim()
                .replace(/[^a-zA-Z0-9_-]/g, "");

              if (value.toLowerCase() === "root") {
                value = "";
              }

              e.target.value = value;
              updateNode(i, "username", value);
            }}
            placeholder="user"
          />


          <TextField
            fullWidth
            label="IP Address"
            margin="dense"
            defaultValue=""
            onChange={(e) => {
              let value = e.target.value
                .replace(/[^\d.]/g, "")
                .replace(/\.{2,}/g, ".");

              value = value.split(".").slice(0, 4).join(".");

              e.target.value = value;
              updateNode(i, "ip", value);
            }}
            placeholder="0.0.0.0"
          />
        </Box>
      ))}

      <Button
        variant="outlined"
        size="small"
        onClick={addServer}
        sx={{ mt: 1 }}
      >
        + Add Another Server
      </Button>
    </Box>
  );
}