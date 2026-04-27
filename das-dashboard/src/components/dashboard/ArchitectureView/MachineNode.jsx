import { Handle, Position } from "reactflow";

export default function MachineNode({ data }) {
  return (
    <div
      style={{
        width: 270,
        borderRadius: 14,
        overflow: "hidden",
        background: "#0f172a",
        border: "2px solid #334155",
        color: "white",
        boxShadow: "0 8px 20px rgba(0,0,0,0.35)",
      }}
    >
      <Handle type="source" position={Position.Right} />
      <Handle type="target" position={Position.Left} />

      <div
        style={{
          background: "#1e293b",
          padding: "12px 16px",
          fontWeight: 700,
          fontSize: 14,
          borderBottom: "1px solid #334155",
        }}
      >
        🖥 Server Node
      </div>

      <div style={{ padding: 14, fontSize: 13, lineHeight: 1.8 }}>
        <div><strong>IP:</strong> {data.ip}</div>
        <div><strong>Status:</strong> {data.status}</div>
        <div><strong>CPU Avg:</strong> {data.cpuAvg}</div>
        <div><strong>RAM Avg:</strong> {data.ramAvg}</div>
        <div><strong>Agents:</strong> {data.agentCount}</div>
      </div>
    </div>
  );
}