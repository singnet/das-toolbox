import { useState } from "react";
import { Box, Button, IconButton, Switch, Tooltip, Typography } from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import CloseIcon from "@mui/icons-material/Close";
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
import { useQueryParameters } from "../../hooks/useQueryParameters";
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
  const [publicKeyFile, setPublicKeyFile] = useState(null);

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
                  onClick={() => startQuery(queryText, publicKeyFile)}
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
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mt: 1.5, minWidth: 0 }}>
              <Button
                component="label"
                variant="outlined"
                size="small"
                startIcon={<VpnKeyIcon />}
                disabled={isRunning}
              >
                Choose public key
                <input
                  hidden
                  type="file"
                  accept=".pub,.key,text/plain"
                  onChange={(event) => {
                    setPublicKeyFile(event.target.files?.[0] ?? null);
                    event.target.value = "";
                  }}
                />
              </Button>
              {publicKeyFile ? (
                <>
                  <Typography
                    variant="body2"
                    noWrap
                    title={publicKeyFile.name}
                    sx={{ minWidth: 0 }}
                  >
                    {publicKeyFile.name}
                  </Typography>
                  <Tooltip title="Remove selected key">
                    <span>
                      <IconButton
                        size="small"
                        aria-label="Remove selected key"
                        disabled={isRunning}
                        onClick={() => setPublicKeyFile(null)}
                      >
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    </span>
                  </Tooltip>
                </>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Optional. The selected file is used for this query only.
                </Typography>
              )}
            </Box>
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
