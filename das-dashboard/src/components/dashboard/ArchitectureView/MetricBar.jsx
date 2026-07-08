import { Box, Typography, LinearProgress } from "@mui/material";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

export function MetricBar({
  label,
  value,
  progress,
}) {
  return (
    <Box mb={1.5}>
      <Box display="flex" justifyContent="space-between" mb={0.5}>
        <Typography variant="caption" sx={{ color: palette.textMuted }}>
          {label}
        </Typography>

        <Typography fontWeight={600} fontSize={12} sx={{ color: palette.textPrimary }}>
          {value}
        </Typography>
      </Box>

      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          height: 6,
          borderRadius: 999,
          backgroundColor: palette.borderSubtle,
          "& .MuiLinearProgress-bar": {
            borderRadius: 999,
            backgroundColor: palette.accent
          },
        }}
      />
    </Box>
  );
}
