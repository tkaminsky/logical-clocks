#!/bin/bash

# List of config files
configs=("c1.yaml" "c2.yaml" "c3.yaml")

# Loop through each config and run runner.py in the background
for config in "${configs[@]}"; do
    echo "Starting runner.py with config $config"
    python runner.py -c "$config" -t 15 &
done

# Wait for all background processes to complete
wait

echo "All runner processes have finished."
