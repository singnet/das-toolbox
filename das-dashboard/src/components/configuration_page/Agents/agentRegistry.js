import QueryParams from "./AgentsParams/QueryParams"
import LinkCreationParams from "./AgentsParams/LinkCreationParams"
import EvolutionParams from "./AgentsParams/EvolutionParams"
import ContextParams from "./AgentsParams/ContextParams"
import BaseQueryParams from "./AgentsParams/BaseParams"
import InferenceParams from "./AgentsParams/InferenceParams"

export const AGENT_GROUPS = [
  {
    label: "Agents",
    items: [
      { key: "query", label: "Query Agent", paramsKey: "query" },
      { key: "link_creation", label: "Link Creation Agent", paramsKey: "link_creation" },
      { key: "inference", label: "Inference Agent", paramsKey: "inference" },
      { key: "evolution", label: "Evolution Agent", paramsKey: "evolution" },
      { key: "command_router", label: "Command Router", paramsKey: null }
    ]
  },
  {
    label: "Brokers",
    items: [
      { key: "attention", label: "Attention Broker", paramsKey: null },
      { key: "context", label: "Context Broker", paramsKey: "context" },
      { key: "atomdb", label: "AtomDB Broker", paramsKey: null }
    ]
  },
  {
    label: "Agent Params",
    items: [
      { key: "base_query", label: "Base Parameters", paramsKey: "base_query" }
    ]
  }
]

const ALL_AGENTS = AGENT_GROUPS.flatMap((group) => group.items)

export function getAgentByKey(key) {
  return ALL_AGENTS.find((item) => item.key === key)
}

export const AGENT_COMPONENTS = {
  query: QueryParams,
  link_creation: LinkCreationParams,
  evolution: EvolutionParams,
  context: ContextParams,
  base_query: BaseQueryParams,
  inference: InferenceParams,
}
