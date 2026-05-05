import { useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Paper,
  TextField,
  Typography,
} from "@mui/material";

import { PageContainer } from "./profilepage.styled";
import { useToast } from "../../components/global_providers/ToastProvider";
import { createProfile } from "./service/ProfileServices";

export default function ProfilePage() {
  const { showToast } = useToast();

  const [showRestartWarning, setShowRestartWarning] =
    useState(false);

  const [form, setForm] = useState({
    profileName: "",
    sshUsername: "",
    sshKeyPath: "",
  });

  const verifyForm = (form) => {
    const errors = [];

    const invalidUserChars = /[^a-zA-Z0-9._-]/g;
    const invalidPathChars = /[^a-zA-Z0-9/._~-]/g;

    if (form.profileName.length < 4) {
        errors.push(
        "Profile name must contain at least 4 characters."
        );
    }

    if (
        form.sshUsername.length < 3 ||
        form.sshUsername.toLowerCase() === "root" ||
        invalidUserChars.test(form.sshUsername)
    ) {
        errors.push(
        "SSH Username must have at least 3 characters, cannot be 'root', and may only contain letters, numbers, '.', '_' or '-'."
        );
    }

    if (
        form.sshKeyPath.length < 4 ||
        invalidPathChars.test(form.sshKeyPath)
    ) {
        errors.push(
        "SSH Key Path is invalid or contains unsupported characters."
        );
    }

    return errors;
    };

  const handleChange = (field) => (event) => {
    setForm((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleSave = async () => {
    const errors = verifyForm(form);

    if (errors.length > 0) {
      showToast(errors.join(" "), "error");
      return;
    }

    const isCustomPath =
      !form.sshKeyPath.startsWith("~/.ssh") &&
      !form.sshKeyPath.startsWith("/home");

    if (isCustomPath) {
      setShowRestartWarning(true);
    }

    try{
        await createProfile(form);

        showToast(
        "Profile saved successfully.",
        "success"
        );
    }

    catch (error) {
        showToast(
            "Failed to save profile.",
            "error"
        )
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
          Create SSH Profile
        </Typography>

        <Box
          display="flex"
          flexDirection="column"
          gap={3}
        >
          <TextField
            label="Profile Name"
            value={form.profileName}
            onChange={handleChange("profileName")}
            fullWidth
          />

          <TextField
            label="SSH Username"
            value={form.sshUsername}
            onChange={handleChange("sshUsername")}
            fullWidth
          />

          <TextField
            label="SSH Key Path"
            value={form.sshKeyPath}
            onChange={handleChange("sshKeyPath")}
            fullWidth
          />

          <Button
            variant="contained"
            onClick={handleSave}
          >
            Save Profile
          </Button>
        </Box>
      </Paper>

      <Dialog
        open={showRestartWarning}
        onClose={() =>
          setShowRestartWarning(false)
        }
      >
        <DialogTitle>
          Dashboard Restart Required
        </DialogTitle>

        <DialogContent>
          <Typography>
            The selected SSH key path is outside the
            default <strong>~/.ssh</strong> directory.
          </Typography>

          <Typography mt={2}>
            You will need to restart the dashboard stack
            before this profile can be used.

            (Ignore if not running the UI via containers)
          </Typography>
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() =>
              setShowRestartWarning(false)
            }
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </PageContainer>
  );
}