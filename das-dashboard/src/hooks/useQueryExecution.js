import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  cancelQueryExecution,
  getQueryExecutionStatus,
  setQueryParameters,
  startQueryExecution
} from "../api/QueryAPI";
import { extractErrorDetails } from "../api/APIUtils";
import { createQueryExecutionStream } from "../api/QueryStreamService";
import { buildFrequencyHistogram, buildStiChart } from "../utils/queryCharts";

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

  const appendAnswersFromChunk = useCallback((chunkItems, receivedCount) => {
    if (typeof receivedCount === "number") {
      setAnswerCount(receivedCount);
    }

    if (!Array.isArray(chunkItems) || chunkItems.length === 0) {
      return;
    }

    const receivedAt = Date.now();
    const nextAnswers = chunkItems.map((item, index) => {
      answerSeqRef.current += 1;
      return {
        id: answerSeqRef.current,
        response: item.response ?? "",
        importance: Number(item.importance ?? 0),
        receivedAt: receivedAt + index
      };
    });

    setAnswers((previous) => [...previous, ...nextAnswers]);
  }, []);

  const showCountResult = useCallback((count) => {
    answerSeqRef.current += 1;
    setAnswers([
      {
        id: answerSeqRef.current,
        response: `Returned ${count} answers`,
        importance: 0,
        receivedAt: Date.now()
      }
    ]);
    setAnswerCount(Number(count));
  }, []);

  const finishExecution = useCallback(async (event) => {
    closeStream();
    startedAtRef.current = null;
    setIsRunning(false);

    if (event?.message) {
      setStreamError(event.message);
    }

    const isCountOnlyQuery =
      isCountOnlyRef.current &&
      event?.status === "completed" &&
      executionIdRef.current;

    if (isCountOnlyQuery) {
      try {
        const status = await getQueryExecutionStatus(executionIdRef.current);
        const count = status.total_items ?? status.received_count;
        if (typeof count === "number") {
          showCountResult(count);
        }
      } catch (error) {
        setStreamError(extractErrorDetails(error));
      }
      return;
    }

    if (typeof event?.received_count === "number") {
      setAnswerCount(event.received_count);
    }
  }, [closeStream, showCountResult]);

  const handleStreamEvent = useCallback(
    (event) => {
      if (event?.type === "chunk" && !isCountOnlyRef.current) {
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
    [appendAnswersFromChunk, finishExecution]
  );

  const connectStream = useCallback(
    (nextExecutionId) => {
      closeStream();
      executionIdRef.current = nextExecutionId;

      streamRef.current = createQueryExecutionStream(nextExecutionId, {
        onEvent: handleStreamEvent,
        onError: (error) => {
          setStreamError(error.message);
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
        const pendingParams = parameters.consumeQueryRunParameters();
        if (Object.keys(pendingParams).length > 0) {
          await setQueryParameters(pendingParams);
        }

        const { execution_id: nextExecutionId } = await startQueryExecution(trimmedQuery);
        if (!nextExecutionId) {
          throw new Error("Query execution did not return an execution id.");
        }

        setExecutionId(nextExecutionId);
        connectStream(nextExecutionId);
      } catch (error) {
        startedAtRef.current = null;
        setIsRunning(false);
        setStreamError(extractErrorDetails(error));
      }
    },
    [connectStream, parameters, resetSession]
  );

  const stopQuery = useCallback(async () => {
    if (!executionIdRef.current) {
      return;
    }

    try {
      await cancelQueryExecution(executionIdRef.current);
    } catch (error) {
      setStreamError(extractErrorDetails(error));
    }
  }, []);

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
