# Engineering Notebook
## Design Problem 2: Logical Clocks

Below we describe some of our thoughts for design exercise two.

#### [Implementation](#implementation-1)


## Implementation

To model each process, our broad strategy will be to create one class which is parametrized by the following (variable) experimental parameters:

* Clock Speed (in ticks/sec)
* Probability of taking an internal action
* A port number
* A list of all other ports with which it should communicate