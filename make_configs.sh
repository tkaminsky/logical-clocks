#!/bin/bash

experiment_name="30_agents_equal_times"
n_clients=30
clock_speeds=( $(for i in {1..30}; do echo 5; done) )
randn_UB=10

ports=($(shuf -i 10000-65535 -n $n_clients))

dir="configs/${experiment_name}/"

if [ ! -d "configs" ]; then
    mkdir "configs"
fi

if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
fi

for ((i=0; i<n_clients; i++)); do
    # Create a config of the form c[i].yaml
    echo "experiment_dir: ${experiment_name}" >> "${dir}c$((i + 1)).yaml"
    echo "name: c$((i + 1))" >> "${dir}c$((i + 1)).yaml"

    echo "port: ${ports[i]}" >>  "${dir}c$((i + 1)).yaml"


    # other_ports is all the other ports
    other_ports=()
    for ((j=0; j<n_clients; j++)); do
        if [ $j -ne $i ]; then
            other_ports+=(${ports[j]})
        fi
    done
    echo "other_ports: [$(IFS=,; echo "${other_ports[*]}")]" >>  "${dir}c$((i + 1)).yaml"

    echo "randn_UB: ${randn_UB}" >>  "${dir}c$((i + 1)).yaml"
    echo "clock_speed: ${clock_speeds[i]}" >>  "${dir}c$((i + 1)).yaml"
done
