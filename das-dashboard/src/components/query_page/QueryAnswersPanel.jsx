import { useState } from "react";
import { Box } from "@mui/material";
import QueryAllAnswersModal from "./QueryAllAnswersModal";
import {
  EmptyPanelState,
  PanelHeader,
  PanelMeta,
  PanelTitle,
  QueryResultsCard,
  ResultAccent,
  ResultRow,
  ResultText,
  ResultsList,
  StreamingHint
} from "../../pages/query/querypage.styled";

const RESULT_LIMIT = 10;

export default function QueryAnswersPanel({
  answers,
  executionId,
  isRunning,
  isCountOnly = false,
  totalAnswers,
  resultLimit = RESULT_LIMIT
}) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const visibleAnswers = answers.slice(-resultLimit);
  const answerTotal = totalAnswers ?? answers.length;
  const canShowAll = Boolean(executionId) && answerTotal > 0;

  return (
    <>
      <QueryResultsCard>
        <PanelHeader>
          <PanelTitle>Results</PanelTitle>
          <Box sx={{ display: "flex", gap: "10px" }}>
            <PanelMeta>
              {answerTotal > 0
                ? `• Last ${Math.min(resultLimit, visibleAnswers.length)} of ${answerTotal}`
                : "MeTTa expression"}
            </PanelMeta>
            {canShowAll ? (
              <PanelMeta
                sx={{ textDecoration: "underline", cursor: "pointer" }}
                onClick={() => setIsModalOpen(true)}
              >
                Show all results
              </PanelMeta>
            ) : null}
          </Box>
        </PanelHeader>

        {visibleAnswers.length === 0 ? (
          <EmptyPanelState>
            {isRunning
              ? isCountOnly
                ? "Waiting for the count result…"
                : "Waiting for the first answer…"
              : isCountOnly
                ? "Run a count-only query to see the total here."
                : "Run a query to stream answers here."}
          </EmptyPanelState>
        ) : (
          <>
            <ResultsList>
              {visibleAnswers.map((answer) => (
                <ResultRow key={answer.id}>
                  <ResultAccent />
                  <ResultText>{answer.response}</ResultText>
                </ResultRow>
              ))}
            </ResultsList>

            {isRunning ? (
              <StreamingHint>Streaming more answers…</StreamingHint>
            ) : null}
          </>
        )}
      </QueryResultsCard>

      <QueryAllAnswersModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        executionId={executionId}
        answers={answers}
      />
    </>
  );
}
