import api from "./AxiosBaseClient";

export async function getQueryParamDefaults() {
  const response = await api.get("/query/param/defaults");
  return response.data;
}

export async function startQueryExecution(queryText, parameters = null) {
  const payload = {
    command_type: "query",
    command_text: queryText
  };

  if (parameters && Object.keys(parameters).length > 0) {
    payload.parameters = parameters;
  }

  const response = await api.post("/query/executions", payload);
  return response.data;
}

export async function getQueryExecutionStatus(executionId) {
  const response = await api.get(`/query/executions/${executionId}`);
  return response.data;
}

export async function getQueryAnswers(executionId, page = 1, pageSize = 10) {
  const response = await api.get(`/query/executions/${executionId}/answers`, {
    params: { page, page_size: pageSize }
  });
  return response.data;
}

export async function cancelQueryExecution(executionId) {
  const response = await api.post(`/query/executions/${executionId}/cancel`);
  return response.data;
}
