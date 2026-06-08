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
      onConfirm: null
    })
  }

  const showConfirm = ({
    title = "Confirm",
    message,
    onConfirm
  }) => {
    setDialog({
      open: true,
      title,
      message,
      type: "confirm",
      onConfirm
    })
  }

  const closeDialog = () => {
    setDialog(prev => ({
      ...prev,
      open: false
    }))
  }

  const handleConfirm = () => {
    dialog.onConfirm?.()
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
        onClose={closeDialog}
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
              <Button onClick={closeDialog}>
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