export function splitEndpoint(endpoint, defaultHost = "localhost", defaultPort = 40020) {
  if (!endpoint) {
    return { host: defaultHost, port: defaultPort }
  }

  const [host, port] = String(endpoint).split(":")

  return {
    host: host || defaultHost,
    port: Number(port) || defaultPort
  }
}

export function parsePortsRange(range, defaultStart = 42000, defaultEnd = 42999) {
  if (!range) {
    return { start: defaultStart, end: defaultEnd }
  }

  const [start, end] = String(range).split(":")

  return {
    start: Number(start) || defaultStart,
    end: Number(end) || defaultEnd
  }
}

const CONNECTION_FIELDS = [
  "endpoint_ip",
  "endpoint_port",
  "ports_range_start",
  "ports_range_end"
]

export function buildAgentPayload(form, { withPortRange = true } = {}) {
  const payload = {
    endpoint: `${form.endpoint_ip}:${form.endpoint_port}`
  }

  if (withPortRange) {
    payload.ports_range = `${form.ports_range_start}:${form.ports_range_end}`
  }

  Object.entries(form).forEach(([key, value]) => {
    if (!CONNECTION_FIELDS.includes(key)) {
      payload[key] = value
    }
  })

  return payload
}

export function initAgentConnection(getDefault, agentKey) {
  const endpoint = splitEndpoint(getDefault(`agents.${agentKey}.endpoint`), "0.0.0.0", 40000)
  const range = parsePortsRange(getDefault(`agents.${agentKey}.ports_range`))

  return {
    endpoint_ip: endpoint.host,
    endpoint_port: endpoint.port,
    ports_range_start: range.start,
    ports_range_end: range.end
  }
}

export function getAgentParam(getDefault, agentKey, param, fallback) {
  return getDefault(`agents.${agentKey}.params.${param}`) ?? fallback
}

export function initRedisMongoConnection(getDefault, prefix = "atomdb.", { withCluster = false } = {}) {
  const redis = splitEndpoint(getDefault(`${prefix}redis.endpoint`), "localhost", 40020)
  const mongo = splitEndpoint(getDefault(`${prefix}mongodb.endpoint`), "localhost", 40021)

  const connection = {
    redis_endpoint: redis.host,
    redis_port: redis.port,
    mongo_endpoint: mongo.host,
    mongo_port: mongo.port,
    mongo_username: getDefault(`${prefix}mongodb.username`) || "admin",
    mongo_password: getDefault(`${prefix}mongodb.password`) || "admin"
  }

  if (!withCluster) {
    return connection
  }

  return {
    ...connection,
    redis_cluster: getDefault(`${prefix}redis.cluster`) ?? false,
    mongo_cluster: getDefault(`${prefix}mongodb.cluster`) ?? false,
    redis_nodes: getDefault(`${prefix}redis.nodes`) || [],
    mongo_nodes: getDefault(`${prefix}mongodb.nodes`) || []
  }
}

export function initMorkMongoConnection(getDefault, prefix = "atomdb.", { withCluster = false } = {}) {
  const mork = splitEndpoint(getDefault(`${prefix}morkdb.endpoint`), "localhost", 40022)
  const mongo = splitEndpoint(getDefault(`${prefix}mongodb.endpoint`), "localhost", 40021)

  const connection = {
    mork_endpoint: mork.host,
    mork_port: mork.port,
    mongo_endpoint: mongo.host,
    mongo_port: mongo.port,
    mongo_username: getDefault(`${prefix}mongodb.username`) || "admin",
    mongo_password: getDefault(`${prefix}mongodb.password`) || "admin"
  }

  if (!withCluster) {
    return connection
  }

  return {
    ...connection,
    mongo_cluster: getDefault(`${prefix}mongodb.cluster`) ?? false,
    mongo_nodes: getDefault(`${prefix}mongodb.nodes`) || []
  }
}

export function initAdapterBackend(getDefault, backendType) {
  const prefix = "atomdb.adapterdb.atomdb_backend."

  if (backendType === "inmemorydb") {
    return { type: "inmemorydb" }
  }

  if (backendType === "redismongodb") {
    return {
      type: "redismongodb",
      ...initRedisMongoConnection(getDefault, prefix, { withCluster: true })
    }
  }

  if (backendType === "morkdb") {
    return {
      type: "morkdb",
      ...initMorkMongoConnection(getDefault, prefix, { withCluster: true })
    }
  }

  return { type: backendType }
}
