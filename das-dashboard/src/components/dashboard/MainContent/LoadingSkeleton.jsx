import styled from "@emotion/styled";
import { CircularProgress, Typography, Stack, Card } from "@mui/material";
import { CloudUploadOutlined, Sensors, BarChart as BarChartIcon } from "@mui/icons-material";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

const ChartPlaceholderContainer = styled(Card)({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "320px",
  margin: "0",
  backgroundColor: palette.surface,
  border: `1px dashed ${palette.border}`,
  borderRadius: 12,
  boxShadow: palette.shadow,
  color: palette.textMuted,
  gap: "8px"
});

export function EmptyState({
  title = "No saved configuration detected.",
  description = "Open the Configuration page, apply your settings, and click Save.",
  icon: IconComponent = CloudUploadOutlined
}) {
  return (
    <Stack
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{
        gridColumn: "span 2",
        minHeight: "52vh",
        gap: 1.5,
        px: 3
      }}
    >
      <BoxLikeSurface>
        <IconComponent sx={{ fontSize: 48, color: palette.accent, opacity: 0.7 }} />
      </BoxLikeSurface>

      <Typography
        variant="h6"
        align="center"
        sx={{ fontWeight: 600, color: palette.textPrimary, fontSize: 18 }}
      >
        {title}
      </Typography>

      {description && (
        <Typography
          variant="body2"
          align="center"
          sx={{ color: palette.textSecondary, maxWidth: 420, lineHeight: 1.6 }}
        >
          {description}
        </Typography>
      )}
    </Stack>
  );
}

function BoxLikeSurface({ children }) {
  return (
    <Stack
      alignItems="center"
      justifyContent="center"
      sx={{
        width: 88,
        height: 88,
        borderRadius: "50%",
        backgroundColor: palette.accentLight,
        border: `1px solid ${palette.accentMuted}`,
        mb: 0.5
      }}
    >
      {children}
    </Stack>
  );
}

export function LoadingOverlay({ text = "Loading server metrics..." }) {
  return (
    <Stack
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{
        gridColumn: "span 2",
        minHeight: "52vh",
        gap: 3,
      }}
    >
      <Stack alignItems="center" justifyContent="center" sx={{ position: "relative" }}>
        <CircularProgress size={56} thickness={3} sx={{ color: palette.accent }} />
        <Sensors sx={{ position: "absolute", fontSize: 24, color: palette.accent }} />
      </Stack>
      <Typography
        variant="h6"
        sx={{ color: palette.textSecondary, fontWeight: 500, fontSize: 15 }}
      >
        {text}
      </Typography>
    </Stack>
  );
}

export function ChartPlaceholder({ title, description = "Waiting for data to display" }) {
  return (
    <ChartPlaceholderContainer elevation={0}>
      <BarChartIcon sx={{ fontSize: 40, color: palette.textMuted }} />
      <Typography variant="subtitle1" fontWeight={600} sx={{ color: palette.textPrimary }}>
        {title}
      </Typography>
      <Typography variant="body2" sx={{ color: palette.textMuted }}>
        {description}
      </Typography>
    </ChartPlaceholderContainer>
  );
}
