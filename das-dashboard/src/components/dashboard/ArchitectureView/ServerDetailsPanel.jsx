import { useState } from "react";
import {
  DialogContent,
  IconButton,
  Typography,
  Box,
  Chip,
  Tab,
} from "@mui/material";

import CloseIcon from "@mui/icons-material/Close";
import DnsIcon from "@mui/icons-material/Dns";

import {
  StyledDialog,
  StyledDialogTitle,
  StyledTabs,
  InfoCard,
  DarkCard,
  ClusterNodeCard,
} from "./serverdetailspanel.styled";

export function ServerDetailsDialog({
  machine,
  open,
  onClose,
}) {
  const [tab, setTab] = useState(0);

  if (!machine) return null;

  const statusColor = machine.running
    ? "#22c55e"
    : "#ef4444";

  return (
    <StyledDialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
    >
      <StyledDialogTitle>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
        >
          <Box display="flex" gap={2} alignItems="center">
            <DnsIcon sx={{ color: "#60a5fa" }} />

            <Box>
              <Typography fontWeight="bold" fontSize={18}>
                {machine.serverIp}
              </Typography>

              <Chip
                size="small"
                label={machine.running ? "Online" : "Offline"}
                sx={{
                  mt: 0.5,
                  background: `${statusColor}20`,
                  color: statusColor,
                }}
              />
            </Box>
          </Box>

          <IconButton
            onClick={onClose}
            sx={{ color: "#94a3b8" }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </StyledDialogTitle>

      <StyledTabs
        value={tab}
        onChange={(e, value) => setTab(value)}
      >
        <Tab label="Overview" />
        <Tab label="Services" />
        <Tab label="DB Clusters" />
      </StyledTabs>

      <DialogContent sx={{ p: 3 }}>
        {tab === 0 && (
          <Box display="grid" gap={2}>
            <InfoCard>
              <Typography variant="caption" color="#94a3b8">
                Server IP
              </Typography>
              <Typography fontWeight="bold">
                {machine.serverIp}
              </Typography>
            </InfoCard>

            <InfoCard>
              <Typography variant="caption" color="#94a3b8">
                Running Services
              </Typography>
              <Typography fontWeight="bold">
                {machine.agents.length}
              </Typography>
            </InfoCard>

            <InfoCard>
              <Typography variant="caption" color="#94a3b8">
                Status
              </Typography>
              <Typography fontWeight="bold">
                {machine.running ? "Online" : "Offline"}
              </Typography>
            </InfoCard>
          </Box>
        )}

        {tab === 1 && (
          <Box display="grid" gap={2}>
            {machine.agents.map((agent) => (
              <DarkCard key={agent.name}>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  mb={1}
                >
                  <Typography fontWeight="bold">
                    {agent.name}
                  </Typography>

                  <Chip
                    size="small"
                    label={agent.status}
                    color={
                      agent.status === "Running"
                        ? "success"
                        : "error"
                    }
                  />
                </Box>

                <Typography variant="body2">
                  Image: {agent.image}
                </Typography>

                <Typography variant="body2">
                  Port: {agent.port}
                </Typography>

                <Typography variant="body2">
                  CPU: {agent.cpu}
                </Typography>

                <Typography variant="body2">
                  RAM: {agent.memory}
                </Typography>

                <Typography variant="body2">
                  Age: {agent.age}
                </Typography>
              </DarkCard>
            ))}
          </Box>
        )}

        {tab === 2 && (
          <Box display="grid" gap={2}>
            {machine.agents
              .filter((a) => a.clusterNodes?.length > 0)
              .map((agent) => (
                <DarkCard key={agent.name}>
                  <Typography
                    fontWeight="bold"
                    mb={2}
                    color="#60a5fa"
                  >
                    {agent.name}
                  </Typography>

                  <Box
                    display="grid"
                    gridTemplateColumns="repeat(auto-fill, minmax(220px, 1fr))"
                    gap={2}
                  >
                    {agent.clusterNodes.map((node) => (
                      <ClusterNodeCard key={node.ip}>
                        <Typography fontWeight="bold">
                          {node.ip}
                        </Typography>

                        <Typography
                          variant="caption"
                          display="block"
                        >
                          Context: {node.context}
                        </Typography>

                        <Typography
                          variant="caption"
                          display="block"
                        >
                          User: {node.username}
                        </Typography>
                      </ClusterNodeCard>
                    ))}
                  </Box>
                </DarkCard>
              ))}
          </Box>
        )}
      </DialogContent>
    </StyledDialog>
  );
}