import { useState } from "react";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import { Switch } from "@mui/material";
import ParameterSection from "../../components/query_page/ParameterSection";
import QueryAnswersPanel from "../../components/query_page/QueryAnswersPanel";
import QueryFrequencyHistogram from "../../components/query_page/QueryFrequencyHistogram";
import QueryImportanceChart from "../../components/query_page/QueryImportanceChart";
import QueryStatusBar from "../../components/query_page/QueryStatusBar";
import {
  QueryExecutionProvider,
  useQueryExecutionContext
} from "../../components/global_providers/QueryExecutionProvider";
import { ApiErrorNotice } from "../../components/common/ApiErrorNotice";
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
  QueryMettaSwitch,
  QueryPageSubtitle,
  QueryPageTitle,
  QueryToolbar,
  QueryToolbarActions,
  QueryToolbarLeading,
  paletteQuery,
  ChartsRow,
  ResultsSection,
  RunButton,
  SideBarEyebrow,
  SideBarSubtitle,
  SideBarTitle,
  SideBarTitleHeader,
  StopButton
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

  const { switches, updateSwitch } = useQueryParameters();

  const canRun = queryText.trim().length > 0 && !isRunning;
  const canStop = isRunning && executionId != null;

  return (
    <PageContainer>
      <ParamSideBar>
        <SideBarTitleHeader>
          <SideBarEyebrow>Parameters</SideBarEyebrow>
          <SideBarTitle>Query inputs</SideBarTitle>
          <SideBarSubtitle>
            Configure the parameters for your query.
          </SideBarSubtitle>
        </SideBarTitleHeader>

        <ParameterSection />
      </ParamSideBar>

      <QueryContent>
        <QueryContentHeader>
          <QueryPageTitle>Query</QueryPageTitle>
          <QueryPageSubtitle>
            Compose and run a query on the Distributed AtomSpace.
          </QueryPageSubtitle>
        </QueryContentHeader>

        <QueryContentBody>
          <QueryCard>
            <QueryToolbar>
              <QueryToolbarLeading>
                <QueryKindChip>Query</QueryKindChip>
                <QueryMettaSwitch
                  label="Use MeTTa query"
                  labelPlacement="end"
                  control={
                    <Switch
                      size="small"
                      checked={switches.use_metta_as_query_tokens}
                      onChange={(event) =>
                        updateSwitch("use_metta_as_query_tokens", event.target.checked)
                      }
                      sx={{
                        "& .MuiSwitch-switchBase.Mui-checked": {
                          color: paletteQuery.accent
                        },
                        "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
                          backgroundColor: paletteQuery.accent
                        }
                      }}
                    />
                  }
                />
              </QueryToolbarLeading>
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
              placeholder="Enter a query expression…"
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
            <ApiErrorNotice error={streamError} sx={{ borderRadius: 2 }} />
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
