import api from "./AxiosBaseClient";

export async function setQueryParameters(params) {
  const response = await api.post("/query/executions", {
    command_type: "set",
    command_text: JSON.stringify(params)
  });
  return response.data;
}
