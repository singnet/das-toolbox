import {
  createContext,
  useContext,
  useState
} from "react"

import {
  Snackbar,
  Alert,
  Button
} from "@mui/material"

import { useDialog } from "./DialogProvider"

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const { showInfo } = useDialog()

  const [toast, setToast] = useState({
    open: false,
    message: "",
    severity: "success",
    details: null
  })

  const showToast = ({
    message,
    severity = "success",
    details = null
  }) => {
    setToast({
      open: true,
      message,
      severity,
      details
    })
  }

  const handleClose = (_, reason) => {
    if (reason === "clickaway") return

    setToast(prev => ({
      ...prev,
      open: false
    }))
  }

  const handleDetails = () => {
    showInfo({
      title: "Server Error",
      message: toast.details
    })
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      <Snackbar
        open={toast.open}
        autoHideDuration={8000}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center"
        }}
      >
        <Alert
          onClose={handleClose}
          severity={toast.severity}
          variant="filled"
          sx={{ width: "100%" }}
          action={
            toast.details && (
              <Button
                color="inherit"
                size="small"
                onClick={handleDetails}
              >
                DETAILS
              </Button>
            )
          }
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)

  if (!context) {
    throw new Error(
      "useToast must be used with ToastProvider"
    )
  }

  return context
}