import { Box, Button, TextField, Typography, styled, keyframes } from "@mui/material";

export const paletteQuery = {
  background: "#f4f4f6",
  surface: "#ffffff",
  surfaceMuted: "#f9fafb",
  sidebar: "#ffffff",
  border: "#e5e7eb",
  borderSubtle: "#f0f1f3",
  textPrimary: "#111827",
  textSecondary: "#6b7280",
  textMuted: "#9ca3af",
  accent: "#4f46e5",
  accentHover: "#4338ca",
  accentLight: "#eef2ff",
  accentMuted: "#e0e7ff",
  success: "#33e622",
  successHover: "#24ac18",
  danger: "#dc2626",
  dangerHover: "#b91c1c",
  shadow: "0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 16px rgba(15, 23, 42, 0.04)"
};

export const PageContainer = styled(Box)({
  display: "flex",
  flexDirection: "row",
  width: "100%",
  height: "100%",
  maxWidth: "100%",
  overflow: "hidden",
  boxSizing: "border-box",
  backgroundColor: paletteQuery.background
});

export const ParamSideBar = styled(Box)({
  display: "flex",
  flexDirection: "column",
  width: 320,
  minWidth: 320,
  flexShrink: 0,
  height: "100%",
  backgroundColor: paletteQuery.sidebar,
  borderRight: `1px solid ${paletteQuery.border}`,
  boxSizing: "border-box",
  overflow: "hidden"
});

export const SideBarTitleHeader = styled(Box)({
  flexShrink: 0,
  padding: "18px 20px 16px",
  borderBottom: `1px solid ${paletteQuery.borderSubtle}`,
  background: `linear-gradient(180deg, ${paletteQuery.accentLight} 0%, ${paletteQuery.surface} 100%)`
});

export const SideBarEyebrow = styled(Typography)({
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  color: paletteQuery.accent,
  marginBottom: 4
});

export const SideBarTitle = styled(Typography)({
  fontSize: 16,
  fontWeight: 600,
  color: paletteQuery.textPrimary,
  letterSpacing: "-0.02em"
});

export const SideBarSubtitle = styled(Typography)({
  fontSize: 12,
  color: paletteQuery.textSecondary,
  marginTop: 4,
  lineHeight: 1.45
});

export const ParameterSectionBody = styled(Box)({
  flex: 1,
  minHeight: 0,
  overflowY: "auto",
  padding: "16px 18px 20px",
  display: "flex",
  flexDirection: "column",
  gap: 16,
  boxSizing: "border-box"
});

export const ParameterDivider = styled(Box)({
  height: 1,
  backgroundColor: paletteQuery.borderSubtle,
  margin: "4px 0"
});

export const ParameterFieldGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: 12
});

export const ParameterSwitchStack = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: 2
});

export const SliderRow = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: 6
});

export const SliderLabelRow = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 8
});

export const SliderLabel = styled(Typography)({
  fontSize: 13,
  fontWeight: 500,
  color: paletteQuery.textPrimary
});

export const SliderValue = styled(Typography)({
  fontSize: 12,
  fontWeight: 600,
  color: paletteQuery.textSecondary,
  fontVariantNumeric: "tabular-nums"
});

export const QueryContent = styled(Box)({
  flex: 1,
  minWidth: 0,
  minHeight: 0,
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
  backgroundColor: paletteQuery.background
});

export const QueryContentHeader = styled(Box)({
  flexShrink: 0,
  padding: "14px 28px 12px",
  borderBottom: `1px solid ${paletteQuery.borderSubtle}`,
  backgroundColor: paletteQuery.surface,
  boxSizing: "border-box"
});

export const QueryBreadcrumb = styled(Typography)({
  fontSize: 12,
  color: paletteQuery.textMuted,
  fontWeight: 500,
  "& span": {
    color: paletteQuery.textSecondary
  }
});

export const QueryPageTitle = styled(Typography)({
  fontSize: 18,
  fontWeight: 600,
  color: paletteQuery.textPrimary,
  letterSpacing: "-0.02em",
  marginTop: 2
});

export const QueryPageSubtitle = styled(Typography)({
  fontSize: 13,
  color: paletteQuery.textSecondary,
  marginTop: 2
});

export const QueryContentBody = styled(Box)({
  flex: 1,
  minHeight: 0,
  overflowY: "auto",
  padding: "20px 28px 28px",
  display: "flex",
  flexDirection: "column",
  gap: 14,
  boxSizing: "border-box"
});

export const QueryCard = styled(Box)({
  backgroundColor: paletteQuery.surface,
  border: `1px solid ${paletteQuery.borderSubtle}`,
  borderRadius: 12,
  boxShadow: paletteQuery.shadow,
  padding: "14px 16px 16px",
  display: "flex",
  flexDirection: "column",
  gap: 12,
  boxSizing: "border-box"
});

export const QueryToolbar = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12
});

export const QueryKindChip = styled(Box)({
  display: "inline-flex",
  alignItems: "center",
  height: 28,
  padding: "0 12px",
  borderRadius: 8,
  border: `1px solid ${paletteQuery.accentMuted}`,
  backgroundColor: paletteQuery.accentLight,
  color: paletteQuery.accent,
  fontSize: 13,
  fontWeight: 600
});

export const QueryToolbarActions = styled(Box)({
  display: "flex",
  alignItems: "center",
  gap: 8
});

export const RunButton = styled(Button)({
  textTransform: "none",
  fontWeight: 600,
  borderRadius: 8,
  minWidth: 80,
  height: 34,
  boxShadow: "none",
  backgroundColor: paletteQuery.accent,
  "&:hover": {
    backgroundColor: paletteQuery.accentHover,
    boxShadow: "none"
  }
});

export const StopButton = styled(Button)({
  textTransform: "none",
  fontWeight: 600,
  borderRadius: 8,
  minWidth: 80,
  height: 34,
  boxShadow: "none",
  color: paletteQuery.textSecondary,
  backgroundColor: paletteQuery.surface,
  border: `1px solid ${paletteQuery.border}`,
  "&:hover": {
    backgroundColor: paletteQuery.surfaceMuted,
    boxShadow: "none"
  }
});

export const QueryInput = styled(TextField)({
  "& .MuiOutlinedInput-root": {
    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
    fontSize: 13,
    lineHeight: 1.5,
    backgroundColor: paletteQuery.surfaceMuted,
    borderRadius: 10,
    alignItems: "flex-start",
    "& fieldset": {
      borderColor: paletteQuery.border
    },
    "&:hover fieldset": {
      borderColor: paletteQuery.accentMuted
    },
    "&.Mui-focused fieldset": {
      borderColor: paletteQuery.accent,
      borderWidth: 1
    }
  },
  "& .MuiOutlinedInput-input": {
    padding: "12px 14px"
  }
});

export const GeneralStatusBar = styled(Box)({
  display: "flex",
  alignItems: "center",
  flexWrap: "wrap",
  gap: 12,
  padding: "12px 16px",
  borderRadius: 12,
  border: `1px solid ${paletteQuery.borderSubtle}`,
  background: `linear-gradient(180deg, ${paletteQuery.surface} 0%, ${paletteQuery.surfaceMuted} 100%)`,
  boxShadow: paletteQuery.shadow,
  boxSizing: "border-box"
});

const statusPulse = keyframes`
  0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.35); }
  70% { box-shadow: 0 0 0 6px rgba(79, 70, 229, 0); }
  100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }
`;

export const StatusPill = styled(Box, {
  shouldForwardProp: (prop) => prop !== "tone"
})(({ tone }) => {
  const tones = {
    idle: {
      backgroundColor: paletteQuery.surfaceMuted,
      color: paletteQuery.textSecondary,
      borderColor: paletteQuery.border
    },
    running: {
      backgroundColor: paletteQuery.accentLight,
      color: paletteQuery.accent,
      borderColor: paletteQuery.accentMuted
    },
    done: {
      backgroundColor: "rgba(51, 230, 34, 0.12)",
      color: paletteQuery.successHover,
      borderColor: "rgba(51, 230, 34, 0.35)"
    },
    stopped: {
      backgroundColor: "rgba(220, 38, 38, 0.08)",
      color: paletteQuery.danger,
      borderColor: "rgba(220, 38, 38, 0.25)"
    }
  };

  const style = tones[tone] || tones.idle;

  return {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    height: 28,
    padding: "0 12px",
    borderRadius: 999,
    border: `1px solid ${style.borderColor}`,
    backgroundColor: style.backgroundColor,
    color: style.color,
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: "0.02em",
    animation: tone === "running" ? `${statusPulse} 1.8s ease-out infinite` : "none"
  };
});

export const StatusDot = styled(Box, {
  shouldForwardProp: (prop) => prop !== "tone"
})(({ tone }) => ({
  width: 7,
  height: 7,
  borderRadius: "50%",
  backgroundColor:
    tone === "running"
      ? paletteQuery.accent
      : tone === "done"
        ? paletteQuery.successHover
        : tone === "stopped"
          ? paletteQuery.danger
          : paletteQuery.textMuted
}));

export const StatusMetrics = styled(Box)({
  display: "flex",
  alignItems: "center",
  flexWrap: "wrap",
  gap: 0,
  minWidth: 0
});

export const StatusMetric = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: 1,
  padding: "0 14px",
  minWidth: 88
});

export const StatusMetricLabel = styled(Typography)({
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
  color: paletteQuery.textMuted
});

export const StatusMetricValue = styled(Typography)({
  fontSize: 14,
  fontWeight: 600,
  color: paletteQuery.textPrimary,
  fontVariantNumeric: "tabular-nums"
});

export const StatusDivider = styled(Box)({
  width: 1,
  alignSelf: "stretch",
  minHeight: 34,
  backgroundColor: paletteQuery.borderSubtle
});

export const ResultsSection = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: 14,
  minHeight: 0
});

export const ChartsRow = styled(Box)({
  display: "grid",
  gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)",
  gap: 14,
  minHeight: 320,
  "@media (max-width: 1100px)": {
    gridTemplateColumns: "1fr"
  }
});

export const ParameterLimitField = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: 8
});

export const QueryResultsCard = styled(Box)({
  backgroundColor: paletteQuery.surface,
  border: `1px solid ${paletteQuery.borderSubtle}`,
  borderRadius: 12,
  boxShadow: paletteQuery.shadow,
  display: "flex",
  flexDirection: "column",
  minHeight: 220,
  maxHeight: 360,
  overflow: "hidden",
  boxSizing: "border-box"
});

export const AnswerHistogramCard = styled(Box)({
  backgroundColor: paletteQuery.surface,
  border: `1px solid ${paletteQuery.borderSubtle}`,
  borderRadius: 12,
  boxShadow: paletteQuery.shadow,
  display: "flex",
  flexDirection: "column",
  minHeight: 300,
  overflow: "hidden",
  boxSizing: "border-box"
});

export const PanelHeader = styled(Box)({
  flexShrink: 0,
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  padding: "12px 16px",
  borderBottom: `1px solid ${paletteQuery.borderSubtle}`
});

export const PanelTitle = styled(Typography)({
  fontSize: 14,
  fontWeight: 600,
  color: paletteQuery.textPrimary
});

export const PanelMeta = styled(Typography)({
  fontSize: 12,
  fontWeight: 500,
  color: paletteQuery.textMuted
});

export const ResultsList = styled(Box)({
  flex: 1,
  minHeight: 0,
  overflowY: "auto",
  padding: "4px 0"
});

export const ResultRow = styled(Box)({
  display: "flex",
  alignItems: "flex-start",
  gap: 10,
  padding: "10px 16px",
  borderBottom: `1px solid ${paletteQuery.borderSubtle}`,
  "&:last-child": {
    borderBottom: "none"
  }
});

export const ResultAccent = styled(Box)({
  width: 3,
  minHeight: 16,
  marginTop: 3,
  borderRadius: 2,
  backgroundColor: paletteQuery.accent,
  flexShrink: 0
});

export const ResultText = styled(Typography)({
  fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
  fontSize: 12.5,
  lineHeight: 1.45,
  color: paletteQuery.textPrimary,
  wordBreak: "break-word"
});

export const ResultsFooter = styled(Box)({
  flexShrink: 0,
  padding: "10px 16px 14px",
  borderTop: `1px solid ${paletteQuery.borderSubtle}`
});

export const ResultsFooterLink = styled(Typography)({
  fontSize: 13,
  fontWeight: 500,
  color: paletteQuery.accent,
  cursor: "pointer",
  "&:hover": {
    color: paletteQuery.accentHover
  }
});

export const HistogramBody = styled(Box)({
  flex: 1,
  minHeight: 0,
  padding: "4px 8px 8px",
  boxSizing: "border-box"
});

export const EmptyPanelState = styled(Box)({
  flex: 1,
  minHeight: 180,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 24,
  color: paletteQuery.textMuted,
  fontSize: 13,
  textAlign: "center",
  lineHeight: 1.5
});

export const StreamingHint = styled(Typography)({
  padding: "10px 16px 14px",
  fontSize: 12,
  fontStyle: "italic",
  color: paletteQuery.textMuted
});
