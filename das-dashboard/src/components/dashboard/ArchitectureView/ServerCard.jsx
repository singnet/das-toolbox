import {
  Box,
  Typography,
  Chip,
} from "@mui/material";

import StorageIcon from "@mui/icons-material/Storage";

import {
  StyledCard,
} from "./architectureview.styled";

import { InlineInfo } from "./InlineInfo";
import { MetricBar } from "./MetricBar";

import {
  getStatusColor,
  getHealthColor,
  parsePercent,
  parseMemory,
} from "./utils/utils";

export function ServerCard({
  service,
  selectedService,
  setSelectedService,
}) {
  return (
    <StyledCard
      onClick={() =>
        setSelectedService(service)
      }
      sx={{
        cursor: "pointer",
        border:
          selectedService?.name === service.name
            ? "1px solid #60a5fa"
            : undefined,
      }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="flex-start"
        gap={2}
        mb={2}
      >
        <Box
          display="flex"
          gap={1.5}
          alignItems="flex-start"
          flex={1}
          minWidth={0}
        >
          <StorageIcon
            sx={{
              color: "#60a5fa",
              mt: "2px",
              flexShrink: 0,
            }}
          />

          <Box flex={1} minWidth={0}>
            <Typography
              fontWeight="bold"
              fontSize={14}
            >
              {service.displayName}
            </Typography>

            <Typography
              variant="caption"
              display="block"
              color="#64748b"
            >
              Host: {service.hostServer}
            </Typography>

            <Typography
              variant="caption"
              display="block"
              color="#64748b"
              sx={{
                whiteSpace: "nowrap",
              }}
            >
              Container: {service.name}
            </Typography>
          </Box>
        </Box>

        <Chip
          size="small"
          label={service.status}
          sx={{
            flexShrink: 0,
            background: `${getStatusColor(
              service.status
            )}20`,
            color: getStatusColor(
              service.status
            ),
          }}
        />
      </Box>

      <MetricBar
        label="CPU"
        value={service.cpu}
        progress={parsePercent(service.cpu)}
      />

      <MetricBar
        label="Memory"
        value={service.memory}
        progress={parseMemory(service.memory)}
      />

      <Box display="grid" gap={0.75} mt={2}>
        <InlineInfo label="Port" value={service.port} />
        <InlineInfo label="Image" value={service.image} />
        <InlineInfo label="Uptime" value={service.age} />
        <InlineInfo
          label="Service Health"
          value={service.health}
          valueColor={getHealthColor(
            service.health
          )}
        />
      </Box>
    </StyledCard>
  );
}