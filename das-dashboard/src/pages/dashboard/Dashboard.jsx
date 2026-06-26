import { Box } from "@mui/material";

import ArchitectureView from "../../components/dashboard/ArchitectureView/ArchitectureView";
import { MainContent } from "../../components/dashboard/MainContent/MainContent";
import { ServerTab } from "../../components/dashboard/MainContent/servertab/ServerTab";
import { SideBar } from "../../components/dashboard/MainContent/sidebar/SideBar";

import { useDashboardContext } from "../../components/global_providers/DashboardContextProvider";

import "./Dashboard.css";

export default function DashboardPage() {
  const { currentContext } = useDashboardContext();

  const isAgentsView = currentContext === "agents";

  return (
    <Box
      sx={{
        display: "flex",
        height: "100%",
        width: "100%",
        overflow: "hidden",
      }}
    >
      <SideBar />

      <Box
        sx={{
          flex: 1,
          minHeight: 0,
          overflowY: "auto",
          backgroundColor: "#f5f5f5",
        }}
      >
        {isAgentsView ? (
          <ArchitectureView />
        ) : (
          <>
            <ServerTab />
            <MainContent />
          </>
        )}
      </Box>
    </Box>
  );
}