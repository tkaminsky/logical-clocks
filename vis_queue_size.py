import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.animation import PillowWriter


base_dir = "logs/test/"
csv_paths = ["c1_log/events.csv", "c2_log/events.csv", "c3_log/events.csv"]

# Read the data from the CSV file logs/test/c1_log/events.csv
dfs = []
start_times = []
max_time_globs = []
n_points = []
queue_len_mins = []
queue_len_maxs = []

for path in csv_paths:
    df = pd.read_csv(base_dir + path)
    start_times.append(df['TimeGlob'].min())
    max_time_globs.append(df['TimeGlob'].max())
    queue_len_maxs.append(df['QueueLen'].max())
    queue_len_mins.append(df['QueueLen'].min())
    n_points.append(df.shape[0])
    dfs.append(df)

# Normalize the time values
for i in range(len(dfs)):
    dfs[i]['TimeGlob'] = dfs[i]['TimeGlob'] - min(start_times)

T = max(max_time_globs) - min(start_times)  # Total time

# Create the figure and axes
fig, ax = plt.subplots()

# Initialize line objects for each dataset
colors = ['b', 'r', 'g', 'y', 'm', 'c']
lines = []
try:
    assert len(dfs) <= len(colors)
except AssertionError:
    print(f"Error: Too many datasets. Maximum number of datasets is {len(colors)}.")
    exit(1)

for i in range(len(dfs)):
    line, = ax.plot([], [], f'{colors[i]}-', label=f'Config {i+1}')
    lines.append(line)

# Set plot limits (adjust these based on your data)
ax.set_xlim(0, T)
ymin = min(queue_len_mins)
ymax = max(queue_len_maxs)
ax.set_ylim(ymin, ymax)
ax.legend()
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

window = 20  # sliding window size

# Determine the maximum number of frames based on each dataset
max_frames = max(int(T) - window, 1)
print(f"Max frames: {max_frames}")

def init():
    for line in lines:
        line.set_data([], [])
    return lines

# def update(frame):
#     start = 0

#     # End points are the first indices with TimeGlob greater than frame
#     ends = []
#     for df in dfs:
#         ends.append(next((i for i, val in enumerate(df['TimeGlob']) if val > frame), len(df)))

#     for i in range(len(dfs)):
#         line = lines[i]
#         df = dfs[i]
#         end = ends[i]

#         line.set_data(df['TimeGlob'].iloc[start:end], df['QueueLen'].iloc[start:end])


#     return lines

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
            mask = df['TimeGlob'] <= frame
        else:
            # Select points within [frame-window, frame]
            mask = (df['TimeGlob'] > frame - window) & (df['TimeGlob'] <= frame)
        
        lines[i].set_data(df['TimeGlob'][mask], df['QueueLen'][mask])

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
anim.save("animation.gif", writer=writer)
