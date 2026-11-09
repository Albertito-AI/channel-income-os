# Channel Income OS

**Turn YouTube Studio CSV exports into an evidence-led income operating system. No API. No cloud upload. No vanity-metric theatre.**

Channel Income OS is a local-first Python tool for creators, educators, musicians and channel operators. It reads ordinary YouTube Studio CSV exports, calculates the real revenue gap, identifies videos that need discovery, retention or rights intervention, and produces a prioritised action queue.

> **Status:** public commercial preview, version 0.1.0. The software is useful now, but it does not guarantee views, distribution, monetisation eligibility or income.

## Why this exists

Most channel dashboards tell you what happened. Channel Income OS is built to answer the harder operating questions:

- Which videos have strong retention but weak discovery?
- Which videos attract views but lose the audience too early?
- Which revenue observations are too anomalous to forecast from?
- How many views would the income target require at the current effective RPM?
- Which experiments should be run first?
- Which videos must not be scaled because rights remain unresolved?
- Is the channel building qualified repeat viewing, or merely accumulating low-value traffic?

## What it produces

One command creates:

- `report.md`, an executive operating report;
- `dashboard.html`, a private browser dashboard;
- `action_queue.csv`, a ranked intervention queue;
- `scorecard.json`, structured output for further automation.

The software runs locally and sends no telemetry.

## Quick demonstration

Python 3.11 or later is required.

```bash
git clone https://github.com/Albertito-AI/channel-income-os.git
cd channel-income-os

python -m venv .venv

# macOS or Linux
. .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -e .
channel-income-os demo
```

Open:

```text
build/demo/dashboard.html
```

The included demonstration uses synthetic data. It does not disclose any real creator's analytics.

Repository preview files are included at:

- [`docs/demo/report.md`](docs/demo/report.md)
- [`docs/demo/index.html`](docs/demo/index.html)
- [`docs/demo/action_queue.csv`](docs/demo/action_queue.csv)

## Analyse your own export

Export a video-level table from YouTube Studio Advanced Mode, then run:

```bash
channel-income-os analyze \
  --videos "/path/to/videos.csv" \
  --summary "/path/to/channel_summary.csv" \
  --rights "/path/to/rights_registry.csv" \
  --target 10000 \
  --currency USD \
  --output build/my-channel
```

Only `--videos` is compulsory. If no channel summary is supplied, the program reconstructs aggregate values from the video table and places a warning in the report.

See [`docs/EXPORT_GUIDE.md`](docs/EXPORT_GUIDE.md) for the recommended export fields.

## Operating signals

The current engine classifies videos into seven evidence-led actions:

| Signal | Meaning |
|---|---|
| `RIGHTS_HOLD` | Do not scale or license until rights are cleared |
| `REVENUE_AUDIT` | High RPM on a weak sample; investigate before forecasting |
| `REPAIR_RETENTION` | Strong reach, weak audience hold |
| `IMPROVE_DISCOVERY` | Strong retention, weak reach |
| `SCALE_WINNER` | Strong reach and retention |
| `PACKAGING_TEST` | Sufficient impressions, weak click-through rate |
| `MONITOR` | No sufficiently strong intervention signal yet |

The thresholds are computed from the supplied channel, rather than pretending that one universal benchmark fits every audience and format.

## Evidence discipline

Channel Income OS is deliberately conservative:

- it does not buy or simulate views, subscribers, comments, likes or watch time;
- it does not automate spam, sub-for-sub or deceptive metadata;
- it separates evidence from projections;
- it treats anomalous RPM as an audit item;
- it supports a rights registry before deliberate scaling;
- it labels target calculations as operating scenarios, not forecasts;
- it keeps the creator's exports on the creator's computer.

## Evaluation and professional use

Explore the synthetic demonstration and inspect the methods before deciding
whether Channel Income OS fits your workflow. Noncommercial research, education,
testing and evaluation are permitted under the
[PolyForm Noncommercial License 1.0.0](LICENSE).

Commercial use requires a separate written licence. Creator, agency and
institutional enquiries can be scoped around the channels, users and intended
workflow. A commissioned review of authorised Studio exports may include a
reviewed action queue and implementation note, with its scope agreed in advance.

[**Discuss a licence or channel review**](https://www.alberttansinhon.com/#contact)
with a short, non-confidential description of your intended use. Commercial terms
are agreed privately. See [licensing scope and boundaries](COMMERCIAL.md).

## Licence

Copyright © 2026 Albert Tan Sin Hon.

- Noncommercial use: [PolyForm Noncommercial License 1.0.0](LICENSE).
- Commercial use: requires a separate written commercial licence from the copyright holder.
- Third-party names and trademarks remain the property of their respective owners.

## Disclaimer

Channel Income OS is independent software. It is not affiliated with, endorsed by or sponsored by YouTube or Google. YouTube is a trademark of Google LLC.

This software provides analytical and operational assistance. It is not financial, legal, tax or investment advice. Actual results depend on content quality, audience demand, rights, platform decisions, advertiser demand, geography, seasonality and many other factors outside the software's control.
