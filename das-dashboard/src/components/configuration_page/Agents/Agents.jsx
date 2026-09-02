import { AGENT_GROUPS } from "./agentRegistry"
import {
  AgentsLayout,
  AgentNav,
  AgentNavGroupLabel,
  AgentNavItem
} from "./Agents.styled"

import QueryAgentPanel from "./QueryAgent"
import ContextBrokerPanel from "./ContextBroker"
import EvolutionAgentPanel from "./EvolutionAgent"
import LinkCreationAgentPanel from "./LinkCreation"
import CommandRouterPanel from "./CommandRouter"
import AttentionBrokerPanel from "./AttentionBroker"
import AtomDbBrokerPanel from "./AtomDbBroker"
import BaseParametersPanel from "./BaseParams"

export function AgentsForm({ activeAgent, onAgentChange }) {
  const selectedAgent = activeAgent || "query"

  return (
    <AgentsLayout>
      <AgentNav>
        {AGENT_GROUPS.map((group) => (
          <div key={group.label}>
            <AgentNavGroupLabel>{group.label}</AgentNavGroupLabel>
            {group.items.map((item) => (
              <AgentNavItem
                key={item.key}
                active={selectedAgent === item.key}
                onClick={() => onAgentChange(item.key)}
              >
                {item.label}
              </AgentNavItem>
            ))}
          </div>
        ))}
      </AgentNav>

      {selectedAgent === "query" && <QueryAgentPanel />}
      {selectedAgent === "context" && <ContextBrokerPanel />}
      {selectedAgent === "evolution" && <EvolutionAgentPanel />}
      {selectedAgent === "link_creation" && <LinkCreationAgentPanel />}
      {selectedAgent === "command_router" && <CommandRouterPanel />}
      {selectedAgent === "attention" && <AttentionBrokerPanel />}
      {selectedAgent === "atomdb" && <AtomDbBrokerPanel />}
      {selectedAgent === "base_query" && <BaseParametersPanel />}
    </AgentsLayout>
  )
}
