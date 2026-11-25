# Public Repository Publishing Checklist

1. Create a public repository named `channel-income-os`.
2. Do not initialise it with a README, licence or `.gitignore`.
3. Push this repository package to `main`.
4. Confirm GitHub Actions passes.
5. Add the repository description:
   `API-free, local-first YouTube Studio CSV analysis and creator revenue operations.`
6. Add topics:
   `youtube-analytics`, `creator-economy`, `revenue`, `csv`, `python`, `dashboard`
7. Enable Issues.
8. Enable Sponsorships after confirming the funding destination.
9. Optionally enable GitHub Pages from `docs/` for the synthetic demo.
10. To publish a new version, update the version in `pyproject.toml` and the release notes together on `main`. The release workflow tests and builds every matching push, then publishes only on a version change. A manual run verifies by default. Select **Publish** on `main` to retry a version that has not yet been published. Existing releases and their assets are immutable.
11. Never publish real creator exports, credentials, private reports or payment identifiers.
