import styled from "@emotion/styled";
import { CircularProgress, Typography, Stack, Card } from "@mui/material";
import { CloudUploadOutlined, Sensors, BarChart as BarChartIcon } from "@mui/icons-material";

const ChartPlaceholderContainer = styled(Card)({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "360px",
  margin: "25px",
  backgroundColor: "rgba(0, 0, 0, 0.02)",
  border: "2px dashed rgba(0, 0, 0, 0.12)",
  boxShadow: "none",
  color: "#9e9e9e",
  gap: "8px"
});

export function EmptyState({ 
  title = <>No saved configuration detected. <br /> Open the Configuration page, apply your settings, and click Save.</>, 
  description = null,
  icon: IconComponent = CloudUploadOutlined 
}) {
  return (
    <Stack
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{ gridColumn: "span 2", minHeight: "60vh", gap: 1, opacity: 0.5 }}
    >
      <IconComponent sx={{ fontSize: 80, color: "grey.500", mb: 1 }} />
      
      <Typography variant="h6" color="grey.500" align="center" sx={{ fontWeight: 400 }}>
        {title}
      </Typography>

      {description && (
        <Typography variant="body2" color="grey.400" align="center">
          {description}
        </Typography>
      )}
    </Stack>
  );
}

export function LoadingOverlay({ text = "Loading server metrics..."}) {
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
        {text}
      </Typography>
    </Stack>
  );
}

export function ChartPlaceholder({ title }) {
  return (
    <ChartPlaceholderContainer>
      <BarChartIcon sx={{ fontSize: 48, color: "rgba(0, 0, 0, 0.26)" }} />
      <Typography variant="subtitle1" fontWeight="600" color="text.secondary">
        {title}
      </Typography>
      <Typography variant="body2" color="text.disabled">
        WAITING FOR DATA TO DISPLAY...
      </Typography>
    </ChartPlaceholderContainer>
  );
}