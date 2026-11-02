# Methodology

## Observed values

The engine preserves observed views, watch hours, impressions, click-through rate, average view duration and estimated revenue from the supplied exports.

## Effective RPM

```text
effective RPM = estimated revenue / views × 1,000
```

When a trusted channel summary is supplied, target mathematics uses the summary effective RPM.

## Retention proxy

```text
retention ratio = average view duration / video duration
```

This is a coarse proxy. It is not a substitute for the audience-retention curve.

## Channel-relative thresholds

The engine uses the supplied channel's quartiles rather than imposing a universal benchmark:

- high reach: views at or above the 75th percentile;
- low reach: views at or below the 25th percentile;
- high retention: retention at or above the 75th percentile;
- low retention: retention at or below the 25th percentile.

This makes the queue useful across differently sized channels while preserving the need for human judgment.

## Revenue anomaly

A low-view video whose effective RPM is at or above the channel's 95th percentile is treated as an audit candidate. The system does not extrapolate from it.

## Concentration

The report compares the view and revenue shares of the ten highest-view videos. A catalogue can have strong reach concentration without corresponding revenue concentration.

## Limits

- Exported rows may be capped.
- Some fields are unavailable for Shorts or particular account types.
- Estimated revenue can change after adjustment.
- Retention ratio hides the shape of the retention curve.
- Percentile classification is prioritisation, not causal inference.
- The tool cannot know whether a title or thumbnail caused a result without a controlled test.
