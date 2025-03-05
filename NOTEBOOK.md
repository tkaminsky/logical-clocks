# Engineering Notebook

## Design Problem 2: Logical Clocks

Below we describe some of our thoughts for design exercise two.

#### [Implementation](#implementation-1)

#### [Experiments](#experiments-1)

## Implementation

To model each process, our broad strategy will be to create one class which is parametrized by the following (variable) experimental parameters:

-   Clock Speed (in ticks/sec)
-   Probability of taking an internal action (expressed as a maximum for a random integer)
-   A port number
-   A list of all other ports with which it should communicate

To encode these hyperparameters, we will store them in `.yaml` config files in a common experiment directory.

Creating new processes will be done by calling `runner.py` with a given config. This runner will create two components:

-   A listener thread which constantly monitors the socket for incoming messages, appending them to the network queue---this will ensure that tick speed doesn't yield dropped messages.
-   A client thread which implements the logical clock specification and the logic for making internal actions / sends / receives

Note that, for taking messsages off of the queue, we assume that messages are first-in-first-out. Though another strategy (like LIFO) may yield better performance in our model (since, at the very least, the client would always see the most recent time from its neighbors), this formulation captures the worst-case of a distributed system, in which each agent must work with each message _in order_ for the algorithm to run correctly.

Broadly, `runner.py` contains broad specificiation (like the probabilities of taking each kind of action), and the underlying class in `client.py` encodes the logic for logging, sending/receiving messages, and updating the clock.

## Results

### Jump Sizes

One metric of interest to us is the "jump size" between consecutive operations for a given process. We defined jump size the same way as in EdPost [#76](https://edstem.org/us/courses/69416/discussion/6308559). More specifically, the jump size of a process at time $t$ is the average difference between consecutive operations of the process up to time $t$. The jump time at $t = 0$ is defined to be 0.

It follows directly, that the process with the fastest clock speed would have a jump time that is asymptotically one since after the first time step the consecutive difference is always 1. We would also suspect the processes with slower clocks will have larger jump times since they are more likely to have to update the logical clock to a value that is larger than their predicted next tick value. We see this behavior directly when comparing processes with clock speeds 1, 3, 6.

<center>
<img src="media/long_clocks_1_3_6/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 50%;">
</center>

We also wanted to investigate how the relative timings affected the jump size. To this end, we scaled the clock size up and down by 2 and graphed the results. We notice that the overall behavior remains the same, however, a lower clock speed tends to result n a higher actual jump size. This is especially noticeable for config 1. This makes intuitive sense, since if the process is leaving messages in the queue for longer, than the absolute change in tick value will increase.

<center>
  <img src="media/scaled_long_clocks_2_6_12/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 45%; margin-right: 10px;">
  <img src="media/scaled_long_clocks_0.5_1.5_3//TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 45%; margin-right: 10px;">
</center>

An additive change to the timings preserves the overall behavior, but does not a seem to provide a consistent effect on the absolute value of the jump size.

<center>
<img src="media/added_long_clocks_6_8_11/TimeGlob_vs_JumpTime.gif" alt="TimeGlob vs QueueLen" style="max-width: 50%;">
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
