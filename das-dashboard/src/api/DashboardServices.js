import api from "./AxiosBaseClient";
import { SERVICE_CLI_NAMES } from "../components/dashboard/ArchitectureView/utils/constants"

export async function executeDashboardAction(container_name, action, target_ip) {
  const prefix = container_name.replace(/-\d+$/, '');
  const shortServiceName = SERVICE_CLI_NAMES[prefix] || prefix;

  const reqBody = {
    targetIp: target_ip,
    targetUsername: "nonetest",
    targetService: shortServiceName,
    targetAction: action
  };

  try {
    const response = await api.get(`/dashboard/service`, {
      params: { 
        action: action,
        ...reqBody 
      }
    });
    return response.data;
  } catch (error) {
    console.error("Action execution failed:", error);
    throw error;
  }
}

export async function saveConfigtoDashboard(fileContent) {
  const formData = new FormData();
  formData.append('config_file', fileContent);

  try {
    const response = await api.post("/dashboard/config", formData, { 
      headers: { 'Content-Type': 'multipart/form-data' } 
    });
    return response.data;
  } catch (error) {
    console.error("Upload failed:", error);
    throw error;
  }
}

export async function fetchDashboardDataStatic(metricScope = "all", targetIp = "localhost") {
  try {
    const response = await api.get("/dashboard/metrics", {
      params: {
        metric_scope: metricScope,
        target_ip: targetIp,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch!", error);
    return null;
  }
}

export function fetchDashboardDataStream(onMessage) {
  const socket = new WebSocket("ws://localhost:8000/dashboard/metrics/stream?metric_scope=all&target_ip=localhost");

  socket.onopen = () => {
    console.log("WebSocket successfully connected.");
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    } catch (err) {
      console.error("Error processing websocket data.", err);
    }
  };

  socket.onerror = (err) => {
    console.error("Error in WebSocket:", err);
  };

  socket.onclose = (event) => {
    console.log("WebSocket closed:", event.code, event.reason);
  };

  return socket;
}