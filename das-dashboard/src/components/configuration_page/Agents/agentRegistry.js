import SearchIcon from "@mui/icons-material/Search"
import LinkIcon from "@mui/icons-material/Link"
import PsychologyIcon from "@mui/icons-material/Psychology"
import LayersIcon from "@mui/icons-material/Layers"
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome"
import StorageIcon from "@mui/icons-material/Storage"
import HubIcon from "@mui/icons-material/Hub"
import TerminalIcon from "@mui/icons-material/Terminal"

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
        paramsKey: null,
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
        configSection: "brokers",
        paramsKey: null,
        hasPortRange: false
      },
      {
        key: "context",
        label: "Context Broker",
        configSection: "brokers",
        paramsKey: "context",
        hasPortRange: true
      },
      {
        key: "atomdb",
        label: "AtomDB Broker",
        configSection: "brokers",
        paramsKey: null,
        hasPortRange: true
      }
    ]
  }
]

export const ALL_AGENTS = AGENT_GROUPS.flatMap((group) => group.items)

export function getAgentByKey(key) {
  return ALL_AGENTS.find((item) => item.key === key)
}
