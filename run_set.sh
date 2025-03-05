#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <experiment_name>"
    exit 1
fi

experiment_name="$1"

# List of config files
# configs=("c1.yaml" "c2.yaml" "c3.yaml")
dir="configs/${experiment_name}/"
configs=($(ls $dir))

# Loop through each config and run runner.py in the background
for config in "${configs[@]}"; do
    echo "Starting runner.py with config $dir$config"
    python runner.py -c "$dir$config" -t 120 &
done

# Wait for all background processes to complete
wait

echo "All runner processes have finished."
