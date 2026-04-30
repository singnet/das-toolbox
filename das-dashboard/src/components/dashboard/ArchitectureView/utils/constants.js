export const EXPECTED_SERVICES = {
  Agents: [
    "das-query-engine-40002",
    "das-link-creation-agent-40007",
    "das-inference-agent-40008",
    "das-evolution-agent-40009",
  ],
  Brokers: [
    "das-attention-broker-40001",
    "das-context-broker-40004",
    "das-atomdb-broker-40010",
  ],
  Loaders: [
    "metta-loader",
    "metta-mork-loader",
  ],
  AtomDB: [
    "das-cli-mongodb-40020",
    "das-cli-redis-40021",
    "das-morkdb-40022",
  ],
};

export const SERVICE_LABELS = {
  "das-query-engine-40002": "Query Agent",
  "das-link-creation-agent-40007":
    "Link Creation Agent",
  "das-inference-agent-40008": "Inference Agent",
  "das-evolution-agent-40009": "Evolution Agent",

  "das-attention-broker-40001": "Attention Broker",
  "das-context-broker-40004": "Context Broker",
  "das-atomdb-broker-40010": "AtomDB Broker",

  "metta-loader": "Metta Loader",
  "metta-mork-loader": "Metta Mork Loader",

  "das-cli-mongodb-40020": "MongoDB",
  "das-cli-redis-40021": "Redis",
  "das-morkdb-40022": "MorkDB",
};