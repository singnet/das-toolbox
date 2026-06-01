export function extractErrorDetails(err) {
  if (!err) {
    return "Unknown error.";
  }

  if (err.response) {
    const data = err.response.data;

    if (typeof data === "string") {
      return data;
    }

    if (data?.message) {
      return data.message;
    }

    return JSON.stringify(data, null, 2);
  }

  if (err.request) {
    return `
    Unable to connect to the server.

    
    Possible causes:
    Server's container crashed and is offline;
    Wrong automatic port/ip assignment by uvicorn;
    Try checking the server's container logs for more information.
    `;
  }

  if (err.message) {
    return err.message;
  }

  return "Unexpected error.";
}