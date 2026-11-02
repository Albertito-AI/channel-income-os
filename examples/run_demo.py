from pathlib import Path

from channel_income_os.cli import main

raise SystemExit(main(["demo", "--output", str(Path("build") / "demo")]))
