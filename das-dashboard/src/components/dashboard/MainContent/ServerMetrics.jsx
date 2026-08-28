import ErrorIcon from "@mui/icons-material/Error";

import { ServerMetricsCharts } from "./charts/ServerMetricsCharts";
import { AgentTable } from "./servicestable/ServicesTable";
import { EmptyState } from "./LoadingSkeleton";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { useServerTabMetricsContext } from "../../global_providers/ServerTabMetricsProvider";
import { MainBoxGrid, TableBox } from "./servermetrics.styled";

export function ServerMetrics() {
  const { machines, currentMachine } = useDashboardContext();
  const { hostStreamError } = useServerTabMetricsContext();

  if (hostStreamError) {
    return (
      <MainBoxGrid>
        <EmptyState title={hostStreamError.title} description={hostStreamError.description} icon={ErrorIcon} />
      </MainBoxGrid>
    );
  }

  if (machines.length === 0) {
    return (
      <MainBoxGrid>
        <EmptyState />
      </MainBoxGrid>
    );
  }

  return (
    <MainBoxGrid>
      <ServerMetricsCharts />
      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}
