#!/bin/bash

# Script to run benchmark and comparison tools

echo "=============================================================="
echo "Running baseline benchmark with inefficient orchestrator..."
echo "=============================================================="
task benchmark -- --test-case all --iterations 3
echo ""

echo "=============================================================="
echo "Running orchestrator comparison with optimized implementations..."
echo "=============================================================="
task compare-benchmarks -- --compare-dir benchmark_orchestrators --iterations 3
echo ""

echo "=============================================================="
echo "Comparison complete. Done!"
echo "==============================================================" 