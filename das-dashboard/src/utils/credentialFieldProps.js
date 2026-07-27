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
      name: "das-config-user",
      ...unlockOnFocusInput
    }
  }
};

// Use masked text instead of type="password" so browsers do not treat this as a login form.
export const credentialPasswordField = {
  type: "text",
  autoComplete: "off",
  sx: {
    "& .MuiInputBase-input": {
      WebkitTextSecurity: "disc",
      MozTextSecurity: "disc"
    }
  },
  slotProps: {
    htmlInput: {
      ...autofillOffInput,
      name: "das-config-secret",
      ...unlockOnFocusInput
    }
  }
};
