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
      return typeof data.message === "string"
        ? data.message
        : JSON.stringify(data.message);
    }

    if (data?.error) {
      return typeof data.error === "string" ? data.error : JSON.stringify(data.error);
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

    if (data?.error) {
      return typeof data.error === "string" ? data.error : JSON.stringify(data.error);
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

export function extractApiError(err, fallbackMessage = "An unexpected error occurred.") {
  return {
    message: extractErrorMessage(err, fallbackMessage),
    details: extractErrorDetails(err),
    severity: "error",
  };
}
