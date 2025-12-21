#!/bin/bash
# Run all page tests and generate report

set -e

FRONTEND_DIR="$(cd "$(dirname "$0")/../frontend" && pwd)"
cd "$FRONTEND_DIR"

echo "Running page tests..."
echo "===================="

# Run tests with coverage
npm run test:coverage -- --run

# Generate test report
echo ""
echo "Test Summary:"
echo "=============="

# Count test files
TEST_COUNT=$(find src/pages/__tests__ -name "*.test.tsx" 2>/dev/null | wc -l | tr -d ' ')
echo "Total test files: $TEST_COUNT"

# Check for test failures
if [ -f "coverage/coverage-summary.json" ]; then
    echo "Coverage report generated in coverage/"
fi

echo ""
echo "Tests completed!"


