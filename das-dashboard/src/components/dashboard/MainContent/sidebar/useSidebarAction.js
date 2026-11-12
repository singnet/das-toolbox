import { useState } from "react";

import { useToast } from "../../../global_providers/ToastProvider";
import { extractApiError } from "../../../../api/APIUtils";

export function useSidebarAction({ onBusyChange, onActionComplete }) {
  const [busy, setBusy] = useState(false);
  const { showToast } = useToast();

  const run = async (action, successMessage, errorMessage) => {
    setBusy(true);
    onBusyChange?.(true);
    try {
      const completed = await action();
      if (completed === false) return;
      try {
        await onActionComplete?.();
      } catch (refreshError) {
        console.error("Failed to refresh sidebar status after action:", refreshError);
      }
      showToast({ message: successMessage, severity: "success" });
    } catch (error) {
      console.error(errorMessage, error);
      const { message, details, severity } = extractApiError(error, errorMessage);
      showToast({ message, severity, details });
    } finally {
      setBusy(false);
      onBusyChange?.(false);
    }
  };

  return { busy, run };
}
