import styled from "@emotion/styled";
import { Box } from "@mui/material";


export const PageContainer = styled(Box)({
  backgroundColor: "#f5f5f5",
  width: "100%",
  height: "100%",
  overflow: "auto",

  display: "flex",
  justifyContent: "center",
  alignItems: "center",

  padding: "24px",
  boxSizing: "border-box",
});