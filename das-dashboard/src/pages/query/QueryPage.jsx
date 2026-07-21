import { useState } from "react";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import ParameterSection from "../../components/query_page/ParameterSection";
import QueryAnswersPanel from "../../components/query_page/QueryAnswersPanel";
import QueryFrequencyHistogram from "../../components/query_page/QueryFrequencyHistogram";
import QueryImportanceChart from "../../components/query_page/QueryImportanceChart";
import QueryStatusBar from "../../components/query_page/QueryStatusBar";
import {
  QueryExecutionProvider,
  useQueryExecutionContext
} from "../../components/global_providers/QueryExecutionProvider";
import {
  PageContainer,
  ParamSideBar,
  QueryBreadcrumb,
  QueryCard,
  QueryContent,
  QueryContentBody,
  QueryContentHeader,
  QueryInput,
  QueryKindChip,
  QueryPageSubtitle,
  QueryPageTitle,
  QueryToolbar,
  QueryToolbarActions,
  ChartsRow,
  ResultsSection,
  RunButton,
  SideBarEyebrow,
  SideBarSubtitle,
  SideBarTitle,
  SideBarTitleHeader,
  StopButton,
  QueryStreamError
} from "./querypage.styled";

function QueryPageContent() {
  const [queryText, setQueryText] = useState(
    ''
  );

  const {
    answers,
    isRunning,
    executionId,
    answerCount,
    elapsedLabel,
    frequencyHistogram,
    stiChart,
    streamError,
    isCountOnly,
    startQuery,
    stopQuery
  } = useQueryExecutionContext();

  const canRun = queryText.trim().length > 0 && !isRunning;
  const canStop = isRunning && executionId != null;

  return (
    <PageContainer>
      <ParamSideBar>
        <SideBarTitleHeader>
          <SideBarEyebrow>Parameters</SideBarEyebrow>
          <SideBarTitle>Query inputs</SideBarTitle>
          <SideBarSubtitle>
            Configure the parameters for your MeTTa query.
          </SideBarSubtitle>
        </SideBarTitleHeader>

        <ParameterSection />
      </ParamSideBar>

      <QueryContent>
        <QueryContentHeader>
          <QueryBreadcrumb>
            Query <span>{'>'}</span> Workspace
          </QueryBreadcrumb>
          <QueryPageTitle>MeTTa query</QueryPageTitle>
          <QueryPageSubtitle>
            Compose and run a MeTTa query against the distributed AtomSpace.
          </QueryPageSubtitle>
        </QueryContentHeader>

        <QueryContentBody>
          <QueryCard>
            <QueryToolbar>
              <QueryKindChip>Query</QueryKindChip>
              <QueryToolbarActions>
                <RunButton
                  variant="contained"
                  disableElevation
                  startIcon={<PlayArrowIcon />}
                  disabled={!canRun}
                  onClick={() => startQuery(queryText)}
                >
                  Run
                </RunButton>
                <StopButton
                  variant="contained"
                  disableElevation
                  startIcon={<StopIcon />}
                  disabled={!canStop}
                  onClick={stopQuery}
                >
                  Stop
                </StopButton>
              </QueryToolbarActions>
            </QueryToolbar>

            <QueryInput
              multiline
              minRows={5}
              maxRows={12}
              fullWidth
              value={queryText}
              onChange={(event) => setQueryText(event.target.value)}
              placeholder="Enter a MeTTa expression…"
            />
          </QueryCard>

          <QueryStatusBar
            isRunning={isRunning}
            answerCount={answerCount}
            elapsedLabel={elapsedLabel}
            executionId={executionId}
            isCountOnly={isCountOnly}
          />

          {streamError ? (
            <QueryStreamError>{streamError}</QueryStreamError>
          ) : null}

          <ResultsSection>
            <QueryAnswersPanel
              answers={answers}
              executionId={executionId}
              isRunning={isRunning}
              isCountOnly={isCountOnly}
              totalAnswers={answerCount}
            />
            <ChartsRow>
              <QueryFrequencyHistogram histogram={frequencyHistogram} />
              <QueryImportanceChart chart={stiChart} />
            </ChartsRow>
          </ResultsSection>
        </QueryContentBody>
      </QueryContent>
    </PageContainer>
  );
}

export default function QueryPage() {
  return (
    <QueryExecutionProvider>
      <QueryPageContent />
    </QueryExecutionProvider>
  );
}
