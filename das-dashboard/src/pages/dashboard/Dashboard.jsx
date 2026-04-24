import { Box } from "@mui/material";
import { CPUViewChart } from "../../components/dashboard/CPUViewChart";
import { MainContent } from "../../components/dashboard/MainContent";
import { MemoryViewChart } from "../../components/dashboard/MemoryViewChart";
import { ServerTab } from "../../components/dashboard/ServerTab";
import { SideBar } from "../../components/dashboard/SideBar";
import "./Dashboard.css"
import ArchitectureView from "../../components/dashboard/ArchitectureView";

export default function DashboardPage() {
  return (
    <Box style={{ display: "flex", height: "100vh", fontFamily: "sans-serif", backgroundColor:"#f5f5f5", gridTemplateColumns: "1fr 1fr"}}>
        <Box>
            <SideBar></SideBar>
        </Box>
        <Box flex={1}>
            <ServerTab></ServerTab>
            <MainContent></MainContent>
            <ArchitectureView></ArchitectureView>
        </Box>
    </Box>
  );
}