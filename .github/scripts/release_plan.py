"""Decide whether a verified build represents a new release."""
import os
import re
import subprocess
import tomllib
from pathlib import Path


def previous_version(before):
    if not re.fullmatch(r"[0-9a-f]{40}", before):
        raise ValueError("The push event must identify its previous commit")
    if before == "0" * 40:
        return None
    # ls-tree succeeds with no entries when the package is first introduced.
    # An unavailable base commit must stop publication.
    if not subprocess.check_output(["git", "ls-tree", before, "--", "pyproject.toml"]):
        return None
    manifest = subprocess.check_output(
        ["git", "show", f"{before}:pyproject.toml"], encoding="utf-8"
    )
    return tomllib.loads(manifest)["project"]["version"]


def should_publish(version, event, ref, before, requested):
    if event == "push":
        publish = previous_version(before) != version
    elif event == "workflow_dispatch":
        publish = requested
    else:
        raise ValueError(f"Unexpected release workflow event: {event}")
    if publish and ref != "refs/heads/main":
        raise ValueError("Publication requires the main branch")
    return publish


def main():
    with Path("pyproject.toml").open("rb") as manifest:
        version = tomllib.load(manifest)["project"]["version"]
    publish = should_publish(
        version, os.environ["GITHUB_EVENT_NAME"], os.environ["GITHUB_REF"],
        os.environ.get("BEFORE_SHA", ""), os.environ.get("REQUEST_PUBLICATION") == "true",
    )
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
        print(f"tag=v{version}", file=output)
        print(f"publish={str(publish).lower()}", file=output)
    if publish:
        print(f"Preparing to publish v{version}.")
    else:
        print(f"Verified the v{version} build. No new release was requested.")


if __name__ == "__main__":
    main()
