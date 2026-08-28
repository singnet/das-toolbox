import { useMemo } from "react";

import { CPUViewChart } from "./CPUViewChart";
import { MemoryViewChart } from "./MemoryViewChart";
import { MetricsHistoryToolbar } from "./MetricsHistoryToolbar";
import { ChartPlaceholder } from "../LoadingSkeleton";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useServerTabMetricsContext } from "../../../global_providers/ServerTabMetricsProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { useServerTabHistory, REALTIME_PERIOD } from "../../../../hooks/useServerTabHistory";
import { extractApiError } from "../../../../api/APIUtils";
import { ChartGrid, ChartPanel, ChartSection } from "../servermetrics.styled";
import { serviceRowKey } from "../../../../utils/serviceRows";

function matchChartService(chartSource, selectedService) {
  if (!selectedService) {
    return null;
  }

  const candidates = [
    serviceRowKey(selectedService),
    selectedService.container_name,
    selectedService.service_name,
    selectedService.service_command_label,
  ].filter(Boolean);

  return candidates.find((name) =>
    chartSource?.agents?.some((agent) => agent.name === name)
  ) ?? null;
}

function pickChartAgents(chartSource, serviceName) {
  if (!serviceName) {
    return chartSource;
  }

  return {
    agents: (chartSource.agents ?? []).filter((agent) => agent.name === serviceName),
  };
}

export function ServerMetricsCharts() {
  const { currentMachine, currentService, metricsPeriod, setMetricsPeriod } =
    useDashboardContext();
  const { hostMachineStats, hostServices, hostMetricsRollup } = useServerTabMetricsContext();
  const { showToast } = useToast();
  const { showConfirm } = useDialog();

  const serverIp = currentMachine?.serverIp;
  const isRealtime = metricsPeriod === REALTIME_PERIOD;
  const {
    machineHistory,
    historyLoading,
    collecting,
    collectionBusy,
    toggleCollection,
    clearServerHistory,
    clearUnusedHistory,
    clearAllHistory,
  } = useServerTabHistory(serverIp, metricsPeriod);

  const selectedService = useMemo(
    () => hostServices?.find((service) => serviceRowKey(service) === currentService),
    [hostServices, currentService]
  );

  const liveHistory = hostMetricsRollup ?? { agents: [] };
  const storedHistory = machineHistory ?? { agents: [] };
  const chartSource = isRealtime ? liveHistory : storedHistory;
  const chartServiceName = matchChartService(chartSource, selectedService);
  const chartData =
    currentService && !chartServiceName
      ? { agents: [] }
      : pickChartAgents(chartSource, chartServiceName);
  const hasChartData = (chartData.agents ?? []).some(
    (agent) =>
      (agent.cpu ?? []).some((value) => value != null) ||
      (agent.memory ?? []).some((value) => value != null)
  );
  const emptyDescription = isRealtime
    ? "Waiting for live samples from the stream."
    : "No stored samples for this period yet.";

  const runAction = async (action, successMessage, fallbackMessage) => {
    try {
      await action();
      showToast({ message: successMessage, severity: "success" });
    } catch (error) {
      const { message, details, severity } = extractApiError(error, fallbackMessage);
      showToast({ message, severity, details });
    }
  };

  const handleToggleCollection = () =>
    runAction(
      toggleCollection,
      collecting ? "Metrics collection stopped." : "Metrics collection started.",
      "Failed to update metrics collection."
    );

  const handleClearServer = () => {
    showConfirm({
      title: "Clear server history",
      message: `Delete stored metrics for ${serverIp}?`,
      onConfirm: () =>
        runAction(clearServerHistory, "Server history cleared.", "Failed to clear server history."),
    });
  };

  const handleClearUnused = () => {
    showConfirm({
      title: "Clear unused history",
      message: "Delete metrics from servers that are no longer in the architecture?",
      onConfirm: () =>
        runAction(clearUnusedHistory, "Unused history cleared.", "Failed to clear unused history."),
    });
  };

  const handleClearAll = () => {
    showConfirm({
      title: "Clear all history",
      message: "Permanently delete metrics history for every server?",
      onConfirm: () =>
        runAction(clearAllHistory, "All metrics history cleared.", "Failed to clear all history."),
    });
  };

  return (
    <ChartSection>
      <MetricsHistoryToolbar
        period={metricsPeriod}
        onPeriodChange={setMetricsPeriod}
        collecting={collecting}
        collectionBusy={collectionBusy}
        historyLoading={historyLoading}
        onToggleCollection={handleToggleCollection}
        onClearServer={handleClearServer}
        onClearUnused={handleClearUnused}
        onClearAll={handleClearAll}
      />

      <ChartGrid>
        <ChartPanel>
          {hasChartData ? (
            <CPUViewChart
              key={`cpu-${serverIp}-${metricsPeriod}`}
              machine={chartData}
              currentService={chartServiceName}
            />
          ) : (
            <ChartPlaceholder title="CPU Usage History" description={emptyDescription} />
          )}
        </ChartPanel>

        <ChartPanel>
          {hasChartData ? (
            <MemoryViewChart
              key={`memory-${serverIp}-${metricsPeriod}`}
              machine={chartData}
              currentService={chartServiceName}
              stats={hostMachineStats}
            />
          ) : (
            <ChartPlaceholder title="Memory Usage History" description={emptyDescription} />
          )}
        </ChartPanel>
      </ChartGrid>
    </ChartSection>
  );
}
