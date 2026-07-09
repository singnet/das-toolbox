import { useState } from "react";
import { CircularProgress, Collapse } from "@mui/material";
import { ExpandMore, PlayArrow, Stop } from "@mui/icons-material";

import {
  ActionIcon,
  ActionRow,
  AgentCheckbox,
  AgentLabel,
  AgentOption,
  AgentPanel,
  ControlRoot,
  ExpandToggle,
  PrimaryAction,
} from "./architectureActionControl.styled";

const ARCHITECTURE_SERVICES = [
  { id: "attention-broker", label: "Attention Broker" },
  { id: "query-agent", label: "Query Agent" },
  { id: "link-creation-agent", label: "Link Creation Agent" },
  { id: "inference-agent", label: "Inference Agent" },
  { id: "evolution-agent", label: "Evolution Agent" },
  { id: "context-broker", label: "Context Broker" },
  { id: "atomdb-broker", label: "AtomDB Broker" },
];

export function ArchitectureActionControl({
  disabled = false,
  loading = false,
  architectureOnline = false,
  onPrimaryClick,
}) {
  const [expanded, setExpanded] = useState(false);
  const [selected, setSelected] = useState(() => ARCHITECTURE_SERVICES.map((service) => service.id));

  const toggle = (id) => {
    setSelected((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
    );
  };

  return (
    <ControlRoot data-expanded={expanded}>
      <ActionRow>
        <PrimaryAction
          disabled={disabled || loading || selected.length === 0}
          online={architectureOnline}
          onClick={() => onPrimaryClick?.(selected)}
        >
          <ActionIcon>
            {loading ? (
              <CircularProgress size={16} />
            ) : architectureOnline ? (
              <Stop />
            ) : (
              <PlayArrow />
            )}
          </ActionIcon>
          {architectureOnline ? "Stop Architecture" : "Start Architecture"}
        </PrimaryAction>

        <ExpandToggle
          disabled={disabled || loading}
          expanded={expanded}
          onClick={(event) => {
            event.stopPropagation();
            if (!disabled && !loading) {
              setExpanded((current) => !current);
            }
          }}
        >
          <ExpandMore fontSize="small" />
        </ExpandToggle>
      </ActionRow>

      <Collapse in={expanded}>
        <AgentPanel>
          {ARCHITECTURE_SERVICES.map((service) => (
            <AgentOption key={service.id}>
              <AgentCheckbox
                size="small"
                checked={selected.includes(service.id)}
                onChange={() => toggle(service.id)}
                disabled={disabled || loading}
              />
              <AgentLabel>{service.label}</AgentLabel>
            </AgentOption>
          ))}
        </AgentPanel>
      </Collapse>
    </ControlRoot>
  );
}
