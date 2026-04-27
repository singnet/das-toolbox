import { Box } from "@mui/material";
import { CPUViewChart } from "../../components/dashboard/CPUViewChart";
import { MainContent } from "../../components/dashboard/MainContent";
import { MemoryViewChart } from "../../components/dashboard/MemoryViewChart";
import { ServerTab } from "../../components/dashboard/ServerTab";
import { SideBar } from "../../components/dashboard/SideBar";
import "./Dashboard.css"
import ArchitectureView from "../../components/dashboard/ArchitectureView/ArchitectureViewCard";
import { useDashboardContext } from "../../components/global_providers/DashboardContextProvider";

export default function DashboardPage() {
  const { currentContext, setCurrentContext } = useDashboardContext()

  const renderContent = () => {

    switch (currentContext) {
      case "overview":
        return (
          <Box flex={1}>
            <ServerTab></ServerTab>
            <MainContent></MainContent>
          </Box>
        );
      case "architecture":
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