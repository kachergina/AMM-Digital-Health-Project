"""Command-line demo for the AMM Digital System simulator (simulation only).

Run it with:

    python3 -m digital_system.demo

Optional arguments:
    --scenario normal|fever|low_spo2|tachycardia|critical
    --count N     number of readings to print (default 5)
    --interval S  seconds between readings (default 1.0)

Every value printed is artificially generated software output for demonstration
only. This script never reads from, or controls, a real medical device.
"""

import argparse
import os
import sys
import time

# Make the sibling packages importable whether this is launched as
# `python3 -m digital_system.demo` (from the project root) or
# `python3 -m demo` (from inside the digital_system/ folder).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.sensors import generate_reading, SCENARIOS
from processing.analyze import analyze_reading


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="AMM simulator CLI demo (simulated data only)."
    )
    parser.add_argument("--scenario", default="normal", choices=SCENARIOS)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args(argv)

    print("AMM Digital System - CLI demo (SIMULATED DATA, not a real medical device)")
    print("Scenario: %s | readings: %d\n" % (args.scenario, args.count))

    for i in range(args.count):
        reading = generate_reading(args.scenario)
        result = analyze_reading(reading)
        print("Reading %d  [%s]" % (i + 1, reading["timestamp"]))
        for vital in result["vitals"]:
            print("  %-22s %8s %-6s  %s" % (
                vital["label"], vital["value"], vital["unit"], vital["status"]))
        print("  Overall status: %s\n" % result["overall_status"])
        if i + 1 < args.count:
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
