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

  let dasCliErrorMessage = null;

  socket.onopen = () => {
    onOpen?.();
  };

  socket.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);

      if (parsed.type === "error") {
        dasCliErrorMessage = parsed.message;

        onError?.({
          type: "application",
          message: parsed.message,
          raw: parsed
        });

        onData?.(parsed);
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
    if (dasCliErrorMessage) return;
    onError?.({
      type: "transport",
      message: "WebSocket transport error.",
      raw: event
    });
  };

  socket.onclose = (event) => {
    onClose?.({
      code: event.code,
      reason: dasCliErrorMessage || event.reason || "Metrics stream closed unexpectedly.",
      wasClean: event.wasClean,
      isDasCliError: !!dasCliErrorMessage
    });
  };

  return {
    close: () => {
      socket.close();
    }
  };
}