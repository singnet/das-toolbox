export function isCliResponseDecodeError(err) {
  const data = err?.response?.data;
  return err?.response?.status === 422 && data?.status === "notice";
}

export function extractErrorMessage(err, fallback = "An unexpected error occurred.") {
  if (!err) {
    return fallback;
  }

  if (err.response) {
    const data = err.response.data;

    if (typeof data === "string") {
      return fallback;
    }

    if (data?.message) {
      return data.message;
    }
  }

  if (err.message) {
    return err.message;
  }

  return fallback;
}

export function extractErrorDetails(err) {
  if (!err) {
    return null;
  }

  if (err.response) {
    const data = err.response.data;

    if (typeof data === "string") {
      return data;
    }

    if (data?.exceptionMessage) {
      return data.exceptionMessage;
    }

    if (data?.detail) {
      return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    }

    return null;
  }

  if (err.request) {
    return "Unable to connect to the server. Server might be offline or container crashed.";
  }

  if (err.message) {
    return err.message;
  }

  return null;
}

export function getApiErrorSeverity(err) {
  return isCliResponseDecodeError(err) ? "warning" : "error";
}

export function extractApiError(err, fallbackMessage = "An unexpected error occurred.") {
  return {
    message: extractErrorMessage(err, fallbackMessage),
    details: extractErrorDetails(err),
    severity: getApiErrorSeverity(err),
  };
}
