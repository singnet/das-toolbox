import {
  EmptyPanelState,
  PanelHeader,
  PanelMeta,
  PanelTitle,
  QueryResultsCard,
  ResultAccent,
  ResultRow,
  ResultText,
  ResultsFooter,
  ResultsFooterLink,
  ResultsList,
  StreamingHint
} from "../../pages/query/querypage.styled";

const PREVIEW_LIMIT = 5;

export default function QueryAnswersPanel({
  answers,
  isRunning,
  previewLimit = PREVIEW_LIMIT
}) {
  const previewAnswers = answers.slice(-previewLimit);

  return (
    <QueryResultsCard>
      <PanelHeader>
        <PanelTitle>Results</PanelTitle>
        <PanelMeta>MeTTa expression</PanelMeta>
      </PanelHeader>

      {previewAnswers.length === 0 ? (
        <EmptyPanelState>
          {isRunning
            ? "Waiting for the first answer…"
            : "Run a query to stream answers here."}
        </EmptyPanelState>
      ) : (
        <>
          <ResultsList>
            {previewAnswers.map((answer) => (
              <ResultRow key={answer.id}>
                <ResultAccent />
                <ResultText>{answer.text}</ResultText>
              </ResultRow>
            ))}
          </ResultsList>

          {answers.length > previewLimit && (
            <ResultsFooter>
              <ResultsFooterLink>
                View all {answers.length} answers
              </ResultsFooterLink>
            </ResultsFooter>
          )}

          {isRunning && (
            <StreamingHint>Streaming more answers…</StreamingHint>
          )}
        </>
      )}
    </QueryResultsCard>
  );
}
