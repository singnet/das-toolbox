import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { getQueryParamDefaults } from "../api/QueryAPI";
import { buildQueryParameters } from "../utils/queryParameters";

const QueryParametersContext = createContext(null);

const SWITCH_KEYS = [
  "unique_assignment_flag",
  "use_link_template_cache",
  "populate_metta_mapping",
  "use_metta_as_query_tokens",
  "allow_incomplete_chain_path",
  "positive_importance_flag",
  "disregard_importance_flag",
  "unique_value_flag",
  "count_flag"
];

function switchesFromDefaults(defaults) {
  return SWITCH_KEYS.reduce((accumulator, key) => {
    accumulator[key] = Boolean(defaults[key]);
    return accumulator;
  }, {});
}

export function QueryParametersProvider({ children }) {
  const [attentionUpdate, setAttentionUpdateState] = useState(0);
  const [attentionCorrelation, setAttentionCorrelationState] = useState(0);
  const [attentionFocusStrictness, setAttentionFocusStrictnessState] = useState(0);
  const [maxBundleSize, setMaxBundleSizeState] = useState(1000);
  const [limitAnswersEnabled, setLimitAnswersEnabledState] = useState(false);
  const [maxAnswersLimit, setMaxAnswersLimitState] = useState(1);
  const [switches, setSwitchesState] = useState(() => switchesFromDefaults({}));
  const queryRunParametersRef = useRef({});

  const setQueryRunParameter = useCallback((key, value) => {
    queryRunParametersRef.current = {
      ...queryRunParametersRef.current,
      [key]: value
    };
  }, []);

  const consumeQueryRunParameters = useCallback(() => {
    const pending = { ...queryRunParametersRef.current };
    queryRunParametersRef.current = {};
    return pending;
  }, []);

  const applyParameterDefaults = useCallback((defaults) => {
    if (!defaults || typeof defaults !== "object") {
      return;
    }

    queryRunParametersRef.current = {};
    setAttentionUpdateState(defaults.attention_update ?? 0);
    setAttentionCorrelationState(defaults.attention_correlation ?? 0);
    setAttentionFocusStrictnessState(defaults.attention_focus_strictness ?? 0);
    setMaxBundleSizeState(defaults.max_bundle_size ?? 1000);

    const maxAnswers = defaults.max_answers ?? 0;
    setLimitAnswersEnabledState(maxAnswers > 0);
    setMaxAnswersLimitState(maxAnswers > 0 ? maxAnswers : 1);
    setSwitchesState(switchesFromDefaults(defaults));
  }, []);

  useEffect(() => {
    let cancelled = false;

    getQueryParamDefaults()
      .then((defaults) => {
        if (!cancelled) {
          applyParameterDefaults(defaults);
        }
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [applyParameterDefaults]);

  const setAttentionUpdate = useCallback(
    (value) => {
      const normalized = Number(value);
      setAttentionUpdateState(normalized);
      setQueryRunParameter("attention_update", normalized);
    },
    [setQueryRunParameter]
  );

  const setAttentionCorrelation = useCallback(
    (value) => {
      const normalized = Number(value);
      setAttentionCorrelationState(normalized);
      setQueryRunParameter("attention_correlation", normalized);
    },
    [setQueryRunParameter]
  );

  const setAttentionFocusStrictness = useCallback(
    (value) => {
      setAttentionFocusStrictnessState(value);
      setQueryRunParameter("attention_focus_strictness", value);
    },
    [setQueryRunParameter]
  );

  const setMaxBundleSize = useCallback(
    (value) => {
      const normalized = Number(value);
      setMaxBundleSizeState(normalized);
      setQueryRunParameter("max_bundle_size", normalized);
    },
    [setQueryRunParameter]
  );

  const setLimitAnswersEnabled = useCallback(
    (enabled) => {
      setLimitAnswersEnabledState(enabled);
      setQueryRunParameter("max_answers", enabled ? maxAnswersLimit : 0);
    },
    [maxAnswersLimit, setQueryRunParameter]
  );

  const setMaxAnswersLimit = useCallback(
    (value) => {
      setMaxAnswersLimitState(value);
      if (limitAnswersEnabled) {
        setQueryRunParameter("max_answers", value);
      }
    },
    [limitAnswersEnabled, setQueryRunParameter]
  );

  const updateSwitch = useCallback(
    (key, checked) => {
      setSwitchesState((previous) => ({ ...previous, [key]: checked }));
      setQueryRunParameter(key, checked);
    },
    [setQueryRunParameter]
  );

  const collectParameters = useCallback(
    () =>
      buildQueryParameters({
        attentionUpdate,
        attentionCorrelation,
        attentionFocusStrictness,
        maxBundleSize,
        limitAnswersEnabled,
        maxAnswersLimit,
        switches
      }),
    [
      attentionUpdate,
      attentionCorrelation,
      attentionFocusStrictness,
      maxBundleSize,
      limitAnswersEnabled,
      maxAnswersLimit,
      switches
    ]
  );

  const value = {
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
    updateSwitch,
    consumeQueryRunParameters,
    collectParameters,
    isCountOnly: switches.count_flag
  };

  return (
    <QueryParametersContext.Provider value={value}>
      {children}
    </QueryParametersContext.Provider>
  );
}

export function useQueryParameters() {
  const context = useContext(QueryParametersContext);
  if (!context) {
    throw new Error("useQueryParameters must be used inside QueryParametersProvider");
  }
  return context;
}
