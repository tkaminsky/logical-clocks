# logical-clocks

Welcome to Design Problem 2: Scale Models and Logical Clocks. Below is a basic overview of the functionality, for running the code on your own!

## Running Experiments

To run your own experiment, first create a new directory in the configs directory, and three `yaml` files within it:

```
cd configs
mkdir [EXPERIMENT_NAME]
cd [EXPERIMENT_NAME]
touch c{1..3}.yaml
```

In each of the configs, include the following data (here's an example for `c2.yaml`):

```
experiment_dir: [EXPERIMENT_NAME]
name: "c2"
port: 12345
other_ports: [23456, 34567]
clock_speed: 5
```

Choose the other ports so each of the configs contains the whole set of ports, with their own being unique.

The clock speed determines the number of operations / second performed by each process, so **bigger = faster**.

Once you have the configs, change the base directory in `run_set.sh`, and then run it. This should generate output logs in the `logs/[EXPERIMENT_NAME]` directory.

## Plotting Data

To plot the data, go to `make_animations.py`, and change the `base_dir` to `logs/[EXPERIMENT_NAME]`.