import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  cancelQueryExecution,
  startQueryExecution
} from "../api/QueryAPI";
import { extractApiError } from "../api/APIUtils";
import { createQueryExecutionStream } from "../api/QueryStreamService";
import { buildFrequencyHistogram, buildStiChart } from "../utils/queryCharts";
import { formatQueryAnswer } from "../utils/formatQueryAnswer";

const TERMINAL_STATUSES = new Set(["completed", "aborted", "error"]);

function formatElapsedLabel(elapsedMs) {
  const totalSeconds = Math.max(0, Math.floor(elapsedMs / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export function useQueryExecution(parameters) {
  const [answers, setAnswers] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [executionId, setExecutionId] = useState(null);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [streamError, setStreamError] = useState(null);
  const [answerCount, setAnswerCount] = useState(0);
  const [isCountOnly, setIsCountOnly] = useState(false);

  const streamRef = useRef(null);
  const startedAtRef = useRef(null);
  const answerSeqRef = useRef(0);
  const executionIdRef = useRef(null);
  const isCountOnlyRef = useRef(false);

  const closeStream = useCallback(() => {
    streamRef.current?.close();
    streamRef.current = null;
  }, []);

  const resetSession = useCallback(() => {
    closeStream();
    setStreamError(null);
    setAnswers([]);
    setAnswerCount(0);
    setElapsedMs(0);
    answerSeqRef.current = 0;
    executionIdRef.current = null;
    setExecutionId(null);
  }, [closeStream]);

  const preferMettaDisplay = Boolean(
    parameters.switches?.populate_metta_mapping ||
      parameters.switches?.use_metta_as_query_tokens
  );

  const appendAnswersFromChunk = useCallback(
    (chunkItems, receivedCount) => {
      if (typeof receivedCount === "number") {
        setAnswerCount(receivedCount);
      }

      if (!Array.isArray(chunkItems) || chunkItems.length === 0) {
        return;
      }

      const receivedAt = Date.now();
      const displayOptions = { preferMetta: preferMettaDisplay };
      const nextAnswers = chunkItems.map((item, index) => {
        answerSeqRef.current += 1;
        return {
          ...item,
          id: answerSeqRef.current,
          label: formatQueryAnswer(item, displayOptions),
          importance: Number(item.importance ?? 0),
          strength: Number(item.strength ?? 0),
          receivedAt: receivedAt + index
        };
      });

      setAnswers((previous) => [...previous, ...nextAnswers]);
    },
    [preferMettaDisplay]
  );

  const showCountResult = useCallback((count) => {
    answerSeqRef.current += 1;
    setAnswers([
      {
        id: answerSeqRef.current,
        count_only: true,
        count: Number(count),
        label: `Returned ${count} answers`,
        importance: 0,
        receivedAt: Date.now()
      }
    ]);
    setAnswerCount(Number(count));
  }, []);

  const finishExecution = useCallback((event) => {
    closeStream();
    startedAtRef.current = null;
    setIsRunning(false);

    if (event?.message) {
      setStreamError({
        message: event.message,
        details: event.details ?? null,
        severity: "error"
      });
    }

    if (typeof event?.received_count === "number" && !isCountOnlyRef.current) {
      setAnswerCount(event.received_count);
    }
  }, [closeStream]);

  const handleStreamEvent = useCallback(
    (event) => {
      if (event?.type === "chunk") {
        const countItem = event.data?.find((item) => item?.count_only);
        if (countItem) {
          showCountResult(countItem.count);
          return;
        }

        appendAnswersFromChunk(event.data, event.received_count);
        return;
      }

      if (event?.status === "running") {
        setIsRunning(true);
        return;
      }

      if (TERMINAL_STATUSES.has(event?.status)) {
        void finishExecution(event);
      }
    },
    [appendAnswersFromChunk, finishExecution, showCountResult]
  );

  const connectStream = useCallback(
    (nextExecutionId) => {
      closeStream();
      executionIdRef.current = nextExecutionId;

      streamRef.current = createQueryExecutionStream(nextExecutionId, {
        onEvent: handleStreamEvent,
        onError: () => {
          setStreamError({
            message: "Lost connection to the query stream.",
            details:
              "Check that the Command Router is still running in your architecture.",
            severity: "error"
          });
          setIsRunning(false);
        },
        onClose: () => {
          streamRef.current = null;
        }
      });
    },
    [closeStream, handleStreamEvent]
  );

  const startQuery = useCallback(
    async (queryText) => {
      const trimmedQuery = queryText.trim();
      if (!trimmedQuery) {
        return;
      }

      isCountOnlyRef.current = parameters.isCountOnly;
      setIsCountOnly(parameters.isCountOnly);
      resetSession();
      setIsRunning(true);
      startedAtRef.current = Date.now();

      try {
        const runParameters = parameters.collectParameters();
        const { execution_id: nextExecutionId } = await startQueryExecution(
          trimmedQuery,
          runParameters
        );
        if (!nextExecutionId) {
          throw new Error("Query execution did not return an execution id.");
        }

        executionIdRef.current = nextExecutionId;
        setExecutionId(nextExecutionId);
        connectStream(nextExecutionId);
      } catch (error) {
        startedAtRef.current = null;
        setIsRunning(false);
        setStreamError(extractApiError(error, "Failed to start query execution."));
      }
    },
    [connectStream, parameters, resetSession]
  );

  const stopQuery = useCallback(async () => {
    if (!executionIdRef.current) {
      setIsRunning(false);
      startedAtRef.current = null;
      return;
    }

    try {
      await cancelQueryExecution(executionIdRef.current);
      finishExecution(null);
    } catch (error) {
      setStreamError(extractApiError(error, "Failed to stop query execution."));
    }
  }, [finishExecution]);

  useEffect(() => {
    if (!isRunning || startedAtRef.current == null) {
      return undefined;
    }

    const tick = () => setElapsedMs(Date.now() - startedAtRef.current);
    tick();
    const intervalId = window.setInterval(tick, 1000);
    return () => window.clearInterval(intervalId);
  }, [isRunning]);

  useEffect(() => () => closeStream(), [closeStream]);

  const frequencyHistogram = useMemo(
    () => buildFrequencyHistogram(answers),
    [answers]
  );

  const stiChart = useMemo(() => buildStiChart(answers), [answers]);

  return {
    answers,
    isRunning,
    executionId,
    answerCount,
    elapsedLabel: formatElapsedLabel(elapsedMs),
    frequencyHistogram,
    stiChart,
    streamError,
    isCountOnly,
    startQuery,
    stopQuery
  };
}
