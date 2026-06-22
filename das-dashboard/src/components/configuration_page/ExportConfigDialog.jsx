import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
  CircularProgress,
  Box
} from "@mui/material"
import { useEffect, useState } from "react"
import { exportConfig, exportConfigScp, getExportTargets } from "../../api/ConfigAPI"
import { extractErrorDetails } from "../../api/APIUtils"
import { useToast } from "../global_providers/ToastProvider"
import saveFile from "../../utils/FileSaver"
import { DialogButton, DialogPaper } from "../../pages/setup_das/SetupDasStyled"

export default function ExportConfigDialog({ open, onClose }) {
  const { showToast } = useToast()

  const [destination, setDestination] = useState("local")
  const [targets, setTargets] = useState([])
  const [loadingTargets, setLoadingTargets] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!open) {
      return
    }

    async function loadTargets() {
      setLoadingTargets(true)
      setDestination("local")

      try {
        const response = await getExportTargets()
        setTargets(response.targets || [])
      } catch (error) {
        console.error(error)
        setTargets([])
        showToast({
          message: "Failed to load export targets",
          severity: "error",
          details: extractErrorDetails(error)
        })
        onClose()
      } finally {
        setLoadingTargets(false)
      }
    }

    loadTargets()
  }, [open, onClose, showToast])

  const handleConfirm = async () => {
    setSubmitting(true)

    try {
      if (destination === "local") {
        const response = await exportConfig()
        await saveFile(response.content)
        showToast({ message: "Configuration exported locally", severity: "success" })
        onClose()
        return
      }

      const response = await exportConfigScp(destination)
      showToast({
        message: response.message || "Configuration exported remotely",
        severity: "success"
      })
      onClose()
    } catch (error) {
      console.error(error)
      showToast({
        message: "Failed to export configuration",
        severity: "error",
        details: extractErrorDetails(error)
      })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog
      open={open}
      onClose={submitting ? undefined : onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: DialogPaper }}
    >
      <DialogTitle sx={{ fontSize: 16, fontWeight: 600 }}>
        Export Configuration
      </DialogTitle>

      <DialogContent sx={{ color: "#6b7280", fontSize: 14 }}>
        <Typography sx={{ fontSize: 14, mb: 2 }}>
          Export the saved configuration from the server.
        </Typography>

        {loadingTargets ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        ) : (
          <FormControl>
            <RadioGroup
              value={destination}
              onChange={(event) => setDestination(event.target.value)}
            >
              <FormControlLabel
                value="local"
                control={<Radio size="small" />}
                label="Download locally"
              />

              {targets.map((target) => (
                <FormControlLabel
                  key={target.ip}
                  value={target.ip}
                  control={<Radio size="small" />}
                  label={
                    <Box>
                      <Typography sx={{ fontSize: 14, color: "#111827" }}>
                        {target.ip}
                      </Typography>
                      {target.labels?.length > 0 && (
                        <Typography sx={{ fontSize: 12, color: "#9ca3af" }}>
                          {target.labels.join(", ")}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              ))}
            </RadioGroup>
          </FormControl>
        )}

        {!loadingTargets && targets.length === 0 && (
          <Typography sx={{ fontSize: 13, color: "#9ca3af", mt: 1 }}>
            No remote machines found in the saved configuration.
          </Typography>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
        <DialogButton variant="secondary" onClick={onClose} disabled={submitting}>
          Cancel
        </DialogButton>
        <DialogButton
          variant="primary"
          onClick={handleConfirm}
          disabled={submitting || loadingTargets}
        >
          {submitting ? "Exporting..." : "Export"}
        </DialogButton>
      </DialogActions>
    </Dialog>
  )
}
