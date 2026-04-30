import { Box, Typography, LinearProgress } from "@mui/material";

export function MetricBar({
  label,
  value,
  progress,
}) {
  return (
    <Box mb={1.5}>
      <Box
        display="flex"
        justifyContent="space-between"
        mb={0.5}
      >
        <Typography variant="caption" color="#94a3b8">
          {label}
        </Typography>

        <Typography fontWeight="bold" fontSize={12}>
          {value}
        </Typography>
      </Box>

      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          height: 6,
          borderRadius: 999,
          background: "#1e293b",
          "& .MuiLinearProgress-bar": {
            borderRadius: 999,
          },
        }}
      />
    </Box>
  );
}