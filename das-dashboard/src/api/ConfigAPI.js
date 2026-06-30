import api from "./AxiosBaseClient";

export async function saveConfig(flatConfig) {
  const response = await api.post("/config/save", flatConfig);
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

export async function getConfigDefaults({ factory = false } = {}) {
  const response = await api.get("/config/defaults", {
    params: factory ? { factory: true } : undefined,
  });
  return response.data;
}
