import api from "./AxiosBaseClient";

async function serviceAction(serviceCommand, action, host = "localhost") {
  const response = await api.post(`/services/${serviceCommand}/${action}`, null, {
    params: { host }
  });
  return response.data;
}

export const startService = (serviceCommand, host) =>
  serviceAction(serviceCommand, "start", host);

export const stopService = (serviceCommand, host) =>
  serviceAction(serviceCommand, "stop", host);

export const restartService = (serviceCommand, host) =>
  serviceAction(serviceCommand, "restart", host);

async function orchestrationAction(action, services) {
  const response = await api.post(`/services/orchestration/${action}`, services);
  return response.data;
}

export const startArchitecture = (services) => orchestrationAction("start", services);

export const stopArchitecture = (services) => orchestrationAction("stop", services);

async function atomDbAction(action, host = "localhost") {
  const response = await api.post(`/services/atomdb/${action}`, null, {
    params: { host }
  });
  return response.data;
}

export const startDatabases = (host) => atomDbAction("start", host);
export const stopDatabases = (host) => atomDbAction("stop", host);
