import { Box, Typography } from "@mui/material"
import { styled } from "@mui/material/styles"
import { palette } from "../../pages/setup_das/SetupDasStyled"

export const PreviewContainer = styled(Box)({
  maxHeight: "70vh",
  overflow: "auto",
  display: "flex",
  flexDirection: "column",
  gap: 16
})

export const PreviewSection = styled(Box)({
  backgroundColor: palette.surfaceMuted,
  border: `1px solid ${palette.border}`,
  borderRadius: 10,
  padding: "16px 18px"
})

export const PreviewSectionTitle = styled(Typography)({
  fontSize: 14,
  fontWeight: 600,
  color: palette.textPrimary,
  marginBottom: 12,
  letterSpacing: "-0.01em"
})

export const PreviewFieldGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "minmax(140px, 220px) 1fr",
  gap: "8px 16px",
  alignItems: "start"
})

export const PreviewFieldLabel = styled(Typography)({
  fontSize: 12,
  fontWeight: 500,
  color: palette.textMuted,
  lineHeight: 1.5
})

export const PreviewFieldValue = styled(Typography)({
  fontSize: 13,
  color: palette.textPrimary,
  lineHeight: 1.5,
  wordBreak: "break-word"
})

export const PreviewEmpty = styled(Typography)({
  fontSize: 13,
  color: palette.textSecondary,
  lineHeight: 1.6
})

export const PreviewNestedBlock = styled(Box)({
  marginTop: 12,
  padding: "12px 14px",
  borderRadius: 8,
  backgroundColor: palette.surface,
  border: `1px solid ${palette.borderSubtle}`
})

export const PreviewPeerBlock = styled(Box)({
  marginBottom: 10,
  padding: "12px 14px",
  borderRadius: 8,
  backgroundColor: palette.surface,
  border: `1px dashed ${palette.border}`,

  "&:last-child": {
    marginBottom: 0
  }
})
