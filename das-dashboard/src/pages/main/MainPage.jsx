import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  MenuItem
} from "@mui/material"
import { useState } from "react"
import { DEFAULT_JSON } from "../../assets/default_json"
import AtomDBForm from "../../components/form_parts/AtomDB"

export default function MainPage() {
    const [config, setConfig] = useState(() => structuredClone(DEFAULT_JSON))

    const handleChange = (path, value) => {
    setConfig(prev => {
        const newConfig = { ...prev } // gets shallow copy of the config
        const keys = path.split(".") // atomdb.type.redis => ["atomdb", "type", "redis"]
        let obj = newConfig // attributes config to obj so we can traverse it and update

        for (let i = 0; i < keys.length - 1; i++) {
        obj = obj[keys[i]] // traverses keys in the config until it gets to the last level (last item in the array)
        }

        obj[keys[keys.length - 1]] = value // changes the config value in last key for the new value.
        return { ...newConfig }
    })
    }

  return (
    <Box
      sx={{
        display: "flex",
        gap: 2,
        p: 2,
        height: "100dvh",
        bgcolor: "#121212"
      }}
    >
      <Card sx={{ width: 340, overflow: "auto" }}>
        <CardContent>
            <Typography variant="h6">Configuration</Typography>

            <AtomDBForm config={config} onChange={handleChange}></AtomDBForm>
        </CardContent>
      </Card>

      {/* JSON Preview */}
      <Card sx={{ flex: 1 }}>
        <CardContent>
          <Typography variant="h6">JSON Preview</Typography>

          <Box
            component="pre"
            sx={{
              mt: 2,
              p: 2,
              bgcolor: "#1e1e1e",
              color: "#00ff9f",
              borderRadius: 1,
              overflow: "auto",
              fontSize: 13
            }}
          >
            {JSON.stringify(config, null, 2)}
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}