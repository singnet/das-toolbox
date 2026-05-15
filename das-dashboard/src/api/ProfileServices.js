import axios from "axios";
import api from "./AxiosBaseClient";

export async function createProfile(form) {
  const data = new FormData();

  data.append("sshUsername", form.sshUsername);
  data.append("sshKeyFile", form.sshKeyFile);

  const response = await api.post("/dashboard/profile", data);

  return response.data;
}