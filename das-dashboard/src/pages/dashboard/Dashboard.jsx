import { Box } from "@mui/material";
import { CPUViewChart } from "../../components/dashboard/MainContent/CPUViewChart";
import { MainContent } from "../../components/dashboard/MainContent/MainContent";
import { MemoryViewChart } from "../../components/dashboard/MainContent/MemoryViewChart";
import { ServerTab } from "../../components/dashboard/MainContent/servertab/ServerTab";
import { SideBar } from "../../components/dashboard/MainContent/SideBar";
import ArchitectureView from "../../components/dashboard/ArchitectureView/ArchitectureView";

import { useDashboardContext } from "../../components/global_providers/DashboardContextProvider";

import "./Dashboard.css"

export default function DashboardPage() {
  const { currentContext, setCurrentContext } = useDashboardContext()

  const renderContent = () => {

    switch (currentContext) {
      case "servers":
        return (
          <Box flex={1}>
            <ServerTab></ServerTab>
            <MainContent></MainContent>
          </Box>
        );
      case "agents":
        return (
          <Box flex={1}>
            <ArchitectureView></ArchitectureView>
          </Box>
        );
      default:
        return (
          <Box flex={1}>
            <ServerTab></ServerTab>
            <MainContent></MainContent>
          </Box>
        );
    }

  }

  return (
    <Box style={{ display: "flex", height: "100vh", fontFamily: "sans-serif", backgroundColor:"#f5f5f5", gridTemplateColumns: "1fr 1fr"}}>
        <Box>
            <SideBar></SideBar>
        </Box>

        {renderContent()}
    </Box>
  );
}