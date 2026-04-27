import React from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";

import MachineNode from "./MachineNode";
import AgentNode from "./AgentNode";

import { mockMachines } from "../../../pages/dashboard/dashboard_mock_data";

const nodeTypes = {
  machine: MachineNode,
  agent: AgentNode,
};

const serviceConnections = [
  { from: "attention-broker", to: "mongodb" },
  { from: "query-engine", to: "redis" },
  { from: "query-engine", to: "attention-broker" },
  { from: "context-broker", to: "link-creation-agent" },
];

export default function ArchitectureView() {
  const nodes = [];
  const edges = [];

  let globalYOffset = 0;

  mockMachines.forEach((machine, machineIndex) => {
    const machineId = `machine-${machineIndex}`;

    nodes.push({
      id: machineId,
      type: "machine",
      position: {
        x: 0,
        y: globalYOffset,
      },
      data: {
        ip: machine.serverIp,
        status: machine.running ? "Online" : "Offline",
        cpuAvg: `${Math.floor(Math.random() * 60)}%`,
        ramAvg: `${(Math.random() * 8).toFixed(1)} GB`,
        agentCount: machine.agents.length,
      },
    });

    machine.agents.forEach((agent, agentIndex) => {
      nodes.push({
        id: agent.name,
        type: "agent",
        position: {
          x: 420,
          y: globalYOffset + agentIndex * 170,
        },
        data: {
          name: agent.name,
          port: agent.port,
          status: agent.status,
          cpu: agent.cpu,
          memory: agent.memory,
        },
      });

      edges.push({
        id: `${machineId}-${agent.name}`,
        source: machineId,
        target: agent.name,
        style: {
          stroke: "#64748b",
          strokeWidth: 2,
        },
      });
    });

    globalYOffset += Math.max(machine.agents.length * 180, 260);
  });

  serviceConnections.forEach((conn, i) => {
    edges.push({
      id: `svc-${i}`,
      source: conn.from,
      target: conn.to,
      animated: true,
      style: {
        stroke: "#3b82f6",
        strokeWidth: 2.5,
      },
    });
  });

  return (
    <div
      style={{
        width: "100%",
        height: "85vh",
        background: "#020617",
        borderRadius: 16,
        overflow: "hidden",
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
      >
        <MiniMap
          style={{
            background: "#0f172a",
          }}
        />
        <Controls />
        <Background gap={20} size={1} color="#1e293b" />
      </ReactFlow>
    </div>
  );
}