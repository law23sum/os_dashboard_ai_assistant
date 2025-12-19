#!/bin/bash
# End-to-End Test Runner
# Supports multiple environments: local/dev, alpha/beta, prod/release

set -e

ENVIRONMENT="${1:-local}"
TEST_TYPE="${2:-all}"

echo "=========================================="
echo "OS Dashboard E2E Test Suite"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "Test Type: $TEST_TYPE"
echo ""

# Validate environment
case "$ENVIRONMENT" in
  local|dev|alpha|beta|prod|release)
    echo "✓ Environment validated: $ENVIRONMENT"
    ;;
  *)
    echo "✗ Invalid environment: $ENVIRONMENT"
    echo "Available: local, dev, alpha, beta, prod, release"
    exit 1
    ;;
esac

# Set environment variables
export TEST_ENV="$ENVIRONMENT"

# Run tests based on type
case "$TEST_TYPE" in
  sanity)
    echo "Running sanity tests..."
    npm run test:e2e:sanity -- --env="$ENVIRONMENT"
    ;;
  functional)
    echo "Running functional tests..."
    npm run test:e2e:functional -- --env="$ENVIRONMENT"
    ;;
  regression)
    echo "Running regression tests..."
    npm run test:e2e:regression -- --env="$ENVIRONMENT"
    ;;
  all)
    echo "Running all test suites..."
    npm run test:e2e:sanity -- --env="$ENVIRONMENT"
    npm run test:e2e:functional -- --env="$ENVIRONMENT"
    npm run test:e2e:regression -- --env="$ENVIRONMENT"
    ;;
  *)
    echo "✗ Invalid test type: $TEST_TYPE"
    echo "Available: sanity, functional, regression, all"
    exit 1
    ;;
esac

echo ""
echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="
