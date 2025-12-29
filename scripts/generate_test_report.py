#!/usr/bin/env python3
"""
Generate test report from test results
"""

import json
import os
from pathlib import Path
from datetime import datetime

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
TEST_RESULTS_DIR = FRONTEND_DIR / "test-results"
COVERAGE_DIR = FRONTEND_DIR / "coverage"

def generate_report():
    """Generate HTML test report"""
    
    # Read test results if available
    results_file = TEST_RESULTS_DIR / "results.json"
    coverage_file = COVERAGE_DIR / "coverage-summary.json"
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "coverage": {},
    }
    
    if results_file.exists():
        with open(results_file) as f:
            test_data = json.load(f)
            report["total_tests"] = test_data.get("numTotalTests", 0)
            report["passed"] = test_data.get("numPassedTests", 0)
            report["failed"] = test_data.get("numFailedTests", 0)
            report["skipped"] = test_data.get("numPendingTests", 0)
    
    if coverage_file.exists():
        with open(coverage_file) as f:
            coverage_data = json.load(f)
            report["coverage"] = coverage_data.get("total", {})
    
    # Generate HTML report
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <div class="stat">
            <div>Total Tests</div>
            <div class="stat-value">{report["total_tests"]}</div>
        </div>
        <div class="stat">
            <div>Passed</div>
            <div class="stat-value passed">{report["passed"]}</div>
        </div>
        <div class="stat">
            <div>Failed</div>
            <div class="stat-value failed">{report["failed"]}</div>
        </div>
        <div class="stat">
            <div>Skipped</div>
            <div class="stat-value skipped">{report["skipped"]}</div>
        </div>
    </div>
    
    <h2>Coverage</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Percentage</th>
        </tr>
        <tr>
            <td>Statements</td>
            <td>{report["coverage"].get("statements", {}).get("pct", 0)}%</td>
        </tr>
        <tr>
            <td>Branches</td>
            <td>{report["coverage"].get("branches", {}).get("pct", 0)}%</td>
        </tr>
        <tr>
            <td>Functions</td>
            <td>{report["coverage"].get("functions", {}).get("pct", 0)}%</td>
        </tr>
        <tr>
            <td>Lines</td>
            <td>{report["coverage"].get("lines", {}).get("pct", 0)}%</td>
        </tr>
    </table>
    
    <p><small>Report generated at: {report["generated_at"]}</small></p>
</body>
</html>
"""
    
    # Write report
    report_file = TEST_RESULTS_DIR / "report.html"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(html)
    
    print(f"Test report generated: {report_file}")
    print(f"  Total tests: {report['total_tests']}")
    print(f"  Passed: {report['passed']}")
    print(f"  Failed: {report['failed']}")
    print(f"  Skipped: {report['skipped']}")

if __name__ == "__main__":
    generate_report()



