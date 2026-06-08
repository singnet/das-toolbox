export function extractErrorDetails(err) {
  if (!err) {
    return "Unknown error.";
  }

  if (err.response) {
    const data = err.response.data;

    if (typeof data === "string") {
      return data;
    }

    if (data?.exceptionMessage) {
      return `${data.message} Details: ${data.exceptionMessage}`;
    }

    if (data?.message) {
      return data.message;
    }

    return JSON.stringify(data, null, 2);
  }

  if (err.request) {
    return `Unable to connect to the server. Server might be offline or container crashed.`;
  }

  if (err.message) {
    return err.message;
  }

  return "Unexpected error.";
}