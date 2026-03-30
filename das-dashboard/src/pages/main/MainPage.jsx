import { Box, Card, CardContent, Typography, List, ListItemButton, ListItemText, Button, Dialog, DialogContent } from "@mui/material"
import { useState } from "react"
import AtomDBForm from "../../components/form_parts/AtomDB/AtomDB"
import { AgentsForm } from "../../components/form_parts/Agents/Agents"

export default function MainPage() {
  const [config, setConfig] = useState({ "schema_version": "1.0", "loaders": {"metta": {"image": "trueagi/das-1.0.0-metta-parser"},"morkdb": {"image": "trueagi/das-mork-loader-1.0.3"}},
})
  const [section, setSection] = useState("atomdb")
  const [openJson, setOpenJson] = useState(false)

const updateSection = (sectionName, data) => {
  setConfig(prev => {
    const next = {
      schema_version: prev.schema_version,
      atomdb: sectionName === "atomdb" ? data : prev.atomdb,
      loaders: prev.loaders,
      agents: sectionName === "agents" ? data : prev.agents,
      brokers: sectionName === "brokers" ? data : prev.brokers
    }

    return next
  })
}

  return (
    <Box sx={{ display: "flex", height: "100vh" }}>
      <Box sx={{ width: 220, borderRight: 1, borderColor: 'divider' }}>
        <List>
          {["atomdb", "agents", "brokers"].map(item => (
            <ListItemButton key={item} onClick={() => setSection(item)} selected={section === item}>
              <ListItemText primary={item.toUpperCase()} />
            </ListItemButton>
          ))}
        </List>
      </Box>

      <Box sx={{ flex: 1, p: 4 }}>
        <Card>
          <CardContent>
            {section === "atomdb" && <AtomDBForm onSectionSave={updateSection} />}
            {section === "agents" && <AgentsForm onSectionSave={updateSection}></AgentsForm>}
          </CardContent>
        </Card>

        <Button variant="outlined" onClick={() => setOpenJson(true)} sx={{ mt: 2 }}>
          View JSON Config
        </Button>
      </Box>

      <Dialog open={openJson} onClose={() => setOpenJson(false)} fullWidth maxWidth="md">
        <DialogContent>
          <pre>{JSON.stringify(config, null, 2)}</pre>
        </DialogContent>
      </Dialog>
    </Box>
  )
}