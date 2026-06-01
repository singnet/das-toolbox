export function createMetricsStream({
  host,
  onData,
  onOpen,
  onClose,
  onError
}) {

  const socket = new WebSocket(
    `ws://localhost:8000/metrics/live-ws?metric_scope=all&host=${host}`
  );

  socket.onopen = () => {
    onOpen?.();
  };

  socket.onmessage = (event) => {

    try {

      const parsed = JSON.parse(event.data);

      if (parsed.type === "error") {

        onError?.({
          type: "application",
          message: parsed.message,
          raw: parsed
        });

        return;
      }

      onData?.(parsed);

    } catch (err) {
      onError?.({
        type: "parse",
        message: err.message,
        raw: err
      });
    }
  };

  socket.onerror = (event) => {

    onError?.({
      type: "transport",
      message: "WebSocket transport error.",
      raw: event
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