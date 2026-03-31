import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItemButton,
  ListItemText,
  Button,
  Dialog,
  DialogContent,
  Divider
} from "@mui/material"
import { useState } from "react"
import saveFileWithPicker from "../../utils/FileSaver"

import AtomDBForm from "../../components/form_parts/AtomDB/AtomDB"
import { AgentsForm } from "../../components/form_parts/Agents/Agents"
import { BrokersForm } from "../../components/form_parts/Brokers/Brokers"
import { ParamsForm } from "../../components/form_parts/AgentsParams/AgentsParams"
import { EnvironmentForm } from "../../components/form_parts/Environment/Environment"

export default function MainPage() {
  const [config, setConfig] = useState({
    schema_version: "1.0",
    loaders: {
      metta: { image: "trueagi/das-1.0.0-metta-parser" },
      morkdb: { image: "trueagi/das-mork-loader-1.0.5" }
    }
  })

  const [section, setSection] = useState("atomdb")
  const [openJson, setOpenJson] = useState(false)

  const isConfigValid = () => {
  return (
    config.atomdb &&
    config.agents &&
    config.brokers &&
    config.params
  )
}

  const sections = [
    { key: "atomdb", label: "ATOMDB" },
    { key: "agents", label: "AGENTS" },
    { key: "brokers", label: "BROKERS" },
    { key: "params", label: "AGENT PARAMS" },
    { key: "environment", label: "ENVIRONMENT" }
  ]


  const updateSection = (sectionName, data) => {
    setConfig(prev => ({
      schema_version: prev.schema_version,
      atomdb: sectionName === "atomdb" ? data : prev.atomdb,
      loaders: prev.loaders,
      agents: sectionName === "agents" ? data : prev.agents,
      brokers: sectionName === "brokers" ? data : prev.brokers,
      params: sectionName === "params" ? data : prev.params,
      environment: sectionName === "environment" ? data : prev.environment
    }))
  }

  return (
    <Box sx={{ display: "flex", height: "100vh" }}>
      
      {/* SIDEBAR */}
      <Box sx={{ width: 220, borderRight: 1, borderColor: "divider" }}>
        <List>
          {sections.map(item => (
            <ListItemButton
              key={item.key}
              onClick={() => setSection(item.key)}
              selected={section === item.key}
            >
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>

        {/* EXPORT CONFIGURATION DATA */}
      
        <Button
          color="primary"
          disabled={!isConfigValid()}
          onClick={() => saveFileWithPicker(config)}
        >
          Export Configuration
        </Button>
      </Box>

      {/* CONTENT */}
      <Box sx={{ flex: 1, p: 4 }}>
        <Card>
          <CardContent>

            {section === "atomdb" && (
              <AtomDBForm onSectionSave={updateSection} />
            )}

            {section === "agents" && (
              <AgentsForm onSectionSave={updateSection} />
            )}

            {section === "brokers" && (
              <BrokersForm onSectionSave={updateSection} />
            )}

            {section === "params" && (
              <ParamsForm onSectionSave={updateSection} />
            )}

            {section === "environment" && (
              <EnvironmentForm onSectionSave={updateSection} />
            )}

          </CardContent>
        </Card>

        <Button
          variant="outlined"
          onClick={() => setOpenJson(true)}
          sx={{ mt: 2 }}
        >
          View JSON Config
        </Button>
      </Box>

      {/* JSON VIEW */}
      <Dialog
        open={openJson}
        onClose={() => setOpenJson(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogContent>
          <Typography>DAS Config Json:</Typography>
          <Divider sx={{ my: 1 }} />
          <pre>{JSON.stringify(config, null, 2)}</pre>
        </DialogContent>
      </Dialog>

    </Box>
  )
}