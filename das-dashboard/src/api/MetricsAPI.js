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

export function fetchDashboardDataStream(onMessage, host, { onOpen, onClose, onError } = {}) {
  const socket = new WebSocket(
    `ws://${host}:8000/metrics/live-ws?metric_scope=all&host=${host}`
  )

  socket.onopen = () => {
    onOpen?.()
  }

  socket.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data)

      if (parsed.type === "error") {
        console.error("WebSocket application error:", parsed.message)

        onError?.({
          type: "application",
          message: parsed.message,
          raw: parsed
        })

        return
      }

      onMessage(parsed)

    } catch (err) {
      console.error("WebSocket parse error:", err)

      onError?.({
        type: "parse",
        message: err.message,
        raw: err
      })
    }
  }

  socket.onerror = (event) => {
    console.error("WebSocket transport error:", event)

    onError?.({
      type: "transport",
      message: "WebSocket transport error.",
      raw: event
    })
  }

  socket.onclose = (event) => {
    console.warn(
      "WebSocket closed:",
      event.code,
      event.reason
    )

    onClose?.({
      code: event.code,
      reason: event.reason,
      wasClean: event.wasClean
    })
  }

  return socket
}