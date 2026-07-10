import { useState } from "react";
import { CircularProgress, Collapse, Tooltip } from "@mui/material";
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
  GroupLabel,
  PrimaryAction,
} from "./architectureActionControl.styled";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { startArchitecture, stopArchitecture } from "../../../../api/ServicesAPI";
import { extractErrorDetails } from "../../../../api/APIUtils";

const CORE_SERVICES = [
  { id: "attention-broker", label: "Attention Broker" },
  { id: "query-agent", label: "Query Agent" },
];

const AGENT_SERVICES = [
  { id: "link-creation-agent", label: "Link Creation Agent" },
  { id: "evolution-agent", label: "Evolution Agent" },
  { id: "context-broker", label: "Context Broker" },
  { id: "inference-agent", label: "Inference Agent" },
  { id: "atomdb-broker", label: "AtomDB Broker" },
  { id: "command-router", label: "Command Router" },
];

const START_ORDER = [
  "attention-broker",
  "query-agent",
  "atomdb-broker",
  "command-router",
  "context-broker",
  "link-creation-agent",
  "evolution-agent",
  "inference-agent",
];

const AGENTS_LOCKED_TOOLTIP =
  "Start Attention Broker and Query Agent before managing other agents.";

function isServiceRunning(services, serviceId) {
  return services.some(
    (service) => service.service_key === serviceId && service.is_running
  );
}

export function ArchitectureActionControl({
  atomDbOnline,
  architectureOnline,
  mergedServices = [],
  isServerOffline,
  disabled = false,
  onBusyChange,
}) {
  const [expanded, setExpanded] = useState(false);
  const [selectedAgents, setSelectedAgents] = useState(() =>
    AGENT_SERVICES.map((service) => service.id)
  );
  const [loadingAction, setLoadingAction] = useState(null);

  const { showToast } = useToast();
  const { showConfirm } = useDialog();

  const isLoading = !!loadingAction;

  const coreOnline =
    isServiceRunning(mergedServices, "attention-broker") &&
    isServiceRunning(mergedServices, "query-agent");

  const agentsLocked = architectureOnline && !coreOnline;
  const agentsEnabled = !agentsLocked;

  const isActionDisabled =
    disabled || isLoading || isServerOffline || (!atomDbOnline && !architectureOnline);

  const setBusy = (actionKey) => {
    setLoadingAction(actionKey);
    onBusyChange?.(!!actionKey);
  };

  const runServices = async (serviceIds, action) => {
    const ordered =
      action === "start"
        ? START_ORDER.filter((id) => serviceIds.includes(id))
        : [...START_ORDER].reverse().filter((id) => serviceIds.includes(id));

    const fn = action === "start" ? startArchitecture : stopArchitecture;
    return fn(ordered);
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
      const toStop = [...selectedAgents, "query-agent", "attention-broker"];

      showConfirm({
        title: "Stop DAS Services",
        message: "Stop selected agents, then Query Agent and Attention Broker?",
        onConfirm: () =>
          executeAsyncAction(
            "stop-architecture",
            () => runServices(toStop, "stop"),
            "Architecture stopped successfully.",
            "Failed to stop architecture."
          ),
      });
      return;
    }

    const toStart = [...CORE_SERVICES.map((s) => s.id), ...selectedAgents];

    showConfirm({
      title: "Start Architecture",
      message: "Start core services first, then selected agents?",
      onConfirm: () =>
        executeAsyncAction(
          "start-architecture",
          () => runServices(toStart, "start"),
          "Architecture started successfully.",
          "Failed to start architecture."
        ),
    });
  };

  const toggleAgent = (id) => {
    setSelectedAgents((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
    );
  };

  const canSubmit =
    !isActionDisabled &&
    (architectureOnline || selectedAgents.length > 0 || CORE_SERVICES.length > 0);

  return (
    <ControlRoot data-expanded={expanded}>
      <ActionRow>
        <PrimaryAction
          disabled={!canSubmit}
          online={architectureOnline}
          onClick={() => canSubmit && handleArchitectureAction()}
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
          <GroupLabel>Core</GroupLabel>
          {CORE_SERVICES.map((service) => (
            <AgentOption key={service.id}>
              <AgentCheckbox size="small" checked disabled />
              <AgentLabel>{service.label}</AgentLabel>
            </AgentOption>
          ))}

          <Tooltip title={agentsLocked ? AGENTS_LOCKED_TOOLTIP : ""} placement="right">
            <span>
              <GroupLabel>Agents</GroupLabel>
              {AGENT_SERVICES.map((service) => (
                <AgentOption key={service.id}>
                  <AgentCheckbox
                    size="small"
                    checked={selectedAgents.includes(service.id)}
                    onChange={() => toggleAgent(service.id)}
                    disabled={isActionDisabled || !agentsEnabled}
                  />
                  <AgentLabel>{service.label}</AgentLabel>
                </AgentOption>
              ))}
            </span>
          </Tooltip>
        </AgentPanel>
      </Collapse>
    </ControlRoot>
  );
}
