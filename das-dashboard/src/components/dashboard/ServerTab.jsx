import { styled } from "@mui/material/styles";
import { Box, Tab, Tabs, Typography } from "@mui/material";
import { Circle } from "@mui/icons-material";
import { useDashboardContext } from "../global_providers/DashboardContextProvider";
import { mockMachines } from "../../pages/dashboard/dashboard_mock_data";

const Container = styled(Box)({
  display: "flex",
  flexDirection: "column",
});

const Header = styled(Box)({
  padding: "10px 16px",
  backgroundColor: "#008cff",
  color: "white",
});

const Title = styled(Typography)({
  fontWeight: "bold",
});

const StyledTabs = styled(Tabs)({
  borderBottom: "1px solid #ddd",

  "& .MuiTabs-indicator": {
    backgroundColor: "#008cff",
  },
});

const StyledTab = styled(Tab)({
  textTransform: "none",
  fontWeight: 500,

  "&.Mui-selected": {
    color: "#008cff",
  },
});

const StatusIcon = styled(Circle)({
  width: "10px",
  height: "10px",
});



export function ServerTab() {
  const { currentMachine, setCurrentMachine } = useDashboardContext();

  const setStatusColor = (running) => (running ? "green" : "red");

  return (
    <Container>
      <Header>
        <Title>
          {currentMachine?.serverIp || "Select server"} - Metrics Overview
        </Title>
      </Header>

      <StyledTabs
        value={currentMachine?.serverIp || false}
        onChange={(e, newValue) => {
          const selectedMachine = mockMachines.find(
            (m) => m.serverIp === newValue
          );

          setCurrentMachine(selectedMachine);
        }}
      >
        {mockMachines.map((server) => (
          <StyledTab
            key={server.serverIp}
            value={server.serverIp}
            label={
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                }}
              >
                <StatusIcon
                  sx={{
                    color: setStatusColor(server.running),
                  }}
                />
                {server.serverIp}
              </Box>
            }
          />
        ))}
      </StyledTabs>
    </Container>
  );
}