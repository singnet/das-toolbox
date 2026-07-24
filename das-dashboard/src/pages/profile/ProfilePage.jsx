import { useEffect, useState } from "react";
import { Box, Button, Paper, TextField, Typography } from "@mui/material";
import { PageContainer } from "./profilepage.styled";
import { useToast } from "../../components/global_providers/ToastProvider";
import { createProfile, getProfile } from "../../api/ProfileAPI";
import { extractErrorDetails } from "../../api/APIUtils";
import { credentialUsernameField } from "../../utils/credentialFieldProps";

export default function ProfilePage() {
  const { showToast } = useToast();
  const [form, setForm] = useState({ sshUsername: "", sshKeyFile: null });

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const profile = await getProfile();
      setForm(prev => ({ ...prev, sshUsername: profile?.profile_username || "" }));
    } catch (err) {
      console.error(err);
      showToast({ message: "Failed to load profile.", severity: "error", details: extractErrorDetails(err) });
    }
  }

  function verifyForm(form) {
    const errors = [];
    const invalidUserChars = /[^a-zA-Z0-9._-]/g;

    if (form.sshUsername.length < 3 || form.sshUsername.toLowerCase() === "root" || invalidUserChars.test(form.sshUsername)) {
      errors.push("SSH Username must have at least 3 characters and cannot contain invalid characters.");
    }
    if (!form.sshKeyFile) {
      errors.push("SSH Key File is required.");
    }
    return errors;
  }

  function handleChange(field) {
    return (event) => {
      setForm(prev => ({ ...prev, [field]: event.target.value }));
    };
  }

  function handleFileSelect(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setForm(prev => ({ ...prev, sshKeyFile: file }));
  }

  async function handleSave() {
    const errors = verifyForm(form);
    if (errors.length > 0) {
      showToast({ message: errors.join(" "), severity: "error" });
      return;
    }

    try {
      await createProfile(form);
      showToast({ message: "Profile saved successfully.", severity: "success" });
      await loadProfile();
    } catch (err) {
      console.error(err);
      showToast({ message: "Failed to save profile.", severity: "error", details: extractErrorDetails(err) });
    }
  }

  return (
    <PageContainer>
      <Paper elevation={2} sx={{ width: "100%", maxWidth: 520, p: 4, borderRadius: 3 }}>
        <Typography variant="h5" fontWeight={700} mb={3}>SSH Profile</Typography>

        <Box
          component="form"
          autoComplete="off"
          display="flex"
          flexDirection="column"
          gap={3}
          onSubmit={(event) => event.preventDefault()}
        >
          <TextField
            label="SSH Username"
            value={form.sshUsername}
            onChange={handleChange("sshUsername")}
            fullWidth
            {...credentialUsernameField}
          />
          <TextField label="SSH Key File" value={form.sshKeyFile?.name || ""} fullWidth disabled />

          <Button variant="outlined" component="label">
            Select SSH Key File
            <input type="file" hidden onChange={handleFileSelect} />
          </Button>

          <Typography fontSize={10} textAlign="center">
            Tip: Hidden folders can be revealed with Ctrl + H on Linux or Command + Shift + . on macOS.
          </Typography>

          <Button variant="contained" onClick={handleSave}>Save Profile</Button>
        </Box>
      </Paper>
    </PageContainer>
  );
}