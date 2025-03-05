# Engineering Notebook

## Design Problem 2: Logical Clocks


Below we describe some of our thoughts for design exercise two. In the first section, we explain our thought process for the implementation of the model, and in the second, we go over some interesting results.

#### [Implementation](#implementation-1)

#### [Results](#results-1)

## Implementation

To model each process, our broad strategy will be to create one class which is parametrized by the following (variable) experimental parameters:

-   Clock Speed (in ticks/sec)
-   Probability of taking an internal action (expressed as a maximum for a random integer)
-   A port number
-   A list of all other ports with which it should communicate

To encode these hyperparameters, we will store them in `.yaml` config files in a common experiment directory.

Creating new processes will be done by calling `runner.py` with a given config. This runner will create two components:

-   A listener thread which constantly monitors the socket for incoming messages, appending them to the network queue---this will ensure that tick speed doesn't yield dropped messages.
-   A client thread which implements the logical clock specification and the logic for making internal actions / sends / receives.

Note that, for taking messsages off of the queue, we assume that messages are first-in-first-out. Though another strategy (like LIFO) may yield better performance in our model (since, at the very least, the client would always see the most recent time from its neighbors), this formulation captures the worst-case of a distributed system, in which each agent must work with each message _in order_ for the algorithm to run correctly.

Broadly, `runner.py` contains broad specificiation (like the probabilities of taking each kind of action), and the underlying class in `client.py` encodes the logic for logging, sending/receiving messages, and updating the clock.

After you've edited `make_configs.sh` to encode your specifications, running experiments and plotting results is as simple as executing the following:

```
./make_configs.sh
./run_experiment.sh [EXPERIMENT_NAME]
python make_animations.py -e [EXPERIMENT_NAME] -s [Plot Subtitle]
```

## Results

Below we describe some results found during our experiments.

Changing Clock Times (in ticks/sec). All clients had 6/10 probability of an internal action:
1. (1, 1.5, 2)
2. (2, 3, 4)
3. (4, 6, 8)
4. (0.5, 1.5, 3)
5. (1, 3, 6)
6. (2, 6, 12)
7. (0.5, 1.5, 2.5)
8. ()

Note that experiments 1-3 have constant ratios between clock times, as do experiments 4-6, with 1-3 having "closer" clock speeds than 4-6. Experiment 

Thus, we think about 1-6 as comparing _multiplicative_ relationships between clock speeds, and (2,5) vs (7,8) as testing _additive_ relationships.

### Observation: Close Clocks Maintain Bounded Queues and Time Delays

We found that clocks with similar relative times (1-3) incurred only bounded queue lengths in their slowest members, and as a result their clocks were periodically rectified with the fastest clock, as can be seen in the middle row of plots. We see that, over two minutes, the two slower processes are periodically returned to the local time of the fastest clock.

The top row of charts show that the queue lengths periodically "empty", indicating that each process is able to read all messages over time. Finally, the bottom row of charts indicate that the average jump time---which is higher when processes are further back in time---reaches a steady state for each process. This indicates that the agents are likely to maintain stable time synchronization, as they remain boundedly far behind the fastest clock upon updates. 

We note that this behavior is consistant across uniform multiples of clock speeds. This makes sense, as speeding up all clocks by 2x both doubles the expected rate at which messages are sent and the rate at which agents can read their messages.

<table>
  <tr>
    <td><img src="media/scaled_long_clocks_0.5_1.5_3/TimeGlob_vs_QueueLen.gif" alt="Image 1" width="300"></td>
    <td><img src="media/long_clocks_1_3_6/TimeGlob_vs_QueueLen.gif" alt="Image 2" width="300"></td>
    <td><img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_QueueLen.gif" alt="Image 3" width="300"></td>
  </tr>
  <tr>
    <td><img src="media/scaled_long_clocks_0.5_1.5_3/TimeGlob_vs_TimeLocal.gif" alt="Image 1" width="300"></td>
    <td><img src="media/long_clocks_1_3_6/TimeGlob_vs_TimeLocal.gif" alt="Image 2" width="300"></td>
    <td><img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_TimeLocal.gif" alt="Image 3" width="300"></td>
  </tr>
  <tr>
    <td><img src="media/scaled_long_clocks_0.5_1.5_3/TimeGlob_vs_JumpTime.gif" alt="Image 1" width="300"></td>
    <td><img src="media/long_clocks_1_3_6/TimeGlob_vs_JumpTime.gif" alt="Image 2" width="300"></td>
    <td><img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_JumpTime.gif" alt="Image 3" width="300"></td>
  </tr>
</table>


<center>
  <img src="media/pc_1_1.5_2/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/pc_2_3_4/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/pc_4_6_8/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs TimeLocal" style="max-width: 30%;">
</center>

<center>
  <img src="media/pc_1_1.5_2/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/pc_2_3_4/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/pc_4_6_8/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs TimeLocal" style="max-width: 30%;">
</center>

<center>
  <img src="media/pc_1_1.5_2/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/pc_2_3_4/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/pc_4_6_8/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs TimeLocal" style="max-width: 30%;">
</center>

### Observation: Distant Clocks May Yield Unbounded Queues and Time Delays

Conversely, experiments 4-6 show that, when relative clock speeds are sufficiently large, it is possible for the queue to grow unboundedly. As we see in the first row of plots below, the length of the slowest process' queue generally increases, and never returns to 0 after the first few timesteps.

This also yields a gradual desynchronization of the slowest process from the faster ones, as it reads messages which are, by the end of the program, around 40 sends old. However, the faster process is able to keep up, and it doesn't experience this divergence.

<center>
  <img src="media/scaled_long_clocks_0.5_1.5_3/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/long_clocks_1_3_6/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs TimeLocal" style="max-width: 30%;">
</center>

<center>
  <img src="media/scaled_long_clocks_0.5_1.5_3/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/long_clocks_1_3_6/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs TimeLocal" style="max-width: 30%;">
</center>

<center>
  <img src="media/scaled_long_clocks_0.5_1.5_3/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs TimeLocal" style="max-width: 30%;">
</center>


### Jump Sizes

One metric of interest to us is the "jump size" between consecutive operations for a given process. We defined jump size the same way as in EdPost [#76](https://edstem.org/us/courses/69416/discussion/6308559). More specifically, the jump size of a process at time $t$ is the average difference between consecutive operations of the process up to time $t$. The jump time at $t = 0$ is defined to be 0.

It follows directly, that the process with the fastest clock speed would have a jump time that is asymptotically one since after the first time step the consecutive difference is always 1. We would also suspect the processes with slower clocks will have larger jump times since they are more likely to have to update the logical clock to a value that is larger than their predicted next tick value. We see this behavior directly when comparing processes with clock speeds 2, 3, 4.

<center>
<img src="media/pc_2_3_4/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 50%;">
</center>

We also wanted to investigate how the relative timings affected the jump size. To this end, we scaled the clock size up and down by 2 and graphed the results. We notice that the overall behavior is exactly the same.

<center>
  <img src="media/pc_1_1.5_2/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 45%; margin-right: 10px;">
  <img src="media/pc_4_6_8//TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 45%; margin-right: 10px;">
</center>

An additive change to the timings preserves the overall behavior, but does not a seem to provide a consistent effect on the absolute value of the jump size.

<center>
<img src="media/pc_.5_1.5_2.5/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 50%;">
</center>

<!-- Here, we set a distance of

<div style="display: flex; align-items: center;">
  <img src="media/long_clocks_1_3_6/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 33%; margin-right: 10px;">
  <img src="media/pc_2_3_4/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 33%; margin-right: 10px;">
  <img src="media/pc_4_6_8/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs TimeLocal" style="max-width: 33%;">
</div> -->

### Time Drift

We also were interested in measuring the time drift between the clocks. As in EdPost [#76](https://edstem.org/us/courses/69416/discussion/6308559) we define time drift as the difference in the values of the individual logical clocks at a given time. For varying clock times, we noticed that there is a significant drift between the slowest clock time and the other two clock times. The second fastest clock time does not drift too far away from the fastest clock time.

<center>
<img src="media/long_clocks_1_3_6/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 50%;">
</center>

This behavior is preserved when scaling the clock speeds. This indicates that drift of between two clocks seems to be related to their relative (multiplicative) magnitude to one another.

<center>
  <img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 45%; margin-right: 10px;">
  <img src="media/scaled_long_clocks_0.5_1.5_3//TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 45%; margin-right: 10px;">
</center>

Further evidence of this is that when we increased the clock speeds of all the clocks by the same amount, the time drift between the clocks dropped significantly. When we added a constant amount to the clock speeds, we ultimately reduced the multiplicative clock ratio which seems to correspond to this decrease in clock drift.

<center>
<img src="media/added_long_clocks_6_8_11/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 50%;">
</center>

### Queue Size

We notice that if a machine has a slow enough clock, then its queue can grow unboundedly.

<center>
<img src="media/long_clocks_1_3_6/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs QueueLen" style="max-width: 50%;">
</center>

#### Observation: Even with equal clocks, queues can grow unboundedly.

Here, we took $n=30$ agents, each with a clock speed of $5$ ticks/second.

We see that the local times remain within a bounded distance, and the jump times converge to approximately 1. However, the queue length for some agents continues to grow. This is because, in effect,

The reason why some agents don't have queue growth is most likely because, once an agent has a nonempty queue, it stops sending messages. This means that some set of agents get their queues filled at a steady rate, and all others now only recieve a small set of messages which they can control.

Here is a gif summary of our results:

<center>
  <img src="media/30_agents/TimeGlob_vs_QueueLen.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/30_agents/TimeGlob_vs_TimeLocal.gif" alt="TimeGlob vs QueueLen" style="max-width: 30%; margin-right: 10px;">
  <img src="media/30_agents/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs TimeLocal" style="max-width: 30%;">
</center>
