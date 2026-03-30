import { Box, Card, CardContent, Typography, List, ListItemButton, ListItemText, Button, Dialog, DialogContent } from "@mui/material"
import { useState } from "react"
import AtomDBForm from "../../components/form_parts/AtomDB/AtomDB"

export default function MainPage() {
  const [config, setConfig] = useState({ schema_version: "1.0" })
  const [section, setSection] = useState("atomdb")
  const [openJson, setOpenJson] = useState(false)

  const updateSection = (sectionName, data) => {
    setConfig(prev => ({
      ...prev,
      [sectionName]: data
    }))
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
            {/* Outras sections seguem o mesmo padrão: onSectionSave={updateSection} */}
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