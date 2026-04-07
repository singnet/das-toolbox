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

import SettingsIcon from "@mui/icons-material/Settings"

import "./SetupDas.css"
import { useState } from "react"
import saveFile  from "../../utils/FileSaver"

import AtomDBForm from "../../components/form_parts/AtomDB/AtomDB"
import { AgentsForm } from "../../components/form_parts/Agents/Agents"
import { BrokersForm } from "../../components/form_parts/Brokers/Brokers"
import { ParamsForm } from "../../components/form_parts/AgentsParams/AgentsParams"
import { EnvironmentForm } from "../../components/form_parts/Environment/Environment"
import { useConfig } from "../../components/global_components/ConfigurationProvider"

export default function SetupDasPage() {

  const { config } = useConfig()

  const [section, setSection] = useState("atomdb")
  const [openJson, setOpenJson] = useState(false)

  const isNotEmpty = (obj) => obj && Object.keys(obj).length > 0

  const isConfigValid = () => {
    return (
      isNotEmpty(config.atomdb) &&
      isNotEmpty(config.agents) &&
      isNotEmpty(config.brokers) &&
      isNotEmpty(config.params) &&
      isNotEmpty(config.environment)
    )
  }

  const sections = [
    { key: "atomdb", label: "ATOMDB" },
    { key: "agents", label: "AGENTS" },
    { key: "brokers", label: "BROKERS" },
    { key: "params", label: "AGENT PARAMS" },
    { key: "environment", label: "ENVIRONMENT" }
  ]

  return (
        <Box className="main-page">
          <Box className="backgroundBox">

            {/* SIDEBAR */}
            <Box className="mainSidebar">

              {/* HEADER */}
              <Box className="sidebarHeader">
                <SettingsIcon fontSize="small" />
                <Typography sx={{borderRadius:"3px"}} variant="subtitle1">Settings</Typography>
              </Box>

              {/* LIST */}
              <List className="sidebarList">
                {sections.map(item => (
                  <ListItemButton
                    key={item.key}
                    onClick={() => setSection(item.key)}
                    selected={section === item.key}
                    className="sidebarItem"
                  >
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                ))}
              </List>

              {/* BUTTONS */}
              <Box className="sidebarButtons">

                <Button
                  variant="contained"
                  disabled={!isConfigValid()}
                  onClick={() => saveFile(config)}
                  sx={{
                    backgroundColor: "#4caf50",
                    "&:hover": { backgroundColor: "#43a047" }
                  }}
                >
                  Export Configuration
                </Button>

                <Button
                  variant="contained"
                  onClick={() => setOpenJson(true)}
                  sx={{
                    backgroundColor: "#1976d2",
                    color: "#fff",
                    "&:hover": { backgroundColor: "#1565c0" }
                  }}
                >
                  View JSON Config
                </Button>

              </Box>
            </Box>

            {/* CONTENT */}
            <Box className="formBox">
              <Card
                elevation={0}
                className="formContent"
                sx={{
                  borderRadius: 0,
                  display: "flex", 
                  flexDirection: "column"
                }}
              >
                <CardContent 
                  sx={{ 
                    flex: 1, 
                    overflowY: "auto",
                    minHeight: 0
                  }}
                >
                  {section === "atomdb" && <AtomDBForm/>}
                  {section === "agents" && <AgentsForm />}
                  {section === "brokers" && <BrokersForm />}
                  {section === "params" && <ParamsForm />}
                  {section === "environment" && <EnvironmentForm />}
                </CardContent>
              </Card>
            </Box>

            {/* JSON VIEW */}
            <Dialog
              open={openJson}
              onClose={() => setOpenJson(false)}
              fullWidth
              maxWidth="md"
            >
              <DialogContent>
                <Typography>DAS Config Preview:</Typography>
                <Divider sx={{ my: 1 }} />
                <pre>{JSON.stringify(config, null, 2)}</pre>
              </DialogContent>
            </Dialog>

          </Box>
        </Box>
  )
}