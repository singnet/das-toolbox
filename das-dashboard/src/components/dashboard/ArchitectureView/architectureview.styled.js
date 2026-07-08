import { styled } from "@mui/material/styles";
import { Box } from "@mui/material";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

export const Container = styled(Box)({
  padding: "24px 28px 28px",
  boxSizing: "border-box"
});

export const Grid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
  gap: 16,
});

export const StyledCard = styled(Box, {
  shouldForwardProp: (prop) => prop !== "selected"
})(({ selected }) => ({
  position: "relative",
  background: selected ? palette.accentLight : palette.surface,
  border: `1px solid ${selected ? palette.accent : palette.borderSubtle}`,
  borderRadius: 12,
  padding: 18,
  color: palette.textPrimary,
  minHeight: 240,
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  boxShadow: selected
    ? `0 0 0 3px ${palette.accentMuted}, 0 8px 24px rgba(79, 70, 229, 0.12)`
    : palette.shadow,
  transition: "border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease",
  overflow: "hidden",

  "&::before": selected
    ? {
        content: '""',
        position: "absolute",
        top: 14,
        left: 0,
        bottom: 14,
        width: 4,
        borderRadius: "0 4px 4px 0",
        backgroundColor: palette.accent
      }
    : {},

  "&:hover": {
    borderColor: selected ? palette.accent : palette.accentMuted,
    boxShadow: selected
      ? `0 0 0 3px ${palette.accentMuted}, 0 10px 28px rgba(79, 70, 229, 0.16)`
      : "0 4px 20px rgba(79, 70, 229, 0.08)"
  }
}));

export const MetricsRow = styled(Box)({
  display: "flex",
  gap: 8,
  marginTop: 12,
});

export const Metric = styled(Box)({
  flex: 1,
  background: palette.surfaceMuted,
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 8,
  padding: "8px 10px",
  textAlign: "center",
});
