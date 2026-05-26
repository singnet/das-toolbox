import api from "./AxiosBaseClient";

export async function createProfile(form) {
  const data = new FormData();

  data.append("sshUsername", form.sshUsername);
  data.append("sshKeyFile", form.sshKeyFile);

  const response = await api.post("/profile", data);

  return response.data;
}

export async function getProfile() {
  const response = await api.get("/profile");

  return response.data;
}