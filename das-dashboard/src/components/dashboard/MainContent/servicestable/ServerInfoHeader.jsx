import styled from "@emotion/styled";
import { Box, Typography } from "@mui/material";

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
    const totalCpu = 37;
    const totalMemory = 8120;

    const diskStats = [
        {currentFileSystem: "/", mockDiskUsed : 12400, mockDiskTotal : 25600},
        {currentFileSystem: "/mnt1", mockDiskUsed : 30000, mockDiskTotal : 128000},
        {currentFileSystem: "/mnt2", mockDiskUsed : 446200, mockDiskTotal : 700000}
    ]

    const currentFileSystem = "/";
    const mockDiskUsed = 12400;
    const mockDiskTotal = 25600;

    const mockTotalCores = 8;

    return (
        <ServerInfoWrapper>
        <ServerInfoBox>
            <Label>CPU - 8 cores</Label>
            <Value>{totalCpu}%</Value>
        </ServerInfoBox>

        <Divider />

        <ServerInfoBox>
            <Label>Memory Usage</Label>
            <Value>{totalMemory}MB / 32000MB</Value>
        </ServerInfoBox>

        <Divider />

        {diskStats.map((disk) => (
            <ServerInfoBox key={disk.currentFileSystem}>
                <Label>Disk ({disk.currentFileSystem})</Label>
                <Value>
                {disk.mockDiskUsed}MB / {disk.mockDiskTotal}MB
                </Value>
            </ServerInfoBox>
            ))
        }
        </ServerInfoWrapper>
    );
}   