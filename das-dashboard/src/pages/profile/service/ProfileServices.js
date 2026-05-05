import axios from "axios";

const api = axios.create({
    baseURL: "http://localhost:8000",
})

export async function createProfile(profileForm) {
  const response = await api.post(
    "/profile",
    profileForm
  );

  return response.data;
}