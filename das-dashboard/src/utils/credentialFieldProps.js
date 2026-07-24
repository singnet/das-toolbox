const autofillOffInput = {
  autoComplete: "off",
  "data-form-type": "other",
  "data-lpignore": "true",
  "data-1p-ignore": "true"
};

const unlockOnFocusInput = {
  readOnly: true,
  onFocus: (event) => {
    event.target.readOnly = false;
  }
};

export const disableAutofillField = {
  autoComplete: "off",
  slotProps: {
    htmlInput: {
      ...autofillOffInput
    }
  }
};

export const credentialUsernameField = {
  autoComplete: "off",
  slotProps: {
    htmlInput: {
      ...autofillOffInput,
      ...unlockOnFocusInput
    }
  }
};

export const credentialPasswordField = {
  autoComplete: "off",
  slotProps: {
    htmlInput: {
      // Avoid "new-password" — Chrome treats that as sign-up and offers to generate.
      autoComplete: "one-time-code",
      "data-form-type": "other",
      "data-lpignore": "true",
      "data-1p-ignore": "true",
      ...unlockOnFocusInput
    }
  }
};
