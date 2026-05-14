import styled from "@emotion/styled";

const ServerInfoWrapper = styled(Box)({
  marginBottom: 24,
  paddingInline: 8,

  display: "flex",
  justifyContent: "center",
  alignItems: "center",

  gap: 32,
  color: "#334155",
});

const ServerInfoBox = styled(Box)({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  textAlign: "center",
  minWidth: 120,
});

const Divider = styled(Box)({
  width: 1,
  height: 32,
  background: "#334155",
});

const Label = styled(Typography)({
  fontSize: 11,
  color: "#334155",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
});

const Value = styled(Typography)({
  fontWeight: 600,
  color: "#334155",
});