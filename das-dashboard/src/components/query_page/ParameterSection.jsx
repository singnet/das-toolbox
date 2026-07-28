import {
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  Switch,
  TextField
} from "@mui/material";
import { useQueryParameters } from "../../hooks/useQueryParameters";
import {
  ParameterDivider,
  ParameterFieldGrid,
  ParameterLimitField,
  ParameterSectionBody,
  ParameterSectionRoot,
  ParameterSwitchStack,
  SliderLabel,
  SliderLabelRow,
  SliderRow,
  SliderValue,
  paletteQuery
} from "../../pages/query/querypage.styled";

const ATTENTION_OPTIONS = [
  { value: 0, label: "None" },
  { value: 1, label: "Handles" },
  { value: 2, label: "Variables" },
  { value: 3, label: "Handles and variables" }
];

const BASE_QUERY_SWITCHES = [
  { key: "unique_assignment_flag", label: "Unique assignment" },
  { key: "use_link_template_cache", label: "Use link template cache" },
  { key: "populate_metta_mapping", label: "Populate MeTTa mapping" },
  { key: "allow_incomplete_chain_path", label: "Allow incomplete chain path" }
];

const QUERY_SWITCHES = [
  { key: "positive_importance_flag", label: "Only answers with non-zero STI" },
  { key: "disregard_importance_flag", label: "Disregard STI" },
  { key: "unique_value_flag", label: "Unique value" },
  { key: "count_flag", label: "Count only" }
];

const fieldSx = {
  "& .MuiOutlinedInput-root": {
    backgroundColor: paletteQuery.surface,
    fontSize: 13
  },
  "& .MuiInputLabel-root": {
    fontSize: 13
  }
};

const switchSx = {
  mx: 0,
  width: "100%",
  justifyContent: "space-between",
  ml: 0,
  mr: 0,
  "& .MuiFormControlLabel-label": {
    fontSize: 13,
    color: paletteQuery.textPrimary
  }
};

export default function ParameterSection() {
  const {
    attentionUpdate,
    setAttentionUpdate,
    attentionCorrelation,
    setAttentionCorrelation,
    attentionFocusStrictness,
    setAttentionFocusStrictness,
    maxBundleSize,
    setMaxBundleSize,
    limitAnswersEnabled,
    setLimitAnswersEnabled,
    maxAnswersLimit,
    setMaxAnswersLimit,
    switches,
    updateSwitch
  } = useQueryParameters();

  const limitValueInvalid =
    limitAnswersEnabled &&
    (!Number.isInteger(maxAnswersLimit) || maxAnswersLimit < 1);

  return (
    <ParameterSectionRoot>
      <ParameterSectionBody>
        <ParameterFieldGrid>
          <FormControl size="small" fullWidth sx={fieldSx}>
            <InputLabel>Attention update</InputLabel>
            <Select
              label="Attention update"
              value={attentionUpdate}
              onChange={(event) => setAttentionUpdate(event.target.value)}
            >
              {ATTENTION_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" fullWidth sx={fieldSx}>
            <InputLabel>Attention correlation</InputLabel>
            <Select
              label="Attention correlation"
              value={attentionCorrelation}
              onChange={(event) => setAttentionCorrelation(event.target.value)}
            >
              {ATTENTION_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </ParameterFieldGrid>

        <SliderRow>
          <SliderLabelRow>
            <SliderLabel>Attention focus strictness</SliderLabel>
            <SliderValue>{attentionFocusStrictness.toFixed(1)}</SliderValue>
          </SliderLabelRow>
          <Slider
            size="small"
            value={attentionFocusStrictness}
            onChange={(_, value) => setAttentionFocusStrictness(value)}
            min={0}
            max={1}
            step={0.1}
            sx={{
              color: paletteQuery.accent,
              "& .MuiSlider-rail": { opacity: 0.35 }
            }}
          />
        </SliderRow>

        <ParameterFieldGrid>
          <TextField
            label="Max bundle size"
            type="number"
            size="small"
            value={maxBundleSize}
            onChange={(event) => setMaxBundleSize(Number(event.target.value))}
            fullWidth
            inputProps={{ min: 1, step: 1 }}
            sx={fieldSx}
          />
        </ParameterFieldGrid>

        <ParameterLimitField>
          <FormControlLabel
            sx={switchSx}
            labelPlacement="start"
            control={
              <Switch
                size="small"
                checked={limitAnswersEnabled}
                onChange={(event) => setLimitAnswersEnabled(event.target.checked)}
                sx={{
                  "& .MuiSwitch-switchBase.Mui-checked": {
                    color: paletteQuery.accent
                  },
                  "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
                    backgroundColor: paletteQuery.accent
                  }
                }}
              />
            }
            label="Limit the number of answers"
          />

          <TextField
            label="Answer limit"
            type="number"
            size="small"
            value={maxAnswersLimit}
            disabled={!limitAnswersEnabled}
            error={limitValueInvalid}
            helperText={
              limitValueInvalid ? "Enter an integer greater than or equal to 1." : " "
            }
            onChange={(event) => {
              const parsed = Number.parseInt(event.target.value, 10);
              if (!Number.isNaN(parsed)) {
                setMaxAnswersLimit(parsed);
              }
            }}
            inputProps={{ min: 1, step: 1 }}
            fullWidth
            sx={fieldSx}
          />
        </ParameterLimitField>

        <ParameterSwitchStack>
          {BASE_QUERY_SWITCHES.map((item) => (
            <FormControlLabel
              key={item.key}
              sx={switchSx}
              labelPlacement="start"
              control={
                <Switch
                  size="small"
                  checked={switches[item.key]}
                  onChange={(event) => updateSwitch(item.key, event.target.checked)}
                  sx={{
                    "& .MuiSwitch-switchBase.Mui-checked": {
                      color: paletteQuery.accent
                    },
                    "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
                      backgroundColor: paletteQuery.accent
                    }
                  }}
                />
              }
              label={item.label}
            />
          ))}
        </ParameterSwitchStack>

        <ParameterDivider />

        <ParameterSwitchStack>
          {QUERY_SWITCHES.map((item) => (
            <FormControlLabel
              key={item.key}
              sx={switchSx}
              labelPlacement="start"
              control={
                <Switch
                  size="small"
                  checked={switches[item.key]}
                  onChange={(event) => updateSwitch(item.key, event.target.checked)}
                  sx={{
                    "& .MuiSwitch-switchBase.Mui-checked": {
                      color: paletteQuery.accent
                    },
                    "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
                      backgroundColor: paletteQuery.accent
                    }
                  }}
                />
              }
              label={item.label}
            />
          ))}
        </ParameterSwitchStack>
      </ParameterSectionBody>
    </ParameterSectionRoot>
  );
}
