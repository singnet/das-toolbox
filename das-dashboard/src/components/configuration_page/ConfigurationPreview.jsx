import { Box, Typography } from "@mui/material"
import { getAgentByKey } from "./Agents/agentRegistry"
import {
  PreviewContainer,
  PreviewEmpty,
  PreviewFieldGrid,
  PreviewFieldLabel,
  PreviewFieldValue,
  PreviewNestedBlock,
  PreviewPeerBlock,
  PreviewSection,
  PreviewSectionTitle
} from "./ConfigurationPreview.styled"

const FIELD_LABELS = {
  atomdb_type: "Database Type",
  redis_endpoint: "Redis Endpoint",
  redis_port: "Redis Port",
  mongo_endpoint: "MongoDB Endpoint",
  mongo_port: "MongoDB Port",
  mongo_username: "MongoDB Username",
  mongo_password: "MongoDB Password",
  redis_cluster: "Redis Cluster",
  mongo_cluster: "MongoDB Cluster",
  redis_nodes: "Redis Cluster Nodes",
  mongo_nodes: "MongoDB Cluster Nodes",
  mork_endpoint: "MorkDB Endpoint",
  mork_port: "MorkDB Port",
  remote_peers: "Remote Peers",
  adapter_type: "Adapter Type",
  adapter_endpoint: "Adapter Endpoint",
  adapter_port: "Adapter Port",
  db_host: "Database Host",
  db_port: "Database Port",
  db_name: "Database Name",
  db_username: "Database Username",
  db_password: "Database Password",
  export_metta_enabled: "Export MeTTa on Mapping",
  export_metta_output_dir: "MeTTa Output Directory",
  persistence_reuse_mongodb: "Reuse MongoDB Persistence",
  atomdb_backend: "AtomDB Backend",
  endpoint: "Endpoint",
  ports_range: "Ports Range",
  jupyter_endpoint: "Jupyter Endpoint",
  jupyter_port: "Jupyter Port",
  positive_importance_flag: "Positive Importance",
  disregard_importance_flag: "Disregard Importance",
  unique_value_flag: "Unique Value",
  count_flag: "Count Flag",
  max_answers: "Max Answers",
  repeat_count: "Repeat Count",
  context: "Context",
  attention_update: "Attention Update",
  attention_correlation: "Attention Correlation",
  attention_focus_strictness: "Attention Focus Strictness",
  http_api_port: "HTTP API Port",
  query_interval: "Query Interval",
  query_timeout: "Query Timeout",
  use_metta_as_query_tokens: "Use MeTTa as Query Tokens",
  population_size: "Population Size",
  max_generations: "Max Generations",
  elitism_rate: "Elitism Rate",
  selection_rate: "Selection Rate",
  initial_rent_rate: "Initial Rent Rate",
  initial_spreading_rate_lowerbound: "Spreading Rate Lower Bound",
  initial_spreading_rate_upperbound: "Spreading Rate Upper Bound",
  use_cache: "Use Cache",
  enforce_cache_recreation: "Enforce Cache Recreation",
  max_bundle_size: "Max Bundle Size",
  unique_assignment_flag: "Unique Assignment",
  use_link_template_cache: "Use Link Template Cache",
  populate_metta_mapping: "Populate MeTTa Mapping",
  allow_incomplete_chain_path: "Allow Incomplete Chain Path",
  uid: "Peer UID",
  type: "Connection Type",
  local_persistence: "Local Persistence"
}

const ATOMDB_TYPE_LABELS = {
  redismongodb: "Redis + MongoDB",
  morkdb: "Mork + MongoDB",
  inmemorydb: "In Memory",
  remotedb: "Remote DB (Multi-Peer)",
  adapterdb: "AdapterDB"
}

const AGENT_CONFIG_KEYS = [
  "agents.query",
  "agents.link_creation",
  "agents.inference",
  "agents.evolution",
  "agents.command_router",
  "agents.attention",
  "agents.context",
  "agents.atomdb",
  "agents.base_query"
]

function formatFieldLabel(key) {
  return FIELD_LABELS[key] || key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatAtomdbType(value) {
  return ATOMDB_TYPE_LABELS[value] || value
}

function formatPreviewValue(key, value) {
  if (value === null || value === undefined || value === "") {
    return "—"
  }

  if (key === "atomdb_type" || key === "type") {
    return formatAtomdbType(value) || String(value)
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No"
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return "None"
    }

    return null
  }

  if (typeof value === "object") {
    return null
  }

  return String(value)
}

function PreviewField({ label, value }) {
  return (
    <>
      <PreviewFieldLabel>{label}</PreviewFieldLabel>
      <PreviewFieldValue>{value}</PreviewFieldValue>
    </>
  )
}

function PreviewNodeList({ nodes, title }) {
  if (!nodes?.length) {
    return null
  }

  return (
    <PreviewNestedBlock>
      <Typography variant="caption" sx={{ fontWeight: 600, color: "#374151", display: "block", mb: 1 }}>
        {title}
      </Typography>
      {nodes.map((node, index) => (
        <Box
          key={`${title}-${index}`}
          sx={{
            display: "grid",
            gridTemplateColumns: "100px 1fr",
            gap: 1,
            fontSize: 13,
            mb: 0.5
          }}
        >
          <Typography component="span" sx={{ color: "#9ca3af", fontSize: 12 }}>
            Node {index + 1}
          </Typography>
          <Typography component="span" sx={{ color: "#374151", fontSize: 13 }}>
            {node.username || "—"} @ {node.ip || "—"}
          </Typography>
        </Box>
      ))}
    </PreviewNestedBlock>
  )
}

function PreviewPeer({ peer, index }) {
  const skipKeys = new Set(["local_persistence"])

  return (
    <PreviewPeerBlock>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: 13, mb: 1 }}>
        Peer {index + 1}
      </Typography>

      <PreviewFieldGrid>
        {Object.entries(peer)
          .filter(([key]) => !skipKeys.has(key))
          .map(([key, value]) => {
            const formatted = formatPreviewValue(key, value)
            if (formatted === null) {
              return null
            }

            return (
              <PreviewField
                key={key}
                label={formatFieldLabel(key)}
                value={formatted}
              />
            )
          })}
      </PreviewFieldGrid>

      {peer.local_persistence && (
        <PreviewNestedBlock sx={{ mt: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 600, color: "#374151", display: "block", mb: 1 }}>
            Local Persistence
          </Typography>
          <PreviewFieldGrid>
            {Object.entries(peer.local_persistence).map(([key, value]) => {
              const formatted = formatPreviewValue(key, value)
              if (formatted === null) {
                return null
              }

              return (
                <PreviewField
                  key={key}
                  label={formatFieldLabel(key)}
                  value={formatted}
                />
              )
            })}
          </PreviewFieldGrid>
        </PreviewNestedBlock>
      )}
    </PreviewPeerBlock>
  )
}

function PreviewFields({ data, skipKeys = [] }) {
  const skipped = new Set(skipKeys)

  return (
    <>
      <PreviewFieldGrid>
        {Object.entries(data)
          .filter(([key]) => !skipped.has(key))
          .map(([key, value]) => {
            if (
              key === "remote_peers" ||
              key === "redis_nodes" ||
              key === "mongo_nodes" ||
              key === "atomdb_backend"
            ) {
              return null
            }

            const formatted = formatPreviewValue(key, value)
            if (formatted === null) {
              return null
            }

            return (
              <PreviewField
                key={key}
                label={formatFieldLabel(key)}
                value={formatted}
              />
            )
          })}
      </PreviewFieldGrid>

      <PreviewNodeList nodes={data.redis_nodes} title="Redis Cluster Nodes" />
      <PreviewNodeList nodes={data.mongo_nodes} title="MongoDB Cluster Nodes" />

      {Array.isArray(data.remote_peers) && data.remote_peers.length > 0 && (
        <Box sx={{ mt: 1.5 }}>
          <Typography variant="caption" sx={{ fontWeight: 600, color: "#374151", display: "block", mb: 1 }}>
            Remote Peers
          </Typography>
          {data.remote_peers.map((peer, index) => (
            <PreviewPeer key={peer.uid || index} peer={peer} index={index} />
          ))}
        </Box>
      )}
    </>
  )
}

function AtomDBPreview({ atomdb }) {
  if (!atomdb || Object.keys(atomdb).length === 0) {
    return (
      <PreviewSection>
        <PreviewSectionTitle>AtomDB</PreviewSectionTitle>
        <PreviewEmpty>No AtomDB settings applied yet.</PreviewEmpty>
      </PreviewSection>
    )
  }

  const { atomdb_backend: atomdbBackend, ...atomdbFields } = atomdb

  return (
    <PreviewSection>
      <PreviewSectionTitle>AtomDB</PreviewSectionTitle>
      {atomdb.atomdb_type && (
        <Typography sx={{ fontSize: 13, color: "#6b7280", mb: 1.5 }}>
          {formatAtomdbType(atomdb.atomdb_type)}
        </Typography>
      )}
      <PreviewFields data={atomdbFields} />

      {atomdbBackend && Object.keys(atomdbBackend).length > 0 && (
        <PreviewNestedBlock sx={{ mt: 2 }}>
          <Typography variant="caption" sx={{ fontWeight: 600, color: "#374151", display: "block", mb: 1 }}>
            AtomDB Backend
            {atomdbBackend.type ? ` (${formatAtomdbType(atomdbBackend.type)})` : ""}
          </Typography>
          <PreviewFields data={atomdbBackend} />
        </PreviewNestedBlock>
      )}
    </PreviewSection>
  )
}

function AgentPreview({ configKey, data }) {
  const agentKey = configKey.replace("agents.", "")
  const agent = getAgentByKey(agentKey)
  const title = agent?.label || formatFieldLabel(agentKey)

  if (!data || Object.keys(data).length === 0) {
    return null
  }

  return (
    <PreviewSection>
      <PreviewSectionTitle>{title}</PreviewSectionTitle>
      <PreviewFields data={data} />
    </PreviewSection>
  )
}

function EnvironmentPreview({ environment }) {
  if (!environment || Object.keys(environment).length === 0) {
    return (
      <PreviewSection>
        <PreviewSectionTitle>Environment</PreviewSectionTitle>
        <PreviewEmpty>No environment settings applied yet.</PreviewEmpty>
      </PreviewSection>
    )
  }

  return (
    <PreviewSection>
      <PreviewSectionTitle>Environment</PreviewSectionTitle>
      <PreviewFields data={environment} />
    </PreviewSection>
  )
}

export default function ConfigurationPreview({ config = {} }) {
  const hasAgents = AGENT_CONFIG_KEYS.some((key) => config[key] && Object.keys(config[key]).length > 0)
  const isEmpty =
    !config.atomdb &&
    !config.environment &&
    !hasAgents

  if (isEmpty) {
    return (
      <PreviewContainer>
        <PreviewEmpty>
          No configuration applied yet. Fill in a section and click Apply to see it here.
        </PreviewEmpty>
      </PreviewContainer>
    )
  }

  return (
    <PreviewContainer>
      <AtomDBPreview atomdb={config.atomdb} />

      {AGENT_CONFIG_KEYS.map((key) => (
        <AgentPreview key={key} configKey={key} data={config[key]} />
      ))}

      <EnvironmentPreview environment={config.environment} />
    </PreviewContainer>
  )
}
