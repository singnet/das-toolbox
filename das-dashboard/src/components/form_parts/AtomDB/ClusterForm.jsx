import { Box, Button, TextField, Typography, Divider } from "@mui/material";
import { useState, useRef } from "react";

export function ClusterForm({ onChange }) {
  const nodes = useRef([]);
  const [count, setCount] = useState(1);

  const updateNode = (index, field, value) => {
    if (!nodes.current[index]) nodes.current[index] = {};
    nodes.current[index][field] = value;
    
    onChange(nodes.current);
  };

  const addServer = () => setCount(prev => prev + 1);

  return (
    <Box sx={{ mt: 2, p: 2, bgcolor: "#f5f5f5", borderRadius: 2 }}>
      <Typography variant="subtitle2" gutterBottom>Cluster Nodes Configuration</Typography>
      
      {Array.from({ length: count }).map((_, i) => (
        <Box key={i} sx={{ mb: 3, p: 2, border: '1px dashed #ccc' }}>
          <Typography variant="caption">Server #{i + 1}</Typography>
          
          <TextField 
            fullWidth 
            label="Username" 
            margin="dense"
            onChange={(e) => updateNode(i, "username", e.target.value)}
            placeholder="root"
          />
          
          <TextField 
            fullWidth 
            label="IP Address" 
            margin="dense"
            onChange={(e) => updateNode(i, "ip", e.target.value)}
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