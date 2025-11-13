#!/bin/bash

# BIFI-001 Test Runner
# Runs all tests for the bifacial performance protocol

set -e

echo "=========================================="
echo "BIFI-001 Bifacial Performance Test Suite"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/ \
    --cov=python \
    --cov=db \
    --cov-report=term-missing \
    --cov-report=html \
    -v

echo ""
echo "=========================================="
echo "Tests completed!"
echo "Coverage report saved to htmlcov/index.html"
echo "=========================================="
