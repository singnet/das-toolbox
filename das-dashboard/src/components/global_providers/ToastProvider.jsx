import { createContext, useContext, useState } from "react"
import { Snackbar, Alert } from "@mui/material"

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toast, setToast] = useState({
    open: false,
    message: "",
    severity: "success" // success | error | warning | info
  })

  const showToast = (message, severity = "success") => {
    setToast({
      open: true,
      message,
      severity
    })
  }

  const handleClose = (_, reason) => {
    if (reason === "clickaway") return
    setToast(prev => ({ ...prev, open: false }))
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      <Snackbar
        open={toast.open}
        autoHideDuration={3000}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={handleClose}
          severity={toast.severity}
          variant="filled"
          sx={{ width: "100%" }}
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
    throw new Error("useToast must be used with a ToastProvider")
  }

  return context
}