export const SERVICE_CLI_NAMES = {
  "das-query-engine": "query-agent",
  "das-link-creation-agent": "link-creation-agent",
  "das-inference-agent": "inference-agent",
  "das-evolution-agent": "evolution-agent",
  "das-attention-broker": "attention-broker",
  "das-context-broker": "context-broker",
  "das-atomdb-broker": "atomdb-broker",
  "metta-loader": "metta load",
  "metta-mork-loader": "metta load",
  "das-cli-mongodb": "db",
  "das-cli-redis": "db",
  "das-morkdb": "db"
};

export const EXPECTED_SERVICES = {
  Agents: [
    "das-query-engine",
    "das-link-creation-agent",
    "das-inference-agent",
    "das-evolution-agent",
  ],
  Brokers: [
    "das-attention-broker",
    "das-context-broker",
    "das-atomdb-broker",
  ],
  Loaders: [
    "metta-loader",
    "metta-mork-loader",
  ],
  AtomDB: [
    "das-cli-mongodb",
    "das-cli-redis",
    "das-morkdb",
  ],
};

export const SERVICE_LABELS = {
  "das-query-engine": "Query Agent",
  "das-link-creation-agent": "Link Creation Agent",
  "das-inference-agent": "Inference Agent",
  "das-evolution-agent": "Evolution Agent",

  "das-attention-broker": "Attention Broker",
  "das-context-broker": "Context Broker",
  "das-atomdb-broker": "AtomDB Broker",

  "metta-loader": "Metta Loader",
  "metta-mork-loader": "Metta Mork Loader",

  "das-cli-mongodb": "MongoDB",
  "das-cli-redis": "Redis",
  "das-morkdb": "MorkDB",
};