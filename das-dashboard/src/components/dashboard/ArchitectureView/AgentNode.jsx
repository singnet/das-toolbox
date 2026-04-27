import { Handle, Position } from "reactflow";

export default function AgentNode({ data }) {
  return (
    <div
      style={{
        width: 240,
        borderRadius: 12,
        overflow: "hidden",
        background: "#1e293b",
        border: "1px solid #475569",
        color: "white",
        boxShadow: "0 4px 10px rgba(0,0,0,0.25)",
      }}
    >
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />

      <div
        style={{
          background: "#334155",
          padding: "10px 14px",
          fontWeight: 700,
          fontSize: 13,
          borderBottom: "1px solid #475569",
        }}
      >
        ⚙ Service
      </div>

      <div style={{ padding: 12, fontSize: 12, lineHeight: 1.8 }}>
        <div><strong>Name:</strong> {data.name}</div>
        <div><strong>Port:</strong> {data.port}</div>
        <div><strong>Status:</strong> {data.status}</div>
        <div><strong>CPU:</strong> {data.cpu}</div>
        <div><strong>RAM:</strong> {data.memory}</div>
      </div>
    </div>
  );
}