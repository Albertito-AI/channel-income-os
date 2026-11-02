# Security and Privacy

## Local-first design

The core tool reads local CSV files and writes local reports. It makes no network request, contains no telemetry and needs no Google or YouTube API credential.

## Never commit real analytics

Public repositories should contain only synthetic or expressly publishable data. Real exports may disclose revenue, geography, audience composition, commercial strategy and unpublished content identifiers.

Recommended private structure:

```text
private-input/
  videos.csv
  channel_summary.csv
  rights_registry.csv

private-output/
  report.md
  dashboard.html
  action_queue.csv
  scorecard.json
```

Add private input and output folders to `.gitignore`.

## Vulnerability reports

Do not post a security vulnerability containing personal data or credentials in a public issue. Email `travelingbert@gmail.com` with the subject `Channel Income OS Security`.

## Supported version

Security corrections presently target the latest 0.x release only.
