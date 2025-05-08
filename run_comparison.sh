#!/bin/bash

# Script to run benchmark and comparison tools

echo "=============================================================="
echo "Running baseline benchmark with inefficient orchestrator..."
echo "=============================================================="
hatch run benchmark --test-case all --iterations 3
echo ""

echo "=============================================================="
echo "Running orchestrator comparison with optimized implementations..."
echo "=============================================================="
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --iterations 3
echo ""

echo "=============================================================="
echo "Comparison complete. Done!"
echo "==============================================================" 