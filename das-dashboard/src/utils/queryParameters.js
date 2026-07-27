export function buildQueryParameters({
  attentionUpdate,
  attentionCorrelation,
  attentionFocusStrictness,
  maxBundleSize,
  limitAnswersEnabled,
  maxAnswersLimit,
  switches = {}
}) {
  return {
    attention_update: attentionUpdate,
    attention_correlation: attentionCorrelation,
    attention_focus_strictness: attentionFocusStrictness,
    max_bundle_size: maxBundleSize,
    max_answers: limitAnswersEnabled ? maxAnswersLimit : 0,
    unique_assignment_flag: switches.unique_assignment_flag,
    use_link_template_cache: switches.use_link_template_cache,
    populate_metta_mapping: switches.populate_metta_mapping,
    use_metta_as_query_tokens: switches.use_metta_as_query_tokens,
    allow_incomplete_chain_path: switches.allow_incomplete_chain_path,
    positive_importance_flag: switches.positive_importance_flag,
    disregard_importance_flag: switches.disregard_importance_flag,
    unique_value_flag: switches.unique_value_flag,
    count_flag: switches.count_flag
  };
}
