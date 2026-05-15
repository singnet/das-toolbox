import { Box } from "@mui/material";
import { ServerTab } from "../../components/dashboard/MainContent/servertab/ServerTab";
import { SideBar } from "../../components/dashboard/MainContent/sidebar/SideBar";
import { MainContent } from "../../components/dashboard/MainContent/MainContent";
import ArchitectureView from "../../components/dashboard/ArchitectureView/ArchitectureView";
import { useDashboardContext } from "../../components/global_providers/DashboardContextProvider";
import "./Dashboard.css"

export default function DashboardPage() {
  const { currentContext } = useDashboardContext();

  const renderContent = () => {
    return (
      <Box sx={{ flex: 1, height: "100vh", overflowY: "auto", backgroundColor: "#f5f5f5" }}>
        {currentContext === "agents" ? (
          <ArchitectureView />
        ) : (
          <>
            <ServerTab />
            <MainContent />
          </>
        )}
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", height: "100vh", width: "100vw", overflow: "hidden" }}>
      <Box>
        <SideBar />
      </Box>
      {renderContent()}
    </Box>
  );
}