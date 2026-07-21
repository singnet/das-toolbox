const WS_BASE = "ws://localhost:8000";

export function createQueryExecutionStream(executionId, { onEvent, onOpen, onClose, onError }) {
  const socket = new WebSocket(`${WS_BASE}/query/executions/${executionId}`);

  socket.onopen = () => {
    onOpen?.();
  };

  socket.onmessage = (event) => {
    try {
      onEvent?.(JSON.parse(event.data));
    } catch (error) {
      onError?.({
        type: "parse",
        message: error.message
      });
    }
  };

  socket.onerror = () => {
    onError?.({
      type: "transport",
      message: "Query stream connection error."
    });
  };

  socket.onclose = (event) => {
    onClose?.({
      code: event.code,
      reason: event.reason,
      wasClean: event.wasClean
    });
  };

  return {
    close: () => {
      socket.close();
    }
  };
}
