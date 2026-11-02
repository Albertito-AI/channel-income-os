# Export Guide

Channel Income OS deliberately works without an API.

## Recommended video-level export

In YouTube Studio:

1. Open **Analytics**.
2. Open **Advanced Mode** or **See More**.
3. Select the desired date range.
4. Use a video-level table.
5. Include as many of these fields as available:
   - Content or Video ID
   - Video title
   - Video publish time
   - Duration
   - Views
   - Watch time (hours)
   - Average view duration
   - Impressions
   - Impressions click-through rate
   - Estimated revenue
   - RPM
   - Estimated monetised playbacks
6. Export the current view as CSV.

Studio wording and available fields can differ by account, country, content type and product version. The importer recognises common spelling variants and currency-labelled revenue columns.

## Recommended summary file

Create a two-column CSV:

```csv
metric,value
period_start,2026-10-01
period_end,2026-10-28
subscribers,10000
views,50000
watch_hours,1200
estimated_revenue,150
impressions,400000
ctr,4.2
average_view_duration,0:02:15
returning_viewers,6500
new_viewers,19000
currency,USD
```

A summary is strongly recommended because Studio may cap a video table. The channel summary should control the aggregate baseline.

## Rights registry

Optional structure:

```csv
video_id,rights_status,notes
abc123,cleared,Creator owns master and composition.
def456,hold,Third-party sample not yet cleared.
```

Recognised blocking statuses are `hold`, `uncleared`, `disputed` and `blocked`.

## Data protection

Keep real exports outside a public repository. The supplied `sample_data` folder is synthetic.
