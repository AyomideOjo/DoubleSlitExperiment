# Citation --> https://github.com/Dementophobia/double-slit-simulator/blob/main/interference_simulation.py
# Wave Experiment for article
# The Double Slit Experiment as taught by Richard Feynman

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import inflect

class Wave:
    source = {"x": 0, "y": 0}
    distance_map = None

    def __init__(self, x, y):
        self.source = {"x": x, "y": y}

    def create_distance_map(self, x, y):
        self.distance_map = np.sqrt((x - self.source["x"]) ** 2 + (y - self.source["y"]) ** 2)

def init_waves(num_slits, slit_distance, close):
    if not 1 <= num_slits <= 4:
        raise ValueError("Not valid Number of Slits input an integer between 1 and 4 inclusive")

    if close != "none" and num_slits == 2:
        temp = list(range(-(num_slits // 2), (num_slits // 2) + 1))
        temp.remove(0)
        if close == "right":
            temp.remove(1)
        if close == "left":
            temp.remove(-1)
        temp = tuple(temp)
        return [Wave(0, direction * slit_distance / 2) for direction in temp]

    if num_slits % 2 == 1:
        return [Wave(0, direction * slit_distance / 2)
            for direction in tuple(range(-(num_slits//2), (num_slits//2) + 1))]

    if num_slits % 2 == 0:
        temp = list(range(-(num_slits//2), (num_slits//2) + 1))
        temp.remove(0)
        temp = tuple(temp)
        return [Wave(0, direction * slit_distance / 2) for direction in temp]

def create_wave_pattern(waves, step, steps):
    return abs(sum([np.sin(wave.distance_map - 2 * np.pi * step / steps) for wave in waves]))

def number_to_words(number):
    p = inflect.engine()
    return p.number_to_words(number)

def update_plot_3d(step, x, y, z_over_time, plot, ax, quality, steps):
    print(f"Step {step + 1} from {steps}")
    plot[0].remove()
    plot[0] = ax.plot_surface(x, y, z_over_time[:, :, step], rstride=quality,
        cstride=quality, cmap=plt.cm.winter, linewidth=0, antialiased=True)

def create_animated_3d_plot(x, y, z_over_time, type_of_simulation, steps, quality):
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(azim=0, elev=90)
    ax.set_zticks([])
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.autoscale(tight=True)

    plot = [ax.plot_surface(x, y, z_over_time[:, :, 0], rstride=quality,
            cstride=quality, cmap=plt.cm.winter, linewidth=0, antialiased=True)]

    ani = FuncAnimation(fig, update_plot_3d, frames=steps, fargs=(x, y, z_over_time, plot, ax, quality, steps), blit=False)
    ani.save(f"{type_of_simulation}_wave_slit_{close}_animated_3d.gif", writer=PillowWriter(fps=steps // 2))

def update_plot_wall(step, wall_over_time, sum_over_time, plots, y, steps):
    print(f"Step {step + 1} from {steps}")
    plots[0].set_data(y, wall_over_time[:, step])
    plots[1].set_data(y, sum_over_time[:, step])
    return [plots]

def create_animated_wall_plot(breadth, z_over_time, type_of_simulation, steps):
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    ax.xaxis.set_ticklabels([])
    ax.xaxis.set_ticks([])

    y = np.arange(-breadth, breadth, 0.05)

    wall_over_time = z_over_time[:, -1, :]
    plt.ylim((-0.2, np.amax(wall_over_time) + 0.2))
    plt.ylabel("Intensity over Time")

    sum_over_time = np.zeros((len(y), steps))
    sum_over_time[:, 0] = wall_over_time[:, 0] / steps

    for step in range(1, steps):
        sum_over_time[:, step] = sum_over_time[:, step - 1] + wall_over_time[:, step] / steps

    plots = [ax.plot(y, wall_over_time[:, 0])[0], ax.plot(y, sum_over_time[:, 0])[0]]

    ani = FuncAnimation(fig, update_plot_wall, frames=steps,
        fargs=(wall_over_time, sum_over_time, plots, y, steps), blit=False)
    ani.save(f"{number_to_words(type_of_simulation)}_wave_slit_{close}_animated_wall.gif", writer=PillowWriter(fps=steps // 3))

    plt.clf()
    ax = fig.add_subplot(111)
    ax.xaxis.set_ticklabels([])
    ax.xaxis.set_ticks([])
    plt.ylim((-0.2, np.amax(wall_over_time) + 0.2))
    plt.ylabel("Intensity over Time")
    plt.plot(sum_over_time[:, -1], color="orange")
    plt.savefig(f"{number_to_words(type_of_simulation)}_wave_slit_{close}_wall_result.png")

def main(breadth, number_of_slits, slit_distance, steps, wall_distance, quality, close):
    waves = init_waves(number_of_slits, slit_distance, close)
    x, y = np.arange(0, wall_distance, 0.05), np.arange(-breadth, breadth, 0.05)
    x, y = np.meshgrid(x, y)
    for wave in waves:
        wave.create_distance_map(x, y)

    z_over_time = np.zeros((len(x), len(y[0]), steps))
    for step in range(steps):
        z_over_time[:, :, step] = create_wave_pattern(waves, step, steps)

    create_animated_3d_plot(x, y, z_over_time, number_of_slits, steps, quality)
    create_animated_wall_plot(breadth, z_over_time, number_of_slits, steps)

close = "none"
main(breadth = 100, number_of_slits = 2, slit_distance = 8 * np.pi,
     steps = 50, wall_distance = 40, quality = 1, close = "none")

# close = "none", "right", "left"