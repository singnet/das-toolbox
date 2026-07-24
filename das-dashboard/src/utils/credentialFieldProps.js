export const credentialUsernameField = {
  autoComplete: "off",
  slotProps: {
    htmlInput: {
      autoComplete: "off",
      "data-form-type": "other",
      "data-lpignore": "true",
      "data-1p-ignore": "true"
    }
  }
};

export const credentialPasswordField = {
  autoComplete: "new-password",
  slotProps: {
    htmlInput: {
      autoComplete: "new-password",
      "data-form-type": "other",
      "data-lpignore": "true",
      "data-1p-ignore": "true"
    }
  }
};
