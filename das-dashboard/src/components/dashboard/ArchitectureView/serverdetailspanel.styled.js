import { styled } from "@mui/material/styles";
import {
  Box,
  Dialog,
  DialogTitle,
  Tabs,
} from "@mui/material";

export const StyledDialog = styled(Dialog)({
  "& .MuiPaper-root": {
    background: "#0f172a",
    color: "#e2e8f0",
    borderRadius: 12,
    border: "1px solid #1e293b",
  },
});

export const StyledDialogTitle = styled(DialogTitle)({
  borderBottom: "1px solid #334155",
  paddingBottom: 16,
});

export const StyledTabs = styled(Tabs)({
  paddingLeft: 24,
  paddingRight: 24,
  borderBottom: "1px solid #334155",

  "& .MuiTab-root": {
    color: "#94a3b8",
  },

  "& .Mui-selected": {
    color: "#60a5fa",
  },

  "& .MuiTabs-indicator": {
    background: "#60a5fa",
  },
});

export const InfoCard = styled(Box)({
  padding: 16,
  borderRadius: 8,
  background: "#1e293b",
  border: "1px solid #334155",
});

export const DarkCard = styled(Box)({
  padding: 16,
  borderRadius: 8,
  background: "#1e293b",
  border: "1px solid #334155",
});

export const ClusterNodeCard = styled(Box)({
  padding: 16,
  borderRadius: 8,
  background: "#020617",
  border: "1px solid #334155",
});