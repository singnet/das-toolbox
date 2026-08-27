import api from "./AxiosBaseClient";

export function extractMetricsContent(payload) {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  if (payload.serviceInfo) {
    return payload;
  }

  if (payload.content?.serviceInfo) {
    return payload.content;
  }

  return payload.content ?? payload;
}

export async function fetchDashboardDataStatic(metricScope = "all", host = "localhost") {
  const response = await api.get("/metrics", {
    params: {
      metric_scope: metricScope,
      host,
    },
  });

  return extractMetricsContent(response.data);
}

export async function fetchMetricsHistory(serverIp, period) {
  const response = await api.get("/metrics/history", {
    params: {
      server_ip: serverIp,
      period,
    },
  });

  return extractMetricsContent(response.data);
}

export async function fetchCollectionStatus(serverIp) {
  const response = await api.get("/metrics/collection", {
    params: { server_ip: serverIp },
  });

  return extractMetricsContent(response.data);
}

export async function setCollectionEnabled(serverIp, enabled) {
  const response = await api.post("/metrics/collection", null, {
    params: {
      server_ip: serverIp,
      enabled,
    },
  });

  return extractMetricsContent(response.data);
}

export async function deleteServerHistory(serverIp) {
  const response = await api.delete(`/metrics/history/${encodeURIComponent(serverIp)}`);
  return extractMetricsContent(response.data);
}

export async function deleteUnusedHistory() {
  const response = await api.delete("/metrics/history", {
    params: { unused_only: true },
  });

  return extractMetricsContent(response.data);
}

export async function deleteAllHistory() {
  const response = await api.delete("/metrics/history");
  return extractMetricsContent(response.data);
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
