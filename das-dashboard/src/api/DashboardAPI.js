import api from "./AxiosBaseClient";

export async function getInitialState() {
  const response = await api.get("/initial-state");
  return response.data;
}
