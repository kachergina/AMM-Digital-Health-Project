"""Tests for the AMM Digital System CLI demo (simulation only).

The demo is launched the same way a user would run it, from the project root,
so this also verifies that `python3 -m digital_system.demo` resolves correctly.
"""

import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_cli_demo_runs_with_scenario():
    result = subprocess.run(
        [sys.executable, "-m", "digital_system.demo",
         "--scenario", "fever", "--count", "2", "--interval", "0"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "SIMULATED" in result.stdout
    assert "Overall status" in result.stdout
    assert "Scenario: fever" in result.stdout


def test_cli_demo_critical_scenario_reports_review():
    result = subprocess.run(
        [sys.executable, "-m", "digital_system.demo",
         "--scenario", "critical", "--count", "1", "--interval", "0"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "REVIEW" in result.stdout
