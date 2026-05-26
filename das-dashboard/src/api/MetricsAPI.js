import api from "./AxiosBaseClient";

export async function fetchDashboardDataStatic(metricScope = "all", host = "localhost") {

  try {
    const response = await api.get("/metrics", {
      params: {
        metric_scope: metricScope,
        host
      }
    });

    return response.data;

  } catch (error) {
    console.error("Failed to fetch metrics:", error);
    return null;
  }
}

export function fetchDashboardDataStream(onMessage, host, {onOpen, onClose, onError} = {}) {
  const socket = new WebSocket(
    `ws://${host}:8000/metrics/live-ws?metric_scope=all&host=${host}`
  );

  socket.onopen = () => {
    onOpen?.();
  };

  socket.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);
      onMessage(parsed);

    } catch (err) {
      console.error("WebSocket parse error:", err);
    }
  };

  socket.onerror = (err) => {
    console.error("WebSocket error:", err);
    onError?.(err);
  };

  socket.onclose = () => {
    console.warn("WebSocket connection closed.");
    onClose?.();
  };

  return socket;
}