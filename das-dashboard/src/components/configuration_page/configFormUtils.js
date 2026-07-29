export function parsePortValue(raw) {
  if (raw === "") {
    return undefined
  }

  return Number(raw)
}

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

export function initAgentConnection(sectionDefaults, agentKey) {
  const defaults = sectionDefaults?.[`agents.${agentKey}`] || {}
  const endpoint = splitEndpoint(defaults.endpoint, "0.0.0.0", 40000)
  const range = parsePortsRange(defaults.ports_range)

  return {
    endpoint_ip: endpoint.host,
    endpoint_port: endpoint.port,
    ports_range_start: range.start,
    ports_range_end: range.end
  }
}

export function initCommandRouterForm(sectionDefaults, agentKey = "command_router") {
  const defaults = sectionDefaults?.[`agents.${agentKey}`] || {}

  return {
    ...initAgentConnection(sectionDefaults, agentKey),
    http_api_port: defaults.http_api_port ?? 40009
  }
}

export function getAgentParam(sectionDefaults, agentKey, param, fallback) {
  const section = sectionDefaults?.[`agents.${agentKey}`]
  return section?.[param] ?? fallback
}

export function initRedisMongoConnection(atomdbDefaults, { withCluster = false } = {}) {
  const connection = {
    redis_endpoint: atomdbDefaults?.redis_endpoint || "localhost",
    redis_port: atomdbDefaults?.redis_port ?? 40020,
    mongo_endpoint: atomdbDefaults?.mongo_endpoint || "localhost",
    mongo_port: atomdbDefaults?.mongo_port ?? 40021,
    mongo_username: atomdbDefaults?.mongo_username || "admin",
    mongo_password: atomdbDefaults?.mongo_password || "admin"
  }

  if (!withCluster) {
    return connection
  }

  return {
    ...connection,
    redis_cluster: atomdbDefaults?.redis_cluster ?? false,
    mongo_cluster: atomdbDefaults?.mongo_cluster ?? false,
    redis_nodes: atomdbDefaults?.redis_nodes || [],
    mongo_nodes: atomdbDefaults?.mongo_nodes || []
  }
}

export function initMorkMongoConnection(atomdbDefaults, { withCluster = false } = {}) {
  const connection = {
    mork_endpoint: atomdbDefaults?.mork_endpoint || "localhost",
    mork_port: atomdbDefaults?.mork_port ?? 40022,
    mongo_endpoint: atomdbDefaults?.mongo_endpoint || "localhost",
    mongo_port: atomdbDefaults?.mongo_port ?? 40021,
    mongo_username: atomdbDefaults?.mongo_username || "admin",
    mongo_password: atomdbDefaults?.mongo_password || "admin"
  }

  if (!withCluster) {
    return connection
  }

  return {
    ...connection,
    mongo_cluster: atomdbDefaults?.mongo_cluster ?? false,
    mongo_nodes: atomdbDefaults?.mongo_nodes || []
  }
}

export function initAdapterBackend(atomdbDefaults, backendType, getAtomdbTemplate) {
  const backendDefaults = atomdbDefaults?.atomdb_backend || {}

  if (backendType === "inmemorydb") {
    return { type: "inmemorydb" }
  }

  if (backendType === "redismongodb") {
    const defaults = getAtomdbTemplate?.("redismongodb") || {}
    return {
      type: "redismongodb",
      ...initRedisMongoConnection({ ...defaults, ...backendDefaults }, { withCluster: true })
    }
  }

  if (backendType === "morkdb") {
    const defaults = getAtomdbTemplate?.("morkdb") || {}
    return {
      type: "morkdb",
      ...initMorkMongoConnection({ ...defaults, ...backendDefaults }, { withCluster: true })
    }
  }

  return { type: backendType }
}
