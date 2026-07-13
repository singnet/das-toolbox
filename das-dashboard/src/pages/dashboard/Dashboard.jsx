import ArchitectureView from "../../components/dashboard/ArchitectureView/ArchitectureView";
import { MainContent } from "../../components/dashboard/MainContent/MainContent";
import { ServerTab } from "../../components/dashboard/MainContent/servertab/ServerTab";
import { SideBar } from "../../components/dashboard/MainContent/sidebar/SideBar";
import { ServerTabMetricsProvider } from "../../components/global_providers/ServerTabMetricsProvider";
import { ArchitectureTabMetricsProvider } from "../../components/global_providers/ArchitectureTabMetricsProvider";
import { useDashboardContext } from "../../components/global_providers/DashboardContextProvider";
import { useServerTabMetricsContext } from "../../components/global_providers/ServerTabMetricsProvider";

import {
  PageContainer,
  ContentContainer,
  ContentHeader,
  ContentHeaderMain,
  ContentHeaderText,
  Breadcrumb,
  ContentTitle,
  ContentSubtitle,
  ContentBody,
  SoftAlert
} from "./Dashboard.styled";

function DashboardPageContent() {
  const { currentContext, machines, currentMachine } = useDashboardContext();
  const { hostStreamError } = useServerTabMetricsContext();

  const isAgentsView = currentContext === "agents";
  const hasServers = machines && machines.length > 0;
  const viewLabel = isAgentsView ? "Agents" : "Servers";
  const showServerStreamError = !isAgentsView && hostStreamError;

  const pageTitle = showServerStreamError
    ? "Connection failed"
    : !hasServers
      ? "No servers configured"
      : isAgentsView
        ? "Architecture overview"
        : `${currentMachine?.serverIp || "Select server"} · Metrics overview`;

  const pageSubtitle = showServerStreamError
    ? hostStreamError.title
    : !hasServers
      ? "Save your configuration on the Configuration page first."
      : isAgentsView
        ? "Monitor agents, brokers, loaders, and AtomDB services."
        : "Live CPU, memory, and agent status for the selected server.";

  return (
    <PageContainer>
      <SideBar />

      <ContentContainer>
        <ContentHeader>
          <ContentHeaderMain>
            <ContentHeaderText>
              <Breadcrumb>
                Dashboard <span>›</span> {viewLabel}
              </Breadcrumb>
              <ContentTitle>{pageTitle}</ContentTitle>
              {!showServerStreamError && (hasServers || isAgentsView) && (
                <ContentSubtitle>{pageSubtitle}</ContentSubtitle>
              )}
            </ContentHeaderText>
          </ContentHeaderMain>

          {showServerStreamError && (
            <SoftAlert>
              {hostStreamError.description || hostStreamError.title}
            </SoftAlert>
          )}

          {hasServers && !isAgentsView && <ServerTab />}
        </ContentHeader>

        <ContentBody>
          {isAgentsView ? <ArchitectureView /> : <MainContent />}
        </ContentBody>
      </ContentContainer>
    </PageContainer>
  );
}

export default function DashboardPage() {
  return (
    <ServerTabMetricsProvider>
      <ArchitectureTabMetricsProvider>
        <DashboardPageContent />
      </ArchitectureTabMetricsProvider>
    </ServerTabMetricsProvider>
  );
}
