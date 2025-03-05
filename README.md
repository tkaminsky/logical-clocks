# logical-clocks

Welcome to Design Problem 2: Scale Models and Logical Clocks. Below is a basic overview of the functionality, for running the code on your own!

## Dependencies

Make sure you have all these dependencies:

```
brew install coreutils
```

## Running Experiments

If any scripts don't run, make sure that you've run `chmod +x [script name].sh`.

To run your own experiment, first edit the information in `make_configs.sh`:

```
#!/bin/bash

experiment_name="two_equal"
n_clients=3
clock_speeds=(1 1 2)
randn_UB=20
```

In this example, 3 agents are created, with clock speeds of 1, 1, and 2 ticks / second. The clock speed determines the number of operations / second performed by each process, so **bigger = faster**.

Take note of the experiment name!

After this, you can run an experiment from configs using

```
./run_set.sh [experiment name]

// e.g.
./run_set.sh two_equal
```

This will save the data to the `logs` directory, in `logs/[experiment_name]`. Each process has a separate log directory `c[i]_log`, which contains a csv file of all logged events and a text document with metadata from the experiment.

## Plotting Data

To plot the data, run

```
python make_animations.py -e [experiment_name] -s [Subtitle]

// e.g. 
python make_animations.py -e two_equal -s "Clock Speeds: 1,1,2"
```