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
import PreviewIcon from "@mui/icons-material/Preview"
import SaveIcon from "@mui/icons-material/Save"

import { useState, useRef } from "react"

import { loadConfig, saveConfig } from "../../api/ConfigAPI"
import { extractErrorDetails } from "../../api/APIUtils"
import { useToast } from "../../components/global_providers/ToastProvider"

import AtomDBForm from "../../components/configuration_page/AtomDB/AtomDB"
import { AgentsForm } from "../../components/configuration_page/Agents/Agents"
import { EnvironmentForm } from "../../components/configuration_page/Environment/Environment"
import { getAgentByKey } from "../../components/configuration_page/Agents/agentRegistry"
import ConfigurationPreview from "../../components/configuration_page/ConfigurationPreview"

import { useConfig } from "../../components/global_providers/ConfigurationProvider"
import { handleLoadConfig } from "../../utils/FileLoader"
import saveFile from "../../utils/FileSaver"

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
  const [openSaveCopyDialog, setOpenSaveCopyDialog] = useState(false)
  const [savedConfigContent, setSavedConfigContent] = useState(null)
  const [openLoadDialog, setOpenLoadDialog] = useState(false)
  const [pendingLoadConfig, setPendingLoadConfig] = useState(null)
  const [disableActions, setDisableActions] = useState(false)
  const loadInputRef = useRef(null)


  const handleSave = async () => {
    try {

      // Disables all buttons temporarily until action is over, this prevents double clicking or misuse that could potentially cause an error on the server.
      setDisableActions(true)
      document.body.style.cursor = 'wait'; // Editing directly on the DOM

      const response = await saveConfig(config)

      showToast({
        message: response?.message || "Configuration saved successfully",
        severity: "success"
      })

      if (response?.content) {
        setSavedConfigContent(response.content)
        setOpenSaveCopyDialog(true)
      }

    } catch (error) {
      console.error(error)
      showToast({
        message: "Failed to save configuration",
        severity: "error",
        details: extractErrorDetails(error)
      })
    }

    // Sets back to normal after action is completed.
    setDisableActions(false)
    document.body.style.cursor = 'default'
  }

  const handleLoad = async (event) => {
    handleLoadConfig(event, ({ parsed, file }) => {
      setPendingLoadConfig({
        parsed,
        fileName: file?.name || "config.json"
      })
      setOpenLoadDialog(true)
    })
  }

  const closeLoadDialog = () => {
    setOpenLoadDialog(false)
    setPendingLoadConfig(null)

    if (loadInputRef.current) {
      loadInputRef.current.value = ""
    }
  }

  const handleConfirmLoad = async () => {
    if (!pendingLoadConfig) {
      closeLoadDialog()
      return
    }

    try {
      setDisableActions(true)
      document.body.style.cursor = "wait"

      const response = await loadConfig(pendingLoadConfig.parsed)
      applyLoadedConfiguration(response.content)
      showToast({ message: "Configuration loaded successfully", severity: "success" })
    } catch (error) {
      console.error(error)
      showToast({
        message: "Failed to load configuration",
        severity: "error",
        details: extractErrorDetails(error)
      })
    } finally {
      setDisableActions(false)
      document.body.style.cursor = "default"
      closeLoadDialog()
    }
  }

  const closeSaveCopyDialog = () => {
    setOpenSaveCopyDialog(false)
    setSavedConfigContent(null)
  }

  const handleSaveLocalCopy = async () => {
    if (!savedConfigContent) {
      closeSaveCopyDialog()
      return
    }

    try {
      await saveFile(savedConfigContent)
    } catch (error) {
      console.error(error)
      showToast({
        message: "Failed to save local copy",
        severity: "error",
        details: extractErrorDetails(error)
      })
    } finally {
      closeSaveCopyDialog()
    }
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
              disabled={disableActions}
            >
              <RestartAltIcon />
              Reset
            </CompactActionButton>

            <CompactActionButton
              component="label"
              disabled={disableActions}
            >
              <UploadFileIcon />
              Load
              <input
                ref={loadInputRef}
                hidden
                type="file"
                accept=".json"
                onChange={handleLoad}
              />
            </CompactActionButton>

            <CompactActionButton disabled={disableActions} onClick={handleSave}>
              <SaveIcon />
              Save
            </CompactActionButton>

            <CompactActionButton
              onClick={() => setOpenPreview(true)}
              disabled={disableActions}
            >
              <PreviewIcon />
              Preview
            </CompactActionButton>

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
                showToast({
                  message: "Failed to reset configuration",
                  severity: "error",
                  details: extractErrorDetails(error)
                })
              }
            }}
          >
            Confirm
          </DialogButton>

        </DialogActions>

      </Dialog>

      <Dialog
        open={openSaveCopyDialog}
        onClose={closeSaveCopyDialog}
        PaperProps={{ sx: DialogPaper }}
      >
        <DialogTitle sx={{ fontSize: 16, fontWeight: 600 }}>
          Save a local copy?
        </DialogTitle>

        <DialogContent sx={{ color: "#6b7280", fontSize: 14 }}>
          Your configuration was saved on the server. Would you like to download a copy of the configuration file to your computer?
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
          <DialogButton
            variant="secondary"
            onClick={closeSaveCopyDialog}
          >
            Not now
          </DialogButton>

          <DialogButton
            variant="primary"
            onClick={handleSaveLocalCopy}
          >
            Save copy
          </DialogButton>
        </DialogActions>
      </Dialog>

      <Dialog
        open={openLoadDialog}
        onClose={closeLoadDialog}
        PaperProps={{ sx: DialogPaper }}
      >
        <DialogTitle sx={{ fontSize: 16, fontWeight: 600 }}>
          Load configuration?
        </DialogTitle>

        <DialogContent sx={{ color: "#6b7280", fontSize: 14 }}>
          {pendingLoadConfig?.fileName ? (
            <>
              <strong>{pendingLoadConfig.fileName}</strong> will become the current and active configuration on the server, replacing any existing configuration. Do you want to continue?
            </>
          ) : (
            <>This file will become the current and active configuration on the server, replacing any existing configuration. Do you want to continue?</>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
          <DialogButton
            variant="secondary"
            onClick={closeLoadDialog}
          >
            Cancel
          </DialogButton>

          <DialogButton
            variant="primary"
            onClick={handleConfirmLoad}
          >
            Load
          </DialogButton>
        </DialogActions>
      </Dialog>
    </>
  )
}
