import { useCallback, useEffect, useState } from "react";

import { getConfigDefaults } from "../api/ConfigAPI";

function sidebarAtomdb(section) {
  if (!section || typeof section !== "object") return null;

  const peers = Array.isArray(section.remote_peers)
    ? section.remote_peers.map((peer) => ({
        type: peer?.type,
        redis_endpoint: peer?.redis_endpoint,
        redis_port: peer?.redis_port,
        mongo_endpoint: peer?.mongo_endpoint,
        mongo_port: peer?.mongo_port,
      }))
    : undefined;

  return {
    atomdb_type: section.atomdb_type ?? null,
    ...(peers ? { remote_peers: peers } : {}),
  };
}

export function useSidebarAtomdbConfig() {
  const [atomdb, setAtomdb] = useState(null);
  const [atomdbType, setAtomdbType] = useState(null);

  const reloadAtomdbConfig = useCallback(async () => {
    const defaults = await getConfigDefaults();
    const section = sidebarAtomdb(defaults?.content?.atomdb);
    setAtomdb(section);
    setAtomdbType(section?.atomdb_type ?? null);
    return section;
  }, []);

  useEffect(() => {
    let active = true;

    const reload = () => {
      reloadAtomdbConfig().catch((error) => {
        console.error("Failed to load AtomDB config for sidebar:", error);
        if (!active) return;
        setAtomdb(null);
        setAtomdbType(null);
      });
    };

    const onVisible = () => {
      if (document.visibilityState === "visible") reload();
    };

    reload();
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      active = false;
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [reloadAtomdbConfig]);

  return { atomdb, atomdbType, reloadAtomdbConfig };
}
