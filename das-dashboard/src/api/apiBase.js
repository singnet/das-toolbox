export function resolveHttpBaseUrl() {
  const configured = import.meta.env.VITE_API_BASE_URL;
  if (configured) {
    return configured.replace(/\/$/, "");
  }

  return `${window.location.protocol}//${window.location.hostname}:8000`;
}

export function resolveWsBaseUrl() {
  const url = new URL(resolveHttpBaseUrl());
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.origin;
}
