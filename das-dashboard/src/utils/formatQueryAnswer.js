export function formatQueryAnswer(answer) {
  if (answer?.count_only) {
    return String(answer.count ?? "");
  }

  return JSON.stringify(
    {
      handles: answer.handles,
      metta: answer.metta,
      assignment: answer.assignment
    },
    null,
    2
  );
}
