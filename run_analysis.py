#!/usr/bin/env python3
"""Stock Analysis Tool - Command line interface.

Simple entry point for running stock analysis from the command line.
"""

import sys
from pathlib import Path

# Add src to path for development use
sys.path.insert(0, str(Path(__file__).parent / "src"))

from stock_analysis_tool import Config, run_analysis


def main() -> None:
    """Run stock analysis with default configuration."""
    try:
        cfg = Config()
        run_analysis(cfg)
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
