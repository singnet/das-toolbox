import { useEffect, useRef, useState } from "react";
import CloseIcon from "@mui/icons-material/Close";
import {
  Box,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Pagination,
  Typography
} from "@mui/material";
import { getQueryAnswers } from "../../api/QueryAPI";
import { extractApiError } from "../../api/APIUtils";
import { ApiErrorNotice } from "../common/ApiErrorNotice";
import { useQueryParameters } from "../../hooks/useQueryParameters";
import { formatQueryAnswer } from "../../utils/formatQueryAnswer";
import {
  AllAnswersList,
  AllAnswersModalPaper,
  ResultAccent,
  ResultRow,
  ResultText,
  paletteQuery
} from "../../pages/query/querypage.styled";

const PAGE_SIZE = 10;

function toPage(answers, page) {
  const total = answers.length;
  const start = (page - 1) * PAGE_SIZE;

  return {
    page,
    page_size: PAGE_SIZE,
    total,
    total_pages: total > 0 ? Math.ceil(total / PAGE_SIZE) : 0,
    items: answers.slice(start, start + PAGE_SIZE)
  };
}

export default function QueryAllAnswersModal({
  open,
  onClose,
  executionId,
  answers = []
}) {
  const [page, setPage] = useState(1);
  const [pageData, setPageData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { switches } = useQueryParameters();
  const displayOptions = {
    preferMetta: Boolean(
      switches.populate_metta_mapping || switches.use_metta_as_query_tokens
    )
  };

  const answersRef = useRef(answers);
  answersRef.current = answers;

  useEffect(() => {
    if (!open) {
      setPage(1);
      setPageData(null);
      setError(null);
      setIsLoading(false);
      return undefined;
    }

    if (!executionId) {
      return undefined;
    }

    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getQueryAnswers(executionId, page, PAGE_SIZE)
      .then((response) => {
        if (cancelled) {
          return;
        }

        setPageData(response.total > 0 ? response : toPage(answersRef.current, page));
      })
      .catch((loadError) => {
        if (cancelled) {
          return;
        }

        if (answersRef.current.length > 0) {
          setPageData(toPage(answersRef.current, page));
          return;
        }

        setError(extractApiError(loadError, "Failed to load answers."));
        setPageData(null);
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [open, executionId, page]);

  const total = pageData?.total ?? 0;
  const totalPages = pageData?.total_pages ?? 0;
  const items = pageData?.items ?? [];

  const pageLabel =
    total === 0
      ? "No answers yet"
      : `Showing ${(page - 1) * PAGE_SIZE + 1}-${Math.min(page * PAGE_SIZE, total)} of ${total}`;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="md"
      slotProps={{ paper: { sx: AllAnswersModalPaper } }}
    >
      <DialogTitle
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 2,
          pr: 1.5,
          fontSize: 16,
          fontWeight: 600,
          color: paletteQuery.textPrimary
        }}
      >
        All answers
        <IconButton aria-label="Close" onClick={onClose} size="small">
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ pt: 0 }}>
        <Typography sx={{ fontSize: 12, color: paletteQuery.textSecondary, mb: 2 }}>
          {pageLabel}
        </Typography>

        {isLoading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress size={24} />
          </Box>
        ) : error ? (
          <ApiErrorNotice error={error} sx={{ py: 2 }} />
        ) : items.length > 0 ? (
          <AllAnswersList>
            {items.map((answer) => (
              <ResultRow key={answer.id}>
                <ResultAccent />
                <ResultText>
                  {answer.label ?? formatQueryAnswer(answer, displayOptions)}
                </ResultText>
              </ResultRow>
            ))}
          </AllAnswersList>
        ) : (
          <Typography sx={{ fontSize: 13, color: paletteQuery.textMuted, py: 4 }}>
            No answers to display.
          </Typography>
        )}

        {totalPages > 1 ? (
          <Box sx={{ display: "flex", justifyContent: "center", pt: 2 }}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, nextPage) => setPage(nextPage)}
              size="small"
              color="primary"
            />
          </Box>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
