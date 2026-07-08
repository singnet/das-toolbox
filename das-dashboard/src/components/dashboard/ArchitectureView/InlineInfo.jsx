import { Box, Typography } from "@mui/material";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

export function InlineInfo({
  label,
  value,
  valueColor,
}) {
  return (
    <Box display="flex" justifyContent="space-between" gap={2}>
      <Typography variant="caption" sx={{ color: palette.textMuted }}>
        {label}
      </Typography>

      <Typography
        fontWeight={600}
        fontSize={12}
        sx={{ color: valueColor || palette.textPrimary, textAlign: "right" }}
      >
        {value}
      </Typography>
    </Box>
  );
}
