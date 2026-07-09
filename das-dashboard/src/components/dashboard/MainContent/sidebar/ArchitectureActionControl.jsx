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
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { startArchitecture, stopArchitecture } from "../../../../api/ServicesAPI";
import { extractErrorDetails } from "../../../../api/APIUtils";

const ARCHITECTURE_SERVICES = [
  { id: "attention-broker", label: "Attention Broker" },
  { id: "query-agent", label: "Query Agent" },
  { id: "link-creation-agent", label: "Link Creation Agent" },
  { id: "inference-agent", label: "Inference Agent" },
  { id: "evolution-agent", label: "Evolution Agent" },
  { id: "context-broker", label: "Context Broker" },
  { id: "atomdb-broker", label: "AtomDB Broker" },
];

const LOADING_KEYS = ["start-architecture", "stop-architecture"];

export function ArchitectureActionControl({
  atomDbOnline,
  architectureOnline,
  isServerOffline,
  disabled = false,
  onBusyChange,
}) {
  const [expanded, setExpanded] = useState(false);
  const [selected, setSelected] = useState(() => ARCHITECTURE_SERVICES.map((service) => service.id));
  const [loadingAction, setLoadingAction] = useState(null);

  const { currentMachine } = useDashboardContext();
  const { showToast } = useToast();
  const { showConfirm } = useDialog();

  const currentHost = currentMachine?.serverIp;
  const isLoading = LOADING_KEYS.includes(loadingAction);
  const isActionDisabled = disabled || isLoading || isServerOffline || (!atomDbOnline && !architectureOnline);

  const setBusy = (actionKey) => {
    setLoadingAction(actionKey);
    onBusyChange?.(!!actionKey);
  };

  const executeAsyncAction = async (actionKey, action, successMessage, errorMessage) => {
    try {
      setBusy(actionKey);
      await action();
      showToast({ message: successMessage, severity: "success" });
    } catch (err) {
      console.error(errorMessage, err);
      showToast({ message: errorMessage, severity: "error", details: extractErrorDetails(err) });
    } finally {
      setBusy(null);
    }
  };

  const handleArchitectureAction = () => {
    if (!atomDbOnline) {
      showToast({ message: "AtomDB must be online before starting architecture.", severity: "warning" });
      return;
    }

    if (architectureOnline) {
      showConfirm({
        title: "Stop DAS Services",
        message: "Are you sure you want to stop all DAS services?\n\nEverything will be shut down except AtomDB.",
        onConfirm: () => executeAsyncAction(
          "stop-architecture",
          () => stopArchitecture(currentHost),
          "Architecture stopped successfully.",
          "Failed to stop architecture."
        )
      });
      return;
    }

    showConfirm({
      title: "Start Architecture",
      message: "Do you want to start the architecture?",
      onConfirm: () => executeAsyncAction(
        "start-architecture",
        () => startArchitecture(currentHost),
        "Architecture started successfully.",
        "Failed to start architecture."
      )
    });
  };

  const toggle = (id) => {
    setSelected((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
    );
  };

  return (
    <ControlRoot data-expanded={expanded}>
      <ActionRow>
        <PrimaryAction
          disabled={isActionDisabled || selected.length === 0}
          online={architectureOnline}
          onClick={() => !isActionDisabled && selected.length > 0 && handleArchitectureAction()}
        >
          <ActionIcon>
            {isLoading ? (
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
          disabled={isActionDisabled}
          expanded={expanded}
          onClick={(event) => {
            event.stopPropagation();
            if (!isActionDisabled) {
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
                disabled={isActionDisabled}
              />
              <AgentLabel>{service.label}</AgentLabel>
            </AgentOption>
          ))}
        </AgentPanel>
      </Collapse>
    </ControlRoot>
  );
}
