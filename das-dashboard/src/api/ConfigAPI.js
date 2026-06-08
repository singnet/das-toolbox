import api from "./AxiosBaseClient";

export async function saveConfig(configFile) {
  const formData = new FormData();

  formData.append("config_file", configFile);

  const response = await api.post("/config", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });

  return response.data;
}

export async function getConfig() {
  const response = await api.get("/config");

  return response.data;
}