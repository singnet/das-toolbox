const BUCKET_COUNT = 30;
const WINDOW_MS = 60_000;

export function buildFrequencyHistogram(answers) {
  const labels = Array.from({ length: BUCKET_COUNT }, (_, index) => String(index + 1));

  if (answers.length === 0) {
    return {
      counts: Array(BUCKET_COUNT).fill(0),
      labels,
      scaleLabel: "1 minute",
      maxCount: 1
    };
  }

  const startTime = answers[0].receivedAt;
  const bucketSize = WINDOW_MS / BUCKET_COUNT;
  const counts = Array(BUCKET_COUNT).fill(0);

  for (const answer of answers) {
    const offset = answer.receivedAt - startTime;
    if (offset < 0 || offset >= WINDOW_MS) {
      continue;
    }

    const index = Math.min(BUCKET_COUNT - 1, Math.floor(offset / bucketSize));
    counts[index] += 1;
  }

  return {
    counts,
    labels,
    scaleLabel: "1 minute",
    maxCount: Math.max(1, ...counts)
  };
}

export function buildStiChart(answers, maxBars = 30) {
  if (answers.length === 0) {
    return {
      values: [],
      labels: [],
      maxValue: 1,
      nonZeroCount: 0
    };
  }

  const slice = answers.slice(-maxBars);
  const offset = answers.length - slice.length;
  const values = slice.map((answer) => answer.importance);
  const labels = slice.map((_, index) => String(offset + index + 1));
  const nonZeroCount = values.filter((value) => value !== 0).length;

  return {
    values,
    labels,
    maxValue: Math.max(0.01, ...values),
    nonZeroCount
  };
}
