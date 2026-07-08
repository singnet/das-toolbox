import { styled } from "@mui/material/styles";
import {
  Paper,
  TableCell,
  TableRow,
  Box,
  IconButton,
} from "@mui/material";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export const TableContainer = styled(Paper)({
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 12,
  overflow: "hidden",
  boxShadow: palette.shadow,
  backgroundColor: palette.surface
});

export const HeaderCell = styled(TableCell)({
  fontWeight: 600,
  fontSize: 13,
  backgroundColor: palette.surfaceMuted,
  color: palette.textSecondary,
  padding: "12px 16px",
  borderBottom: `1px solid ${palette.borderSubtle}`
});

export const BodyCell = styled(TableCell)({
  fontSize: 13,
  padding: "12px 16px",
  color: palette.textPrimary,
  borderBottom: `1px solid ${palette.borderSubtle}`
});

export const StyledRow = styled(TableRow)({
  cursor: "pointer",
  transition: "background-color 0.15s ease",

  "&:hover": {
    backgroundColor: palette.surfaceMuted,
  },

  "&:last-child td": {
    borderBottom: "none"
  }
});

export const ActionsBox = styled(Box)({
  display: "flex",
  gap: "8px",
  justifyContent: "flex-end",
});

export const ActionButton = styled(IconButton)({
  width: 34,
  height: 34,
  padding: 7,
  borderRadius: 4,
  border: `1px solid ${palette.border}`,
  backgroundColor: palette.surface,
  boxSizing: "border-box",

  "& .MuiSvgIcon-root": {
    fontSize: 18
  },

  "&.Mui-disabled": {
    opacity: 0.45
  }
});
