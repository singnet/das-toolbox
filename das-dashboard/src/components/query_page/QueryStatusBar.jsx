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
  status,
  answerCount,
  elapsedLabel,
  answersPerSecond,
  queryId
}) {
  return (
    <GeneralStatusBar>
      <StatusPill tone={status}>
        <StatusDot tone={status} />
        {status}
      </StatusPill>

      <StatusDivider />

      <StatusMetrics>
        <StatusMetric>
          <StatusMetricLabel>Answers</StatusMetricLabel>
          <StatusMetricValue>{answerCount}</StatusMetricValue>
        </StatusMetric>

        <StatusDivider />

        <StatusMetric>
          <StatusMetricLabel>Elapsed</StatusMetricLabel>
          <StatusMetricValue>{elapsedLabel}</StatusMetricValue>
        </StatusMetric>

        <StatusDivider />

        <StatusMetric>
          <StatusMetricLabel>Retrieved</StatusMetricLabel>
          <StatusMetricValue>{answerCount}</StatusMetricValue>
        </StatusMetric>

        <StatusDivider />

        <StatusMetric>
          <StatusMetricLabel>Rate</StatusMetricLabel>
          <StatusMetricValue>{answersPerSecond.toFixed(1)} ans/s</StatusMetricValue>
        </StatusMetric>

        {queryId != null && (
          <>
            <StatusDivider />
            <StatusMetric>
              <StatusMetricLabel>Query ID</StatusMetricLabel>
              <StatusMetricValue>#{queryId}</StatusMetricValue>
            </StatusMetric>
          </>
        )}
      </StatusMetrics>
    </GeneralStatusBar>
  );
}
