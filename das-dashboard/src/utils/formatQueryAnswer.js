function flattenNestedValues(values) {
  if (!Array.isArray(values) || values.length === 0) {
    return [];
  }

  return values.flatMap((entry) =>
    Array.isArray(entry) ? entry.map(String) : [String(entry)]
  );
}

function formatHandles(handles) {
  const flattened = flattenNestedValues(handles);
  return flattened.length > 0 ? flattened.join(" | ") : "(no handles)";
}

function formatMettaContent(answer) {
  const expressionLines = flattenNestedValues(answer.metta_expressions ?? answer.metta);
  const assignmentMetta = answer.assignment_metta ?? {};
  const assignmentLines = Object.entries(assignmentMetta).map(
    ([key, value]) => `${key}: ${value}`
  );

  const parts = [...expressionLines, ...assignmentLines];
  return parts.length > 0 ? parts.join("\n") : "(no metta)";
}

export function formatQueryAnswer(answer, { preferMetta = false } = {}) {
  if (answer?.count_only) {
    return String(answer.count ?? "");
  }

  if (preferMetta) {
    const mettaLabel = formatMettaContent(answer);
    if (mettaLabel !== "(no metta)") {
      return mettaLabel;
    }
  }

  return formatHandles(answer.handles);
}
