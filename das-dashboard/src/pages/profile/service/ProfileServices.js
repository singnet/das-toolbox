import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export async function createProfile(form) {
  const data = new FormData();

  data.append("sshUsername", form.sshUsername);
  data.append("sshKeyFile", form.sshKeyFile);

  const response = await api.post("/profile", data);

  return response.data;
}