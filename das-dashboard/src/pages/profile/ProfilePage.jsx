import { useState } from "react";
import {
  Box,
  Button,
  Paper,
  TextField,
  Typography,
} from "@mui/material";

import { PageContainer } from "./profilepage.styled";
import { useToast } from "../../components/global_providers/ToastProvider";
import { createProfile } from "./service/ProfileServices";

export default function ProfilePage() {
  const { showToast } = useToast();

  const [form, setForm] = useState({
    sshUsername: "",
    sshKeyFile: null,
  });

  const verifyForm = (form) => {
    const errors = [];

    const invalidUserChars = /[^a-zA-Z0-9._-]/g;

    if (
      form.sshUsername.length < 3 ||
      form.sshUsername.toLowerCase() === "root" ||
      invalidUserChars.test(form.sshUsername)
    ) {
      errors.push(
        "SSH Username must have at least 3 characters, cannot be 'root', and may only contain letters, numbers, '.', '_' or '-'."
      );
    }

    if (!form.sshKeyFile) {
      errors.push("SSH Key File is required.");
    }

    return errors;
  };

  const handleChange = (field) => (event) => {
    setForm((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setForm((prev) => ({
      ...prev,
      sshKeyFile: file,
    }));
  };

  const handleSave = async () => {
    const errors = verifyForm(form);

    if (errors.length > 0) {
      showToast(errors.join(" "), "error");
      return;
    }

    try {
      await createProfile(form);

      showToast("Profile saved successfully.", "success");
    } catch (error) {
      console.error(error.response?.data || error);
      showToast("Failed to save profile.", "error");
    }
  };

  return (
    <PageContainer>
      <Paper
        elevation={2}
        sx={{
          width: "100%",
          maxWidth: 520,
          p: 4,
          borderRadius: 3,
        }}
      >
        <Typography variant="h5" fontWeight={700} mb={3}>
          SSH Profile
        </Typography>

        <Box display="flex" flexDirection="column" gap={3}>
          <TextField
            label="SSH Username"
            value={form.sshUsername}
            onChange={handleChange("sshUsername")}
            fullWidth
          />

          <TextField
            label="SSH Key File"
            value={form.sshKeyFile?.name || ""}
            fullWidth
            disabled
          />

          <Button variant="outlined" component="label">
            Select SSH Key File
            <input
              type="file"
              hidden
              onChange={handleFileSelect}
            />
          </Button>

          <Typography fontSize={10} textAlign={"center"}>Tip: Keys in hidden folders can be revealed with 'Ctrl + H' on Linux or 'Command + Shift + .' on macOS.'</Typography>

          <Button variant="contained" onClick={handleSave}>
            Save Profile
          </Button>
        </Box>
      </Paper>
    </PageContainer>
  );
}