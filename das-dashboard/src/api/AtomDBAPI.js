import api from "./AxiosBaseClient";

export async function uploadMettaFile(host, force_overwrite, file) {
  const formData = new FormData();
  formData.append("knowledge_base_file", file);

  const response = await api.post(
    "/services/atomdb/metta/upload",
    formData,
    {
      params: { host, force_overwrite },
      headers: {
        "Content-Type": "multipart/form-data"
      }
    }
  );

  return response.data;
}

export async function loadMettaFile(host, mettaFilePath) {
  
  const response = await api.post(
    "/services/atomdb/metta/load",
    null,
    {
      params: {
        host,
        metta_file_path: mettaFilePath
      }
    }
  );

  return response.data;
}