import { styled } from "@mui/material/styles";
import {
  Paper,
  TableCell,
  TableRow,
  Box,
  IconButton,
} from "@mui/material";

export const TableContainer = styled(Paper)({
  border: "1px solid #ccc",
  borderRadius: "8px",
  overflow: "hidden",
});

export const HeaderCell = styled(TableCell)({
  fontWeight: "bold",
  fontSize: "14px",
  backgroundColor: "#f0f0f0",
  padding: "14px",
});

export const BodyCell = styled(TableCell)({
  fontSize: "14px",
  padding: "14px",
});

export const StyledRow = styled(TableRow)({
  cursor: "pointer",
  transition: "0.2s ease",

  "&:hover": {
    backgroundColor: "#f9f9f9",
  },
});

export const ActionsBox = styled(Box)({
  display: "flex",
  gap: "8px",
  justifyContent: "flex-end",
});

export const ActionButton = styled(IconButton)({
  padding: "6px",
});