import api from "./AxiosBaseClient";

export async function setQueryParameters(params) {
  const response = await api.post("/query/executions", {
    command_type: "set",
    command_text: JSON.stringify(params)
  });
  return response.data;
}

export async function startQueryExecution(queryText) {
  const response = await api.post("/query/executions", {
    command_type: "query",
    command_text: queryText
  });
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
