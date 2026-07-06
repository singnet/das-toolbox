import { styled } from "@mui/material/styles"
import { Box, Typography } from "@mui/material"
import { palette } from "../setup_das/SetupDasStyled"

export { palette }

export const PageContainer = styled(Box)({
  display: "flex",
  width: "100%",
  height: "100%",
  maxWidth: "100%",
  overflow: "hidden",
  boxSizing: "border-box",
  backgroundColor: palette.background
})

export const ContentContainer = styled(Box)({
  flex: 1,
  minWidth: 0,
  minHeight: 0,
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
  backgroundColor: palette.background
})

export const ContentHeader = styled(Box)({
  flexShrink: 0,
  display: "flex",
  flexDirection: "column",
  gap: 0,
  borderBottom: `1px solid ${palette.borderSubtle}`,
  backgroundColor: palette.surface,
  boxSizing: "border-box"
})

export const ContentHeaderMain = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 16,
  padding: "14px 28px",
  minHeight: 56,
  boxSizing: "border-box"
})

export const ContentHeaderText = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: 2,
  minWidth: 0
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
  fontSize: 18,
  fontWeight: 600,
  color: palette.textPrimary,
  letterSpacing: "-0.02em"
})

export const ContentSubtitle = styled(Typography)({
  fontSize: 13,
  color: palette.textSecondary,
  fontWeight: 400
})

export const ContentBody = styled(Box)({
  flex: 1,
  minHeight: 0,
  minWidth: 0,
  overflowY: "auto",
  overflowX: "hidden",
  backgroundColor: palette.background,
  boxSizing: "border-box"
})

export const SoftAlert = styled(Box)({
  margin: "0 28px 14px",
  padding: "12px 16px",
  borderRadius: 10,
  backgroundColor: palette.accentLight,
  border: `1px solid ${palette.accentMuted}`,
  color: palette.textPrimary,
  fontSize: 13,
  lineHeight: 1.5
})
