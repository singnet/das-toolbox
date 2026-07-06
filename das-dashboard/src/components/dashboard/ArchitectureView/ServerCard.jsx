import {
  Box,
  Typography,
  Chip,
} from "@mui/material";

import StorageIcon from "@mui/icons-material/Storage";

import { StyledCard } from "./architectureview.styled";
import { InlineInfo } from "./InlineInfo";
import { MetricBar } from "./MetricBar";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

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
  const isSelected = selectedService?.name === service.name;

  return (
    <StyledCard
      selected={isSelected}
      onClick={() => setSelectedService(service)}
      sx={{ cursor: "pointer" }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="flex-start"
        gap={2}
        mb={2}
      >
        <Box display="flex" gap={1.5} alignItems="flex-start" flex={1} minWidth={0}>
          <StorageIcon sx={{ color: palette.accent, mt: "2px", flexShrink: 0 }} />

          <Box flex={1} minWidth={0}>
            <Typography fontWeight={600} fontSize={14} noWrap>
              {service.displayName}
            </Typography>

            <Typography
              variant="caption"
              display="block"
              sx={{
                color: palette.textMuted,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis"
              }}
            >
              ID: {service.name}
            </Typography>
          </Box>
        </Box>

        <Chip
          size="small"
          label={service.status}
          sx={{
            flexShrink: 0,
            fontWeight: 600,
            background: `${getStatusColor(service.status)}20`,
            color: getStatusColor(service.status),
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
          label="Health"
          value={service.health}
          valueColor={getHealthColor(service.health)}
        />
      </Box>
    </StyledCard>
  );
}
