import { BarChart } from "@mui/x-charts/BarChart";
import {
  AnswerHistogramCard,
  EmptyPanelState,
  HistogramBody,
  PanelHeader,
  PanelMeta,
  PanelTitle,
  paletteQuery
} from "../../pages/query/querypage.styled";

const BUCKET_COUNT = 30;

export default function QueryFrequencyHistogram({ histogram }) {
  const hasData = histogram.counts.some((count) => count > 0);

  return (
    <AnswerHistogramCard>
      <PanelHeader>
        <PanelTitle>Answer frequency</PanelTitle>
        <PanelMeta>
          Answers in the last {histogram.scaleLabel}
        </PanelMeta>
      </PanelHeader>

      <HistogramBody>
        {hasData ? (
          <BarChart
            height={260}
            series={[
              {
                data: histogram.counts,
                label: "Answers",
                color: paletteQuery.accent,
                id: "answers"
              }
            ]}
            xAxis={[
              {
                data: histogram.labels,
                scaleType: "band",
                tickLabelStyle: { display: "none" }
              }
            ]}
            yAxis={[
              {
                min: 0,
                max: histogram.maxCount,
                tickMinStep: 1,
                label: "Answers",
                tickLabelStyle: {
                  fontSize: 11,
                  fill: paletteQuery.textSecondary
                }
              }
            ]}
            margin={{ left: 48, right: 16, top: 24, bottom: 36 }}
            slotProps={{ legend: { hidden: true } }}
            grid={{ horizontal: true }}
            borderRadius={3}
            skipAnimation
          />
        ) : (
          <EmptyPanelState>
            Frequency timeline fills as answers arrive within the current{" "}
            {histogram.scaleLabel} window.
          </EmptyPanelState>
        )}
      </HistogramBody>
    </AnswerHistogramCard>
  );
}
