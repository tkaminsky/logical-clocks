import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.animation import PillowWriter
import argparse
import colorsys
import os

def create_distinguishable_colors(n):
    # Generate a list of n distinguishable colors
    # Adapted from https://stackoverflow.com/a/9701141
    colors = []
    for i in np.arange(0., 360., 360. / n):
        hue = i / 360.
        lightness = (50 + np.random.rand() * 10) / 100.
        saturation = (90 + np.random.rand() * 10) / 100.
        colors.append(tuple(colorsys.hls_to_rgb(hue, lightness, saturation) )
    )
    return colors

# Read experiment name from the command line
parser = argparse.ArgumentParser(description="Make animations for the experiment.")
parser.add_argument("-e", "--experiment", type=str, help="Experiment name.")
parser.add_argument("-s", "--subtitle", type=str, help="Subtitle data.")
args = parser.parse_args()

if args.experiment is None:
    # Raise an error if no experiment name is provided
    print("[ERROR] No experiment name provided.")
    exit(1)

experiment_name = args.experiment
base_dir = f"logs/{experiment_name}/"

subdirs = os.listdir(base_dir)

# If it is not a directory, remove it from the list
subdirs = [dir_now for dir_now in subdirs if os.path.isdir(f"{base_dir}{dir_now}")]

csv_paths = [f"{base_dir}{dir_now}/events.csv" for dir_now in subdirs]

# Sort them alpanumerically
csv_paths.sort()

subtitle_data = args.subtitle

xs_to_graph = ['TimeGlob', 'TimeGlob', 'TimeGlob']
ys_to_graph = ['QueueLen', 'TimeLocal', 'JumpTime']

window = 20  # sliding window size

# Read the data from the CSV file logs/test/c1_log/events.csv
dfs = []

for path in csv_paths:
    df = pd.read_csv(path)
    diffs = df['TimeLocal'].diff().fillna(0)
    df['JumpTime'] = diffs.expanding().mean()
    dfs.append(df)

for x, y in zip(xs_to_graph, ys_to_graph):
    start_times = []
    max_time_globs = []
    n_points = []
    queue_len_mins = []
    queue_len_maxs = []

    for df in dfs:
        start_times.append(df[x].min())
        max_time_globs.append(df[x].max())
        queue_len_maxs.append(df[y].max())
        queue_len_mins.append(df[y].min())
        n_points.append(df.shape[0])

    # Normalize the time values
    for i in range(len(dfs)):
        dfs[i][x] = dfs[i][x] - min(start_times)

    T = max(max_time_globs) - min(start_times)  # Total time

    # Create the figure and axes
    fig, ax = plt.subplots()

    # Initialize line objects for each dataset
    colors = ['b', 'r', 'g', 'y', 'm', 'c', 'k', 'orange', 'purple', 'brown', 'pink', 'gray']

    lines = []
    if len(dfs) > len(colors):
        colors = create_distinguishable_colors(len(dfs))



    for i in range(len(dfs)):
        # line, = ax.plot([], [], f'{colors[i]}-', label=f'Config {i+1}')
        line, = ax.plot([], [], color=colors[i], linestyle="solid", label=f'Config {i+1}')
        lines.append(line)

    # Set plot limits (adjust these based on your data)
    ax.set_xlim(0, T)
    ymin = min(queue_len_mins)
    ymax = max(queue_len_maxs)
    ax.set_ylim(ymin, ymax)
    # ax.legend()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Name axes
    ax.set_xlabel(x)
    ax.set_ylabel(y)

    fig.subplots_adjust(top=0.84)  # adjust as needed for your title/subtitle spacing

    # Set the centered main title and subtitle using the figure's methods.
    fig.suptitle(f"{x} vs {y}", fontsize=16, fontweight='bold', y=0.95)
    fig.text(0.5, 0.85, subtitle_data, ha='center', fontsize=12)

    # Determine the maximum number of frames based on each dataset
    max_frames = int(T)

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def update(frame):
        # Update x-axis limits: if frame < window, use [0, frame]; else use [frame-window, frame]
        if frame < window:
            ax.set_xlim(0, frame)
        else:
            ax.set_xlim(frame - window, frame)

        # For each dataframe, filter the data within the current x-axis window
        for i, df in enumerate(dfs):
            if frame < window:
                # Select points from 0 to frame
                mask = df[x] <= frame
            else:
                # Select points within [frame-window, frame]
                mask = (df[x] > frame - window) & (df[x] <= frame)

            lines[i].set_data(df[x][mask], df[y][mask])

        # Gather y data from all lines that have non-empty data
        all_y = np.concatenate([line.get_ydata() for line in lines if len(line.get_ydata()) > 0])
        if len(all_y) > 0:
            y_min, y_max = np.min(all_y), np.max(all_y)
            # Optionally, add a margin so the points don't touch the border
            margin = (y_max - y_min) * 0.1 if y_max != y_min else 1
            ax.set_ylim(y_min - margin, y_max + margin)

        return lines



    anim = FuncAnimation(
        fig, update, frames=range(0, max_frames),
        init_func=init, blit=False, interval=200
    )

    # Create a PillowWriter with desired frames per second (fps)
    writer = PillowWriter(fps=8)  # adjust fps as needed

    # Save the animation as a GIF
    anim.save(f"{base_dir}{x}_vs_{y}.gif", writer=writer)
