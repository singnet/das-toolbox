import { Box, Typography } from "@mui/material";

export function InlineInfo({
  label,
  value,
  valueColor,
}) {
  return (
    <Box
      display="flex"
      justifyContent="space-between"
    >
      <Typography variant="caption" color="#94a3b8">
        {label}
      </Typography>

      <Typography
        fontWeight="bold"
        fontSize={12}
        color={valueColor || "inherit"}
      >
        {value}
      </Typography>
    </Box>
  );
}