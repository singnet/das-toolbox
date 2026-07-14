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

const EMPTY_CHART = {
  values: [],
  labels: [],
  maxValue: 1,
  nonZeroCount: 0
};

export default function QueryImportanceChart({ chart = EMPTY_CHART }) {
  const hasData = chart.values.length > 0;

  return (
    <AnswerHistogramCard>
      <PanelHeader>
        <PanelTitle>Answer importance (STI)</PanelTitle>
        <PanelMeta>
          {hasData
            ? `${chart.nonZeroCount} non-zero · scale 0–1`
            : "Short-term importance per answer"}
        </PanelMeta>
      </PanelHeader>

      <HistogramBody>
        {hasData ? (
          <BarChart
            height={260}
            series={[
              {
                data: chart.values,
                label: "STI",
                color: paletteQuery.accent,
                id: "sti"
              }
            ]}
            xAxis={[
              {
                data: chart.labels,
                scaleType: "band",
                tickLabelStyle: {
                  fontSize: 10,
                  fill: paletteQuery.textSecondary,
                  angle: chart.labels.length > 6 ? -35 : 0,
                  textAnchor: chart.labels.length > 6 ? "end" : "middle"
                }
              }
            ]}
            yAxis={[
              {
                min: 0,
                max: chart.maxValue,
                label: "STI",
                tickLabelStyle: {
                  fontSize: 11,
                  fill: paletteQuery.textSecondary
                }
              }
            ]}
            margin={{
              left: 48,
              right: 16,
              top: 24,
              bottom: chart.labels.length > 6 ? 56 : 40
            }}
            slotProps={{ legend: { hidden: true } }}
            grid={{ horizontal: true }}
            borderRadius={3}
            skipAnimation
          />
        ) : (
          <EmptyPanelState>
            STI values from each answer will appear here once a query is run.
          </EmptyPanelState>
        )}
      </HistogramBody>
    </AnswerHistogramCard>
  );
}
