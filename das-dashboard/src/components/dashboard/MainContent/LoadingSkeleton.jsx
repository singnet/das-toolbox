import { CircularProgress, Typography, Stack } from "@mui/material";
import { CloudUploadOutlined, Sensors } from "@mui/icons-material";

export function EmptyState() {
  return (
    <Stack
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{
        gridColumn: "span 2",
        minHeight: "60vh",
        gap: 2,
        opacity: 0.5,
      }}
    >
      <CloudUploadOutlined sx={{ fontSize: 80, color: "grey.500" }} />
      <Typography variant="h5" color="white" sx={{ fontWeight: 300 }}>
        Dashboard Inativo
      </Typography>
      <Typography color="grey.400" align="center">
        No configuration file detected. <br />
        Please upload your configuration file using the button by the sidebar.
      </Typography>
    </Stack>
  );
}

export function LoadingOverlay() {
  return (
    <Stack
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{
        gridColumn: "span 2",
        minHeight: "60vh",
        gap: 3,
      }}
    >
      <Stack alignItems="center" justifyContent="center" sx={{ position: 'relative' }}>
        <CircularProgress size={70} thickness={2} sx={{ color: "#00e676" }} />
        <Sensors sx={{ position: 'absolute', fontSize: 30, color: "#00e676" }} />
      </Stack>
      <Typography variant="h6" sx={{ color: "#4e4e4e", fontWeight: 300, letterSpacing: '1px' }}>
        Loading server metrics...
      </Typography>
    </Stack>
  );
}