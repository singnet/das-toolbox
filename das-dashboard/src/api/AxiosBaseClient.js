import axios from "axios";
import { resolveHttpBaseUrl } from "./apiBase";

const api = axios.create({
  baseURL: resolveHttpBaseUrl(),
});

export default api