#!/bin/bash
# Monitor progress of movie cleaning processes

echo "=========================================="
echo "MOVIE CLEANING PROGRESS MONITOR"
echo "=========================================="
echo ""

# Check running processes
echo "=== RUNNING PROCESSES ==="
ps aux | grep -E "clean.py|process_both" | grep -v grep | while read line; do
    pid=$(echo $line | awk '{print $2}')
    cmd=$(echo $line | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
    cpu=$(echo $line | awk '{print $3}')
    mem=$(echo $line | awk '{print $4}')
    echo "PID: $pid | CPU: $cpu% | MEM: $mem%"
    echo "  Command: $cmd"
    echo ""
done

# Check log files
echo "=== CODE_3 PROGRESS (Last 20 lines) ==="
if [ -f /tmp/code3_clean.log ]; then
    tail -20 /tmp/code3_clean.log | grep -E "Step|Found|Processing|SUCCESS|Error|Analyzing|Detecting" || tail -5 /tmp/code3_clean.log
else
    echo "Log file not found"
fi
echo ""

echo "=== BATCH PROCESS LOG (Last 20 lines) ==="
if [ -f /tmp/movies_batch.log ]; then
    tail -20 /tmp/movies_batch.log | grep -E "Processing|SUCCESS|Failed|Step|Found" || tail -5 /tmp/movies_batch.log
else
    echo "Log file not found"
fi
echo ""

# Check output files
echo "=== OUTPUT FILES ==="
if [ -d "movies/cleaned" ]; then
    ls -lh movies/cleaned/* 2>/dev/null | awk '{print $5, $9}' | head -10
    file_count=$(ls -1 movies/cleaned/* 2>/dev/null | wc -l)
    echo "Total files in cleaned folder: $file_count"
else
    echo "Cleaned folder not found yet"
fi
echo ""

echo "=========================================="
echo "To watch progress in real-time, run:"
echo "  tail -f /tmp/code3_clean.log"
echo "  tail -f /tmp/movies_batch.log"
echo "=========================================="





