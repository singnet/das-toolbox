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
  Divider,
  DialogTitle,
  DialogActions
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
import handleLoadConfig from "../../utils/FileLoader"

export default function SetupDasPage() {

  const { config, loadExternalConfiguration, resetConfiguration } = useConfig()

  const [section, setSection] = useState("atomdb")
  const [openJson, setOpenJson] = useState(false)
  const [openResetDialog, setResetDialog] = useState(false)

  const sections = [
    { key: "atomdb", label: "AtomDB" },
    { key: "agents", label: "Agents" },
    { key: "brokers", label: "Brokers" },
    { key: "params", label: "Agent Params" },
    { key: "environment", label: "Environment" }
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
                component="label"
                sx={{
                    backgroundColor: "#f8a231",
                    color: "#fff",
                    "&:hover": { backgroundColor: "#e4942c" }
                  }}
                onClick={() => setResetDialog(true)}
                >
                  Reset Configuration
                </Button>

                <Button
                  variant="contained"
                  component="label"
                  sx={{
                    backgroundColor: "#8ba73f",
                    color: "#fff",
                    "&:hover": { backgroundColor: "#7b9436" }
                  }}
                >
                  Load Config
                  <input
                    type="file"
                    hidden
                    accept=".json"
                    onChange={(e) => handleLoadConfig(e, loadExternalConfiguration)}
                  />
                </Button>

                <Button
                  variant="contained"
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

            {/* CONFIRM RESET */}
            <Dialog
              open={openJson}
              onClose={() => setOpenJson(false)}
              fullWidth
              maxWidth="md"
            >
              <DialogContent>
                <Box sx={{display: "flex", alignContent: "center", justifyContent: "space-between"}}>
                  <Typography sx={{alignContent:"center"}}>DAS Config Preview:</Typography>
                  <Button onClick={() => setOpenJson(false)}>Close</Button>
                </Box>
                <Divider sx={{ my: 1 }} />
                <pre>{JSON.stringify(config, null, 2)}</pre>
              </DialogContent>
            </Dialog>

            <Dialog
              open={openResetDialog}
              onClose={() => setOpenJson(false)}
              fullWidth
              maxWidth="md"
            >
              <DialogContent>
                <DialogTitle>Confirm reset</DialogTitle>
                <DialogContent>Are you sure you want to reset your settings? Everything will turn into default values.</DialogContent>
                <DialogActions>
                  <Button onClick={() => {setResetDialog(false)}}>Cancel</Button>
                  <Button onClick={() => {setResetDialog(false); resetConfiguration()}} autoFocus>Confirm</Button>
                </DialogActions>
              </DialogContent>
            </Dialog>

          </Box>
        </Box>
  )
}