import styled from "@emotion/styled";
import { Box } from "@mui/material";


export const PageContainer = styled(Box)({
  backgroundColor: "#f5f5f5",
  width: "100%",
  minHeight: "calc(100vh - 64px)",

  display: "flex",
  justifyContent: "center",
  alignItems: "center",

  padding: "24px",
  boxSizing: "border-box",
});