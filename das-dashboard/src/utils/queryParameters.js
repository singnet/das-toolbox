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
    attention_update: Math.trunc(Number(attentionUpdate) || 0),
    attention_correlation: Math.trunc(Number(attentionCorrelation) || 0),
    attention_focus_strictness: Number(attentionFocusStrictness) || 0,
    max_bundle_size: Math.max(0, Math.trunc(Number(maxBundleSize) || 0)),
    max_answers: limitAnswersEnabled
      ? Math.max(0, Math.trunc(Number(maxAnswersLimit) || 0))
      : 0,
    unique_assignment_flag: Boolean(switches.unique_assignment_flag),
    use_link_template_cache: Boolean(switches.use_link_template_cache),
    populate_metta_mapping: Boolean(switches.populate_metta_mapping),
    use_metta_as_query_tokens: Boolean(switches.use_metta_as_query_tokens),
    allow_incomplete_chain_path: Boolean(switches.allow_incomplete_chain_path),
    positive_importance_flag: Boolean(switches.positive_importance_flag),
    disregard_importance_flag: Boolean(switches.disregard_importance_flag),
    unique_value_flag: Boolean(switches.unique_value_flag),
    count_flag: Boolean(switches.count_flag)
  };
}
