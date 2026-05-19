import styled from "@emotion/styled";
import { Box, Typography } from "@mui/material";
import { useDashboardContext } from "../../../../components/global_providers/DashboardContextProvider";

const ServerInfoWrapper = styled(Box)({
  marginBottom: 24,
  paddingInline: 8,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  gap: 32,
  color: "#334155",
});

const ServerInfoBox = styled(Box)({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  textAlign: "center",
  minWidth: 120,
});

const Divider = styled(Box)({
  width: 1,
  height: 32,
  background: "#334155",
});

const Label = styled(Typography)({
  fontSize: 11,
  color: "#334155",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
});

const Value = styled(Typography)({
  fontWeight: 600,
  color: "#334155",
});

export function ServerInfoHeader() {
  const { machineStats } = useDashboardContext();

  if (!machineStats) {
    return null;
  }

  const cpuUsage = machineStats.CPUInfo?.cpuUsage ?? 0;
  const cpuCores = machineStats.CPUInfo?.cpuTotalCores ?? 0;
  const usedMem = machineStats.MemoryInfo?.usedMemory ?? 0;
  const totalMem = machineStats.MemoryInfo?.totalMemory ?? 0;
  
  const rawDisks = machineStats.DisksInfo ?? [];
  const uniqueDisks = Array.from(
    new Map(rawDisks.map((d) => [d.disk_device, d])).values()
  );

  return (
    <ServerInfoWrapper>
      <ServerInfoBox>
        <Label>CPU - {cpuCores} cores</Label>
        <Value>{cpuUsage}%</Value>
      </ServerInfoBox>

      <Divider />

      <ServerInfoBox>
        <Label>Memory Usage</Label>
        <Value>
          {usedMem}MB / {totalMem}MB
        </Value>
      </ServerInfoBox>

      {uniqueDisks.map((disk, index) => (
        <Box
          key={disk.disk_device || index}
          display="flex"
          alignItems="center"
          gap="32px"
        >
          <Divider />
          <ServerInfoBox>
            <Label>Disk {index + 1} ({disk.disk_device})</Label>
            <Value>
              {disk.disk_used_space}MB / {disk.disk_total_space}MB
            </Value>
          </ServerInfoBox>
        </Box>
      ))}
    </ServerInfoWrapper>
  );
}