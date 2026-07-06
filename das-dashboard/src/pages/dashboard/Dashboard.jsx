import ArchitectureView from "../../components/dashboard/ArchitectureView/ArchitectureView";
import { MainContent } from "../../components/dashboard/MainContent/MainContent";
import { ServerTab } from "../../components/dashboard/MainContent/servertab/ServerTab";
import { SideBar } from "../../components/dashboard/MainContent/sidebar/SideBar";

import { useDashboardContext } from "../../components/global_providers/DashboardContextProvider";

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

export default function DashboardPage() {
  const { currentContext, machines, currentMachine, connectionError } = useDashboardContext();

  const isAgentsView = currentContext === "agents";
  const hasServers = machines && machines.length > 0;
  const viewLabel = isAgentsView ? "Agents" : "Servers";

  const pageTitle = connectionError
    ? "Connection failed"
    : !hasServers
      ? "No servers configured"
      : isAgentsView
        ? "Architecture overview"
        : `${currentMachine?.serverIp || "Select server"} · Metrics overview`;

  const pageSubtitle = connectionError
    ? connectionError.title
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
              {!connectionError && hasServers && (
                <ContentSubtitle>{pageSubtitle}</ContentSubtitle>
              )}
            </ContentHeaderText>
          </ContentHeaderMain>

          {connectionError && (
            <SoftAlert>
              {connectionError.description || connectionError.title}
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
