const BUCKET_COUNT = 30;
const WINDOW_MS = 60_000;

export function buildFrequencyHistogram(answers) {
  const streamAnswers = answers.filter((answer) => !answer.count_only);
  const labels = Array.from({ length: BUCKET_COUNT }, (_, index) => String(index + 1));

  if (streamAnswers.length === 0) {
    return {
      counts: Array(BUCKET_COUNT).fill(0),
      labels,
      scaleLabel: "1 minute",
      maxCount: 1
    };
  }

  const startTime = streamAnswers[0].receivedAt;
  const bucketSize = WINDOW_MS / BUCKET_COUNT;
  const counts = Array(BUCKET_COUNT).fill(0);

  for (const answer of streamAnswers) {
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
  const stiAnswers = answers.filter((answer) => !answer.count_only);

  if (stiAnswers.length === 0) {
    return {
      values: [],
      labels: [],
      maxValue: 1,
      nonZeroCount: 0
    };
  }

  const slice = stiAnswers.slice(-maxBars);
  const offset = stiAnswers.length - slice.length;
  const values = slice.map((answer) => Number(answer.importance ?? 0));
  const labels = slice.map((_, index) => String(offset + index + 1));
  const nonZeroCount = values.filter((value) => value !== 0).length;

  return {
    values,
    labels,
    maxValue: Math.max(0.01, ...values),
    nonZeroCount
  };
}
