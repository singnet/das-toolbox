import {
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogContent,
  Divider,
  DialogTitle,
  DialogActions
} from "@mui/material"

import SettingsIcon from "@mui/icons-material/Settings"
import StorageIcon from "@mui/icons-material/Storage"
import DeveloperBoardIcon from '@mui/icons-material/DeveloperBoard';
import PublicIcon from "@mui/icons-material/Public"
import RestartAltIcon from "@mui/icons-material/RestartAlt"
import UploadFileIcon from "@mui/icons-material/UploadFile"
import DownloadIcon from "@mui/icons-material/Download"
import PreviewIcon from "@mui/icons-material/Preview"
import SaveIcon from "@mui/icons-material/Save"

import { useState } from "react"

import ExportConfigDialog from "../../components/configuration_page/ExportConfigDialog"
import { loadConfig, saveConfig } from "../../api/ConfigAPI"
import { useToast } from "../../components/global_providers/ToastProvider"

import AtomDBForm from "../../components/configuration_page/AtomDB/AtomDB"
import { AgentsForm } from "../../components/configuration_page/Agents/Agents"
import { EnvironmentForm } from "../../components/configuration_page/Environment/Environment"
import { getAgentByKey } from "../../components/configuration_page/Agents/agentRegistry"
import ConfigurationPreview from "../../components/configuration_page/ConfigurationPreview"

import { useConfig } from "../../components/global_providers/ConfigurationProvider"
import { handleLoadConfig } from "../../utils/FileLoader"

import {
  PageContainer,
  SidebarContainer,
  SidebarHeader,
  SidebarTitle,
  SidebarListContainer,
  SectionLabel,
  SidebarButtons,
  ContentContainer,
  ContentHeader,
  Breadcrumb,
  ContentTitle,
  ContentBody,
  CompactActionButton,
  CompactActionButtonPrimary,
  DialogButton,
  DialogPaper
} from "./SetupDasStyled"

const sections = [
  { key: "atomdb", label: "AtomDB", icon: StorageIcon },
  { key: "agents", label: "Agents", icon: DeveloperBoardIcon },
  { key: "environment", label: "Environment", icon: PublicIcon }
]

export default function SetupDasPage() {
  const {
    config,
    configSeed,
    applyLoadedConfiguration,
    resetConfiguration
  } = useConfig()

  const { showToast } = useToast()

  const [section, setSection] = useState("atomdb")
  const [activeAgent, setActiveAgent] = useState("query")
  const [openPreview, setOpenPreview] = useState(false)
  const [openResetDialog, setResetDialog] = useState(false)
  const [openExportDialog, setOpenExportDialog] = useState(false)

  const handleSave = async () => {
    try {
      await saveConfig(config)
      showToast({ message: "Configuration saved successfully", severity: "success" })
    } catch (error) {
      console.error(error)
      showToast({ message: "Failed to save configuration", severity: "error" })
    }
  }

  const handleLoad = async (event) => {
    handleLoadConfig(event, async ({ parsed }) => {
      try {
        const response = await loadConfig(parsed)
        applyLoadedConfiguration(response.content)
        showToast({ message: "Configuration loaded successfully", severity: "success" })
      } catch (error) {
        console.error(error)
        showToast({ message: "Failed to load configuration", severity: "error" })
      }
    })
  }

  const activeSection = sections.find((item) => item.key === section)
  const activeAgentMeta = section === "agents" ? getAgentByKey(activeAgent) : null

  return (
    <>
      <PageContainer>

        <SidebarContainer>

          <SidebarHeader>
            <SettingsIcon />
            <SidebarTitle>
              Settings
            </SidebarTitle>
          </SidebarHeader>

          <SidebarListContainer>

            <SectionLabel>
              Configuration
            </SectionLabel>

            <List disablePadding>

              {sections.map((item) => {
                const Icon = item.icon

                return (
                  <ListItemButton
                    key={item.key}
                    selected={section === item.key}
                    onClick={() => setSection(item.key)}
                  >
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Icon sx={{ fontSize: 18 }} />
                    </ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                )
              })}

            </List>

          </SidebarListContainer>

          <SidebarButtons>

            <CompactActionButton
              onClick={() => setResetDialog(true)}
            >
              <RestartAltIcon />
              Reset
            </CompactActionButton>

            <CompactActionButton
              component="label"
            >
              <UploadFileIcon />
              Load
              <input
                hidden
                type="file"
                accept=".json"
                onChange={handleLoad}
              />
            </CompactActionButton>

            <CompactActionButton onClick={() => setOpenExportDialog(true)}>
              <DownloadIcon />
              Export
            </CompactActionButton>

            <CompactActionButton onClick={handleSave}>
              <SaveIcon />
              Save
            </CompactActionButton>

            <CompactActionButtonPrimary
              onClick={() => setOpenPreview(true)}
            >
              <PreviewIcon />
              Preview
            </CompactActionButtonPrimary>

          </SidebarButtons>

        </SidebarContainer>

        <ContentContainer>

          <ContentHeader>

            <Breadcrumb>
              Settings <span>›</span> {activeSection?.label}
              {activeAgentMeta && (
                <> <span>›</span> {activeAgentMeta.label}</>
              )}
            </Breadcrumb>

            <ContentTitle>
              DAS Configuration
            </ContentTitle>

          </ContentHeader>

          <ContentBody flush={section === "agents"}>

            {section === "atomdb" && <AtomDBForm key={configSeed} />}
            {section === "agents" && (
              <AgentsForm
                key={configSeed}
                activeAgent={activeAgent}
                onAgentChange={setActiveAgent}
              />
            )}
            {section === "environment" && <EnvironmentForm key={configSeed} />}

          </ContentBody>

        </ContentContainer>

      </PageContainer>

      <Dialog
        open={openPreview}
        onClose={() => setOpenPreview(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{ sx: DialogPaper }}
      >
        <DialogContent>
          <Typography
            variant="h6"
            sx={{ fontSize: 16, fontWeight: 600, color: "#111827" }}
          >
            Configuration Preview
          </Typography>

          <Typography sx={{ fontSize: 13, color: "#6b7280", mt: 0.5, mb: 0 }}>
            Applied settings from each section
          </Typography>

          <Divider sx={{ mt: 2, mb: 2, borderColor: "#f0f1f3" }} />

          <ConfigurationPreview config={config} />
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2.5 }}>
          <DialogButton
            variant="primary"
            onClick={() => setOpenPreview(false)}
          >
            Close
          </DialogButton>
        </DialogActions>
      </Dialog>

      <Dialog
        open={openResetDialog}
        onClose={() => setResetDialog(false)}
        PaperProps={{ sx: DialogPaper }}
      >
        <DialogTitle sx={{ fontSize: 16, fontWeight: 600 }}>
          Confirm Reset
        </DialogTitle>

        <DialogContent sx={{ color: "#6b7280", fontSize: 14 }}>
          Are you sure you want to reset all settings?
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>

          <DialogButton
            variant="secondary"
            onClick={() => setResetDialog(false)}
          >
            Cancel
          </DialogButton>

          <DialogButton
            variant="primary"
            onClick={async () => {
              setResetDialog(false)
              try {
                await resetConfiguration()
                showToast({ message: "Configuration reset", severity: "success" })
              } catch (error) {
                console.error(error)
                showToast({ message: "Failed to reset configuration", severity: "error" })
              }
            }}
          >
            Confirm
          </DialogButton>

        </DialogActions>

      </Dialog>

      <ExportConfigDialog
        open={openExportDialog}
        onClose={() => setOpenExportDialog(false)}
        flatConfig={config}
      />
    </>
  )
}
