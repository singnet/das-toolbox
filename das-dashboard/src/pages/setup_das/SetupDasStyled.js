import { styled } from "@mui/material/styles"
import { Box, Button, Typography } from "@mui/material"

export const palette = {
  background: "#f4f4f6",
  surface: "#ffffff",
  surfaceMuted: "#f9fafb",
  sidebar: "#fafafa",
  border: "#e5e7eb",
  borderSubtle: "#f0f1f3",
  textPrimary: "#111827",
  textSecondary: "#6b7280",
  textMuted: "#9ca3af",
  accent: "#4f46e5",
  accentHover: "#4338ca",
  accentLight: "#eef2ff",
  accentMuted: "#e0e7ff",
  shadow: "0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 16px rgba(15, 23, 42, 0.04)"
}


export const PageContainer = styled(Box)({
  display: "flex",
  width: "100%",
  height: "100%",
  maxWidth: "100%",
  overflow: "hidden",
  boxSizing: "border-box",
  backgroundColor: palette.surface
})

export const SidebarContainer = styled(Box)({
  width: 240,
  minWidth: 240,
  flexShrink: 0,
  height: "100%",
  overflow: "hidden",
  backgroundColor: palette.sidebar,
  borderRight: `1px solid ${palette.border}`,
  display: "flex",
  flexDirection: "column"
})

export const SidebarHeader = styled(Box)({
  height: 64,
  padding: "0 20px",
  display: "flex",
  alignItems: "center",
  gap: 10,
  borderBottom: `1px solid ${palette.borderSubtle}`,
  color: palette.textPrimary,

  "& .MuiSvgIcon-root": {
    fontSize: 20,
    color: palette.accent
  }
})

export const SidebarTitle = styled(Typography)({
  fontSize: 15,
  fontWeight: 600,
  color: palette.textPrimary,
  letterSpacing: "-0.01em"
})

export const SidebarListContainer = styled(Box)({
  flex: 1,
  minHeight: 0,
  overflowY: "auto",
  overflowX: "hidden",
  padding: "12px 10px",

  "& .MuiListItemButton-root": {
    minHeight: 36,
    padding: "6px 12px",
    marginBottom: 2,
    borderRadius: 8,
    color: palette.textSecondary,
    fontSize: 13,
    fontWeight: 500,
    transition: "background-color 0.15s ease, color 0.15s ease",

    "&:hover": {
      backgroundColor: palette.surfaceMuted,
      color: palette.textPrimary
    }
  },

  "& .MuiListItemText-primary": {
    fontSize: 13,
    fontWeight: 500
  },

  "& .Mui-selected": {
    backgroundColor: `${palette.accentLight} !important`,
    color: `${palette.accent} !important`,

    "& .MuiListItemText-primary": {
      fontWeight: 600,
      color: palette.accent
    },

    "& .MuiSvgIcon-root": {
      color: palette.accent
    }
  }
})

export const SectionLabel = styled(Typography)({
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.06em",
  textTransform: "uppercase",
  color: palette.textMuted,
  padding: "8px 12px 6px"
})

export const SidebarButtons = styled(Box)({
  flexShrink: 0,
  padding: "14px 12px",
  borderTop: `1px solid ${palette.borderSubtle}`,
  display: "grid",
  gridTemplateColumns: "repeat(2, 1fr)",
  gap: 8,
  boxSizing: "border-box"
})

export const CompactActionButton = styled(Button)({
  textTransform: "none",
  fontWeight: 500,
  fontSize: 11,
  borderRadius: 10,
  minHeight: 52,
  padding: "8px 6px",
  flexDirection: "column",
  gap: 4,
  lineHeight: 1.2,
  color: palette.textSecondary,
  backgroundColor: palette.surface,
  border: `1px solid ${palette.border}`,
  boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",

  "& .MuiSvgIcon-root": {
    fontSize: 18,
    color: palette.accent
  },

  "&:hover": {
    backgroundColor: palette.accentLight,
    borderColor: palette.accentMuted,
    color: palette.accent
  }
})

export const CompactActionButtonPrimary = styled(CompactActionButton)({
  backgroundColor: palette.accent,
  borderColor: palette.accent,
  color: "#ffffff",

  "& .MuiSvgIcon-root": {
    color: "#ffffff"
  },

  "&:hover": {
    backgroundColor: palette.accentHover,
    borderColor: palette.accentHover,
    color: "#ffffff"
  }
})

export const ContentContainer = styled(Box)({
  flex: 1,
  minWidth: 0,
  minHeight: 0,
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
  backgroundColor: palette.surface
})

export const ContentHeader = styled(Box)({
  flexShrink: 0,
  height: 64,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  paddingLeft: 28,
  paddingRight: 28,
  borderBottom: `1px solid ${palette.borderSubtle}`,
  backgroundColor: palette.surface,
  gap: 2,
  boxSizing: "border-box"
})

export const Breadcrumb = styled(Typography)({
  fontSize: 12,
  color: palette.textMuted,
  fontWeight: 500,

  "& span": {
    color: palette.textSecondary
  }
})

export const ContentTitle = styled(Typography)({
  fontSize: 20,
  fontWeight: 600,
  color: palette.textPrimary,
  letterSpacing: "-0.02em"
})

export const ContentBody = styled(Box, {
  shouldForwardProp: (prop) => prop !== "flush"
})(({ flush }) => ({
  flex: 1,
  minHeight: 0,
  minWidth: 0,
  overflowY: flush ? "hidden" : "auto",
  overflowX: "hidden",
  padding: flush ? 0 : "24px 28px",
  backgroundColor: palette.surface,
  boxSizing: "border-box"
}))

export const DialogButton = styled(Button, {
  shouldForwardProp: (prop) => prop !== "variant"
})(({ variant = "primary" }) => ({
  textTransform: "none",
  fontWeight: 500,
  fontSize: 13,
  borderRadius: 8,
  minWidth: 72,
  height: 34,
  padding: "0 14px",
  boxShadow: "none",

  ...(variant === "primary" && {
    color: "#ffffff",
    backgroundColor: palette.accent,

    "&:hover": {
      backgroundColor: palette.accentHover,
      boxShadow: "none"
    }
  }),

  ...(variant === "secondary" && {
    color: palette.textSecondary,
    backgroundColor: palette.surfaceMuted,
    border: `1px solid ${palette.border}`,

    "&:hover": {
      backgroundColor: palette.borderSubtle,
      boxShadow: "none"
    }
  })
}))

export const DialogPaper = {
  borderRadius: 3,
  boxShadow: "0 8px 32px rgba(15, 23, 42, 0.12)",
  border: `1px solid ${palette.borderSubtle}`
}
