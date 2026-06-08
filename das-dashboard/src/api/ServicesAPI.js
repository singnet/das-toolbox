import api from "./AxiosBaseClient";

function normalizeContainerName(fullContainerName) {
    return fullContainerName.replace(/-[0-9]{5}$/, "");
}

async function serviceAction(containerName, action, host = "localhost") {
  const response = await api.post(`/services/${containerName}/${action}`, null, {
    params: { host }
  });
  return response.data;
}

export const startService = (containerName, host) => 
    serviceAction(normalizeContainerName(containerName), "start", host);

export const stopService = (containerName, host) => 
    serviceAction(normalizeContainerName(containerName), "stop", host);

export const restartService = (containerName, host) => 
    serviceAction(normalizeContainerName(containerName), "restart", host);


async function orchestrationAction(action, host = "localhost") {
  const response = await api.post(`/services/orchestration/${action}`, null, {
    params: { host }
  });
  return response.data;
}

export const startArchitecture = (host) => orchestrationAction("start", host);
export const stopArchitecture = (host) => orchestrationAction("stop", host);


async function atomDbAction(action, host = "localhost") {
  const response = await api.post(`/services/atomdb/${action}`, null, {
    params: { host }
  });
  return response.data;
}

export const startDatabases = (host) => atomDbAction("start", host);
export const stopDatabases = (host) => atomDbAction("stop", host);