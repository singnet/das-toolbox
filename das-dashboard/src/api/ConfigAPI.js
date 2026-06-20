import api from "./AxiosBaseClient";

export async function saveConfig(flatConfig) {
  const response = await api.post("/config", flatConfig);
  return response.data;
}

export async function exportConfig(flatConfig) {
  const response = await api.post("/config/export", flatConfig);
  return response.data;
}

export async function getConfig() {
  const response = await api.get("/config");
  return response.data;
}

export async function getConfigDefaults() {
  const response = await api.get("/config/defaults");
  return response.data;
}

export async function getWorkspacePaths() {
  const response = await api.get("/config/workspace-paths");
  return response.data;
}

export async function uploadContextMappingFile(file, { forceOverwrite = false } = {}) {
  const formData = new FormData();
  formData.append("mapping_file", file);

  const response = await api.post(
    `/config/workspace/context-mapping?force_overwrite=${forceOverwrite}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    }
  );

  return response.data;
}
