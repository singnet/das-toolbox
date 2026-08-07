import { useEffect, useMemo, useRef, useState } from "react";
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
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { startArchitecture, stopArchitecture } from "../../../../api/ServicesAPI";
import { extractErrorDetails } from "../../../../api/APIUtils";

const CORE_TOOLTIP =
  "'Core' refers to necessary services to start/connect to other agents; disabling them can cause the architecture to be unusable or prone to failure.";

const AGENTS_TOOLTIP = "DAS Agents and services";

const CORE_SERVICE_KEYS = new Set(["attention-broker", "query-engine"]);

const ORCHESTRATION_SERVICE_KEYS = [
  "attention-broker",
  "query-engine",
  "atomdb-broker",
  "command-router",
  "context-broker",
  "link-creation-agent",
  "evolution-agent",
  "inference-agent",
];

function collectOrchestrationServices(machines = []) {
  const displayNames = new Map();

  for (const machine of machines) {
    for (const service of machine.services ?? []) {
      if (!ORCHESTRATION_SERVICE_KEYS.includes(service.service_key)) continue;
      if (!displayNames.has(service.service_key)) {
        displayNames.set(service.service_key, service.display_name);
      }
    }
  }

  return ORCHESTRATION_SERVICE_KEYS.filter((key) => displayNames.has(key)).map((key) => ({
    id: key,
    label: displayNames.get(key),
    group: CORE_SERVICE_KEYS.has(key) ? "core" : "agent",
  }));
}

export function ArchitectureActionControl({
  atomDbOnline,
  architectureOnline,
  isServerOffline,
  disabled = false,
  onBusyChange,
  onActionComplete,
}) {
  const { machines } = useDashboardContext();
  const orchestrationServices = useMemo(
    () => collectOrchestrationServices(machines),
    [machines]
  );

  const coreServices = useMemo(
    () => orchestrationServices.filter((service) => service.group === "core"),
    [orchestrationServices]
  );

  const agentServices = useMemo(
    () => orchestrationServices.filter((service) => service.group === "agent"),
    [orchestrationServices]
  );

  const [expanded, setExpanded] = useState(false);
  const [selectedServices, setSelectedServices] = useState([]);
  const [loadingAction, setLoadingAction] = useState(null);

  const { showToast } = useToast();
  const { showConfirm } = useDialog();
  const hasInitializedSelection = useRef(false);

  useEffect(() => {
    const availableIds = orchestrationServices.map((service) => service.id);
    setSelectedServices((current) => {
      if (!hasInitializedSelection.current) {
        hasInitializedSelection.current = true;
        return availableIds;
      }
      return current.filter((id) => availableIds.includes(id));
    });
  }, [orchestrationServices]);

  const isLoading = !!loadingAction;

  const isActionDisabled =
    disabled ||
    isLoading ||
    isServerOffline ||
    (!atomDbOnline && !architectureOnline) ||
    orchestrationServices.length === 0;

  const setBusy = (actionKey) => {
    setLoadingAction(actionKey);
    onBusyChange?.(!!actionKey);
  };

  const executeAsyncAction = async (actionKey, action, successMessage, errorMessage) => {
    try {
      setBusy(actionKey);
      await action();
      try {
        await onActionComplete?.();
      } catch (refreshError) {
        console.error("Failed to refresh sidebar status after action:", refreshError);
      }
      showToast({ message: successMessage, severity: "success" });
    } catch (err) {
      console.error(errorMessage, err);
      const serverMessage = err?.response?.data?.message;
      showToast({
        message: serverMessage || errorMessage,
        severity: "error",
        details: extractErrorDetails(err),
      });
    } finally {
      setBusy(null);
    }
  };

  const handleArchitectureAction = () => {
    if (architectureOnline) {
      if (!selectedServices.length) {
        showToast({ message: "Select at least one service to stop.", severity: "warning" });
        return;
      }

      showConfirm({
        title: "Stop DAS Services",
        message: `Stop ${selectedServices.length} selected service(s)?`,
        onConfirm: () =>
          executeAsyncAction(
            "stop-architecture",
            () => stopArchitecture(selectedServices),
            "Architecture stopped successfully.",
            "Failed to stop architecture."
          ),
      });
      return;
    }

    if (!atomDbOnline) {
      showToast({ message: "AtomDB must be online before starting architecture.", severity: "warning" });
      return;
    }

    if (!selectedServices.length) {
      showToast({ message: "Select at least one service to start.", severity: "warning" });
      return;
    }

    const serviceLabels = selectedServices
      .map((id) => orchestrationServices.find((service) => service.id === id)?.label)
      .filter(Boolean);

    showConfirm({
      title: "Start Architecture",
      message: `The following services will be started:\n\n${serviceLabels.map((label) => `• ${label}`).join("\n")}`,
      onConfirm: () =>
        executeAsyncAction(
          "start-architecture",
          () => startArchitecture(selectedServices),
          "Architecture started successfully.",
          "Failed to start architecture."
        ),
    });
  };

  const toggleService = (id) => {
    setSelectedServices((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
    );
  };

  const canSubmit = !isActionDisabled && selectedServices.length > 0;

  return (
    <ControlRoot data-expanded={expanded}>
      <ActionRow>
        <PrimaryAction
          type="button"
          disabled={!canSubmit}
          online={architectureOnline}
          onClick={handleArchitectureAction}
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
          type="button"
          disabled={isActionDisabled}
          expanded={expanded}
          aria-expanded={expanded}
          aria-label={expanded ? "Collapse agent selection" : "Expand agent selection"}
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
          <Tooltip title={CORE_TOOLTIP} placement="right">
            <GroupLabel component="span" sx={{ cursor: "help" }}>
              Core
            </GroupLabel>
          </Tooltip>
          {coreServices.map((service) => (
            <AgentOption key={service.id}>
              <AgentCheckbox
                size="small"
                checked={selectedServices.includes(service.id)}
                onChange={() => toggleService(service.id)}
                disabled={isActionDisabled}
              />
              <AgentLabel>{service.label}</AgentLabel>
            </AgentOption>
          ))}

          <Tooltip title={AGENTS_TOOLTIP} placement="right">
            <GroupLabel component="span" sx={{ cursor: "help" }}>
              Agents
            </GroupLabel>
          </Tooltip>
          {agentServices.map((service) => (
            <AgentOption key={service.id}>
              <AgentCheckbox
                size="small"
                checked={selectedServices.includes(service.id)}
                onChange={() => toggleService(service.id)}
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
