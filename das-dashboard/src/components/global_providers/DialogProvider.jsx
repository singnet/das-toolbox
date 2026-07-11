import {
  createContext,
  useContext,
  useState
} from "react"

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button
} from "@mui/material"

const DialogContext = createContext(null)

export function DialogProvider({ children }) {
  const [dialog, setDialog] = useState({
    open: false,
    title: "",
    message: "",
    onConfirm: null,
    onCancel: null,
    type: "info"
  })

  const showInfo = ({
    title = "Information",
    message
  }) => {
    setDialog({
      open: true,
      title,
      message,
      type: "info",
      onConfirm: null,
      onCancel: null
    })
  }

  const showConfirm = ({
    title = "Confirm",
    message,
    onConfirm,
    onCancel
  }) => {
    setDialog({
      open: true,
      title,
      message,
      type: "confirm",
      onConfirm,
      onCancel
    })
  }

  const closeDialog = () => {
    setDialog(prev => ({
      ...prev,
      open: false,
      onConfirm: null,
      onCancel: null
    }))
  }

  const handleConfirm = () => {
    dialog.onConfirm?.()
    closeDialog()
  }

  const handleCancel = () => {
    dialog.onCancel?.()
    closeDialog()
  }

  return (
    <DialogContext.Provider
      value={{
        showInfo,
        showConfirm
      }}
    >
      {children}

      <Dialog
        open={dialog.open}
        onClose={handleCancel}
      >
        <DialogTitle>
          {dialog.title}
        </DialogTitle>

        <DialogContent>
          <DialogContentText>
            {dialog.message}
          </DialogContentText>
        </DialogContent>

        <DialogActions>
          {dialog.type === "confirm" ? (
            <>
              <Button onClick={handleCancel}>
                Cancel
              </Button>

              <Button onClick={handleConfirm}>
                Confirm
              </Button>
            </>
          ) : (
            <Button onClick={closeDialog}>
              Close
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </DialogContext.Provider>
  )
}

export function useDialog() {
  const context = useContext(DialogContext)

  if (!context) {
    throw new Error(
      "useDialog must be used within DialogProvider"
    )
  }

  return context
}