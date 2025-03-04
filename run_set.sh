#!/bin/bash

# List of config files
# configs=("c1.yaml" "c2.yaml" "c3.yaml")
dir="configs/close/"
configs=("c1.yaml" "c2.yaml" "c3.yaml")

# Loop through each config and run runner.py in the background
for config in "${configs[@]}"; do
    echo "Starting runner.py with config $dir$config"
    python runner.py -c "$dir$config" -t 120 &
done

# Wait for all background processes to complete
wait

echo "All runner processes have finished."
