import {
  GeneralStatusBar,
  StatusDivider,
  StatusDot,
  StatusMetric,
  StatusMetricLabel,
  StatusMetricValue,
  StatusMetrics,
  StatusPill
} from "../../pages/query/querypage.styled";

export default function QueryStatusBar({
  isRunning,
  answerCount,
  elapsedLabel,
  executionId,
  isCountOnly = false
}) {
  return (
    <GeneralStatusBar>
      <StatusPill tone={isRunning ? "running" : "idle"}>
        <StatusDot tone={isRunning ? "running" : "idle"} />
        {isRunning ? "Running" : "Running"}
      </StatusPill>

      <StatusDivider />

      <StatusMetrics>
        <StatusMetric>
          <StatusMetricLabel>{isCountOnly ? "Count" : "Answers"}</StatusMetricLabel>
          <StatusMetricValue>{answerCount}</StatusMetricValue>
        </StatusMetric>

        <StatusDivider />

        <StatusMetric>
          <StatusMetricLabel>Elapsed</StatusMetricLabel>
          <StatusMetricValue>{elapsedLabel}</StatusMetricValue>
        </StatusMetric>

        <StatusDivider />

        <StatusMetric>
          <StatusMetricLabel>{isCountOnly ? "Total" : "Retrieved"}</StatusMetricLabel>
          <StatusMetricValue>{answerCount}</StatusMetricValue>
        </StatusMetric>

        {executionId != null && (
          <>
            <StatusDivider />
            <StatusMetric>
              <StatusMetricLabel>Query ID</StatusMetricLabel>
              <StatusMetricValue>#{executionId.slice(0, 8)}</StatusMetricValue>
            </StatusMetric>
          </>
        )}
      </StatusMetrics>
    </GeneralStatusBar>
  );
}
