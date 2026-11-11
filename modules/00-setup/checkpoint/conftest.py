"""Prints the checkpoint as one line per acceptance criterion.

pytest's own output is kept for the details of a failure. This adds a short
summary at the end that reads like the module's spec.
"""

import re

import pytest

RESULTS = {}
LABELS = {"passed": "pass", "failed": "FAIL", "skipped": "skip"}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    finished = report.when == "call" or (report.when == "setup" and report.outcome != "passed")
    if not finished:
        return
    title = (item.function.__doc__ or item.name).strip().splitlines()[0]
    reason = ""
    if report.skipped and isinstance(report.longrepr, tuple):
        reason = report.longrepr[2].replace("Skipped: ", "")
    RESULTS[item.name] = (report.outcome, title, reason)


def pytest_terminal_summary(terminalreporter):
    def number(name):
        match = re.search(r"criterion_(\d+)", name)
        return int(match.group(1)) if match else 0

    terminalreporter.section("Checkpoint")
    for name in sorted(RESULTS, key=number):
        outcome, title, reason = RESULTS[name]
        line = f"{LABELS[outcome]}  {number(name)}. {title}"
        if reason:
            line += f" ({reason})"
        terminalreporter.write_line(line)
