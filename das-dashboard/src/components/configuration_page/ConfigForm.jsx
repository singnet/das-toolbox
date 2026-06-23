import { Box } from "@mui/material"

export function ConfigForm({ onSubmit, children, sx }) {
  return (
    <Box
      component="form"
      sx={{ display: "contents", ...sx }}
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit(event)
      }}
    >
      {children}
    </Box>
  )
}
