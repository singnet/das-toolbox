import { Box, Typography } from "@mui/material";

const stylesBySeverity = {
  error: {
    color: "#dc2626",
    border: "1px solid rgba(220, 38, 38, 0.25)",
    backgroundColor: "rgba(220, 38, 38, 0.06)"
  },
  warning: {
    color: "#b45309",
    border: "1px solid rgba(180, 83, 9, 0.25)",
    backgroundColor: "rgba(245, 158, 11, 0.08)"
  }
};

export function ApiErrorNotice({ error, sx }) {
  if (!error) {
    return null;
  }

  const normalized = typeof error === "string"
    ? { message: error, details: null, severity: "error" }
    : error;

  const { message, details, severity = "error" } = normalized;
  const palette = stylesBySeverity[severity] || stylesBySeverity.error;

  return (
    <Box
      sx={{
        fontSize: 13,
        lineHeight: 1.45,
        padding: "10px 14px",
        borderRadius: 1,
        ...palette,
        ...sx
      }}
    >
      <Typography component="p" sx={{ fontSize: "inherit", color: "inherit", m: 0 }}>
        {message}
      </Typography>
      {details ? (
        <Typography
          component="p"
          sx={{
            fontSize: "inherit",
            color: "inherit",
            opacity: 0.9,
            mt: 1,
            mb: 0,
            whiteSpace: "pre-wrap"
          }}
        >
          {details}
        </Typography>
      ) : null}
    </Box>
  );
}
