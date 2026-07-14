import { useState } from "react";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import ParameterSection from "../../components/query_page/ParameterSection";
import QueryAnswersPanel from "../../components/query_page/QueryAnswersPanel";
import QueryFrequencyHistogram from "../../components/query_page/QueryFrequencyHistogram";
import QueryImportanceChart from "../../components/query_page/QueryImportanceChart";
import QueryStatusBar from "../../components/query_page/QueryStatusBar";
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
  StopButton
} from "./querypage.styled";

const EMPTY_HISTOGRAM = {
  counts: Array(30).fill(0),
  labels: Array.from({ length: 30 }, (_, index) => String(index + 1)),
  scaleLabel: "1 minute",
  maxCount: 1
};

export default function QueryPage() {
  const [queryText, setQueryText] = useState(
    '(Evaluation (Predicate (public.cvterm "FBgn0034331")) (Concept "gene"))'
  );

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
                  disabled={!queryText.trim()}
                >
                  Run
                </RunButton>
                <StopButton
                  variant="contained"
                  disableElevation
                  startIcon={<StopIcon />}
                  disabled
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
            status="idle"
            answerCount={0}
            elapsedLabel="00:00"
            answersPerSecond={0}
          />

          <ResultsSection>
            <QueryAnswersPanel answers={[]} isRunning={false} />
            <ChartsRow>
              <QueryFrequencyHistogram histogram={EMPTY_HISTOGRAM} />
              <QueryImportanceChart />
            </ChartsRow>
          </ResultsSection>
        </QueryContentBody>
      </QueryContent>
    </PageContainer>
  );
}
