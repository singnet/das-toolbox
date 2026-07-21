import { createContext, useCallback, useContext, useRef, useState } from "react";
import { buildQueryParameters } from "../utils/queryParameters";

const QueryParametersContext = createContext(null);

function serializeParameters(params) {
  return JSON.stringify(params);
}

const INITIAL_SWITCH_STATE = {
  unique_assignment_flag: false,
  use_link_template_cache: false,
  populate_metta_mapping: true,
  use_metta_as_query_tokens: true,
  allow_incomplete_chain_path: false,
  positive_importance_flag: false,
  disregard_importance_flag: false,
  unique_value_flag: false,
  count_flag: false
};

export function QueryParametersProvider({ children }) {
  const [attentionUpdate, setAttentionUpdate] = useState(0);
  const [attentionCorrelation, setAttentionCorrelation] = useState(0);
  const [attentionFocusStrictness, setAttentionFocusStrictness] = useState(0);
  const [maxBundleSize, setMaxBundleSize] = useState(1000);
  const [limitAnswersEnabled, setLimitAnswersEnabled] = useState(false);
  const [maxAnswersLimit, setMaxAnswersLimit] = useState(1);
  const [switches, setSwitches] = useState(INITIAL_SWITCH_STATE);
  const lastAppliedParametersRef = useRef(null);

  const collectParameters = () =>
    buildQueryParameters({
      attentionUpdate,
      attentionCorrelation,
      attentionFocusStrictness,
      maxBundleSize,
      limitAnswersEnabled,
      maxAnswersLimit,
      switches
    });

  const needsParameterApply = useCallback((params) => {
    return serializeParameters(params) !== lastAppliedParametersRef.current;
  }, []);

  const markParametersApplied = useCallback((params) => {
    lastAppliedParametersRef.current = serializeParameters(params);
  }, []);

  const updateSwitch = (key, checked) => {
    setSwitches((previous) => ({ ...previous, [key]: checked }));
  };

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
    collectParameters,
    needsParameterApply,
    markParametersApplied,
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
