import { useCallback, useEffect, useState } from "react";

import { getConfigDefaults } from "../api/ConfigAPI";

function atomdbForSidebar(section) {
  if (!section || typeof section !== "object") return null;

  const remotePeers = Array.isArray(section.remote_peers)
    ? section.remote_peers.map((peer) => ({
        type: peer?.type,
        redis_endpoint: peer?.redis_endpoint,
        redis_port: peer?.redis_port,
        mongo_endpoint: peer?.mongo_endpoint,
        mongo_port: peer?.mongo_port,
      }))
    : [];

  return {
    atomdb_type: section.atomdb_type ?? null,
    remote_peers: remotePeers,
  };
}

export function useSidebarAtomdbConfig() {
  const [atomdb, setAtomdb] = useState(null);

  const reloadAtomdbConfig = useCallback(async () => {
    const defaults = await getConfigDefaults();
    setAtomdb(atomdbForSidebar(defaults?.content?.atomdb));
  }, []);

  useEffect(() => {
    let active = true;
    reloadAtomdbConfig().catch((error) => {
      console.error("Failed to load AtomDB config for sidebar:", error);
      if (active) setAtomdb(null);
    });
    return () => {
      active = false;
    };
  }, [reloadAtomdbConfig]);

  return atomdb;
}
