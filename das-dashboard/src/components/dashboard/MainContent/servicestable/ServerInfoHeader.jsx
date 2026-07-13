import styled from "@emotion/styled";
import { Box, Typography, Skeleton } from "@mui/material";
import { useServerTabMetricsContext } from "../../../../components/global_providers/ServerTabMetricsProvider";
import { ServerInfoWrapper, ServerInfoBox, Divider, Label, Value } from "./serverinfoheader.styled.js";

export function ServerInfoHeader() {
  const { hostMachineStats, hostStreamSwitching } = useServerTabMetricsContext();

  if (!hostMachineStats || hostStreamSwitching) {
    return (
      <ServerInfoWrapper>
        <ServerInfoBox>
          <Label><Skeleton variant="text" width={90} height={16} animation="wave" /></Label>
          <Value><Skeleton variant="text" width={50} height={28} animation="wave" /></Value>
        </ServerInfoBox>
        <Divider />
        
        <ServerInfoBox>
          <Label><Skeleton variant="text" width={95} height={16} animation="wave" /></Label>
          <Value><Skeleton variant="text" width={110} height={28} animation="wave" /></Value>
        </ServerInfoBox>
        <Divider />

        <ServerInfoBox>
          <Label><Skeleton variant="text" width={100} height={16} animation="wave" /></Label>
          <Value><Skeleton variant="text" width={110} height={28} animation="wave" /></Value>
        </ServerInfoBox>
      </ServerInfoWrapper>
    );
  }

  const cpuUsage = hostMachineStats.CPUInfo?.cpuUsage ?? 0;
  const cpuCores = hostMachineStats.CPUInfo?.cpuTotalCores ?? 0;
  const usedMem = hostMachineStats.MemoryInfo?.usedMemory ?? 0;
  const totalMem = hostMachineStats.MemoryInfo?.totalMemory ?? 0;
  
  const rawDisks = hostMachineStats.DisksInfo ?? [];
  const uniqueDisks = Array.from(
    new Map(rawDisks.map((d) => [d.disk_device, d])).values()
  );

  return (
    <ServerInfoWrapper>
      <ServerInfoBox>
        <Label>Machine Load - {cpuCores} cores</Label>
        <Value>{cpuUsage}%</Value>
      </ServerInfoBox>
      <Divider />
      
      <ServerInfoBox>
        <Label>Memory Usage</Label>
        <Value>
          {usedMem}GB / {totalMem}GB
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
            <Label>Disk (Root partition '/')</Label>
            <Value>
              {disk.disk_used_space}GB / {disk.disk_total_space}GB
            </Value>
          </ServerInfoBox>
        </Box>
      ))}
    </ServerInfoWrapper>
  );
}