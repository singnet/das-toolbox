import { useCallback, useEffect, useState } from "react";

import { getConfigDefaults } from "../api/ConfigAPI";

export function useSidebarAtomdbConfig() {
  const [atomdb, setAtomdb] = useState(null);
  const [atomdbType, setAtomdbType] = useState(null);

  const reloadAtomdbConfig = useCallback(async () => {
    const defaults = await getConfigDefaults();
    const section = defaults?.content?.atomdb ?? null;
    setAtomdb(section);
    setAtomdbType(section?.atomdb_type ?? null);
    return section;
  }, []);

  useEffect(() => {
    reloadAtomdbConfig().catch((error) => {
      console.error("Failed to load AtomDB config for sidebar:", error);
      setAtomdb(null);
      setAtomdbType(null);
    });
  }, [reloadAtomdbConfig]);

  return { atomdb, atomdbType, reloadAtomdbConfig };
}
