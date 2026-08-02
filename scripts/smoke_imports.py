#!/usr/bin/env python3
"""Verify core application modules import cleanly on Python 3.12."""

import importlib
import sys

MODULES = [
    "src.settings",
    "src.core.models",
    "src.core.api",
    "src.api.app",
    "src.database.db",
    "src.database.data_ingestion",
    "src.auth.auth",
    "src.agents.base_agent",
    "src.mcp.orchestrator_server",
    "src.mcp.planner_server",
    "src.mcp.tutor_server",
    "src.mcp.critic_server",
    "src.mcp.notes_server",
]


def main() -> int:
    failed = []
    for module in MODULES:
        try:
            importlib.import_module(module)
            print(f"OK  {module}")
        except Exception as exc:
            print(f"FAIL {module}: {exc}")
            failed.append(module)

    if failed:
        print(f"\n{len(failed)} module(s) failed to import.")
        return 1

    print(f"\nAll {len(MODULES)} modules imported successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
