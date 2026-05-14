import api from "./AxiosBaseClient";
import { SERVICE_CLI_NAMES } from "../components/dashboard/ArchitectureView/utils/constants"

export async function executeDashboardAction(container_name, action, target_ip) {
  const prefix = container_name.replace(/-\d+$/, '');
  const shortServiceName = SERVICE_CLI_NAMES[prefix] || prefix;

  try {
    const response = await api.post(`/dashboard/service`, null, {
      params: { 
        action: action,
        targetIp: target_ip,
        targetService: shortServiceName
      }
    });
    
    return response.data;
  } catch (error) {
    console.error("Action execution failed:", error.response?.data || error.message);
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

export function fetchDashboardDataStream(onMessage, targetIp = "localhost") {
  const ip = targetIp || "localhost";
  
  const socketUrl = `ws://localhost:8000/dashboard/metrics/stream?metric_scope=all&target_ip=${ip}`;
  
  const socket = new WebSocket(socketUrl);

  socket.onopen = () => {
    console.log(`[WebSocket] Connected to metrics stream: ${ip}`);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    } catch (err) {
      console.error("[WebSocket] Error parsing incoming data:", err);
    }
  };

  socket.onerror = (err) => {
    console.error(`[WebSocket] Connection error on host ${ip}:`, err);
  };

  socket.onclose = (event) => {
    console.log(`[WebSocket] Connection closed for ${ip}. Code: ${event.code}`);
  };

  return socket;
}