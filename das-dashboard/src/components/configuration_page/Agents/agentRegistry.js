import SearchIcon from "@mui/icons-material/Search"
import LinkIcon from "@mui/icons-material/Link"
import PsychologyIcon from "@mui/icons-material/Psychology"
import LayersIcon from "@mui/icons-material/Layers"
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome"
import StorageIcon from "@mui/icons-material/Storage"
import HubIcon from "@mui/icons-material/Hub"
import TerminalIcon from "@mui/icons-material/Terminal"

import QueryParams from "./AgentsParams/QueryParams"
import LinkCreationParams from "./AgentsParams/LinkCreationParams"
import EvolutionParams from "./AgentsParams/EvolutionParams"
import ContextParams from "./AgentsParams/ContextParams"
import BaseQueryParams from "./AgentsParams/BaseParams"

export const AGENT_GROUPS = [
  {
    label: "Agents",
    items: [
      {
        key: "query",
        label: "Query Agent",
        configSection: "agents",
        paramsKey: "query",
        hasPortRange: true
      },
      {
        key: "link_creation",
        label: "Link Creation Agent",
        configSection: "agents",
        paramsKey: "link_creation",
        hasPortRange: true
      },
      {
        key: "inference",
        label: "Inference Agent",
        configSection: "agents",
        paramsKey: 'inference',
        hasPortRange: true
      },
      {
        key: "evolution",
        label: "Evolution Agent",
        configSection: "agents",
        paramsKey: "evolution",
        hasPortRange: true
      },
      {
        key: "command_router",
        label: "Command Router",
        configSection: "agents",
        paramsKey: null,
        hasPortRange: true
      }
    ]
  },
  {
    label: "Brokers",
    items: [
      {
        key: "attention",
        label: "Attention Broker",
        configSection: "agents",
        paramsKey: null,
        hasPortRange: false
      },
      {
        key: "context",
        label: "Context Broker",
        configSection: "agents",
        paramsKey: "context",
        hasPortRange: true
      },
      {
        key: "atomdb",
        label: "AtomDB Broker",
        configSection: "agents",
        paramsKey: null,
        hasPortRange: true
      }
    ]
  },
  {
    label: "Agent Params",
    items: [
      {
        key: "base_query",
        label: "Base Parameters",
        configSection: "agents",
        paramsKey: "base_query",
        hasPortRange: false
      }
    ]
  }
]

export const ALL_AGENTS = AGENT_GROUPS.flatMap((group) => group.items)

export function getAgentByKey(key) {
  return ALL_AGENTS.find((item) => item.key === key)
}

export const AGENT_COMPONENTS = {
  query: QueryParams,
  link_creation: LinkCreationParams,
  evolution: EvolutionParams,
  context: ContextParams,
  base_query: BaseQueryParams
}