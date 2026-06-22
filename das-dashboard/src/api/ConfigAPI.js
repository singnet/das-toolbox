import api from "./AxiosBaseClient";

export async function saveConfig(flatConfig) {
  const response = await api.post("/config/save", flatConfig);
  return response.data;
}

export async function getConfigSaved() {
  const response = await api.get("/config/saved");
  return response.data;
}

export async function exportConfig() {
  const response = await api.post("/config/export");
  return response.data;
}

export async function getExportTargets() {
  const response = await api.post("/config/export/targets");
  return response.data;
}

export async function exportConfigScp(ip) {
  const response = await api.post(`/config/export/scp/${encodeURIComponent(ip)}`);
  return response.data;
}

export async function loadConfig(nestedConfig) {
  const response = await api.post("/config/load", nestedConfig);
  return response.data;
}

export async function saveContextMapping({ content, path } = {}) {
  const payload = {}
  if (path !== undefined) {
    payload.path = path
  }
  if (content !== undefined) {
    payload.content = content
  }
  const response = await api.post("/config/adapter/context-mapping", payload);
  return response.data;
}

export async function getConfigDefaults() {
  const response = await api.get("/config/defaults");
  return response.data;
}
