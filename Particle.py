import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import inflect
from scipy.stats import skewnorm
from scipy.interpolate import make_interp_spline

class Particle:
    position = {"x": 0, "y": 0}
    angle = 90

    def __init__(self, x, y, skewness):
        self.get_angle(skewness if y < 0 else -skewness if y > 0 else 0)
        self.position = {"x": x, "y": y}

    def get_angle(self, skewness):
        numValues = 10000; maxValue = 180
        temp = skewnorm.rvs(a = skewness, loc = maxValue, size = numValues)
        temp = temp - min(temp)
        temp = temp / max(temp)
        temp = temp * maxValue
        self.angle = np.random.choice(np.array(temp))

def init_particle(num_slits, slit_distance, close, skewness, num_particles):
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
        return [Particle(0, direction * slit_distance / 2, skewness)
                for direction in temp for _ in range(num_particles)]

    if num_slits % 2 == 1:
        return [Particle(0, direction * slit_distance / 2, skewness)
            for direction in tuple(range(-(num_slits//2), (num_slits//2) + 1))
                for _ in range(num_particles)]

    if num_slits % 2 == 0:
        temp = list(range(-(num_slits//2), (num_slits//2) + 1))
        temp.remove(0)
        temp = tuple(temp)
        return [Particle(0, direction * slit_distance / 2, skewness) for direction in temp
                for _ in range(num_particles)]

def update_particle_position(wall_distance, particles, thres):
    histogram = []
    for particle in particles:
        adjacent = wall_distance
        opposite = np.tan(particle.angle) * adjacent
        particle.position["x"] = wall_distance

        temp_y = particle.position["y"]
        index = opposite + temp_y
        histogram.append(index)

    histogram = np.array(histogram)
    histogram = histogram[histogram <= thres]
    histogram = histogram[histogram >= -thres]
    return histogram

def number_to_words(number):
    p = inflect.engine()
    return p.number_to_words(number)

def generate_histogram(histogram, num_particles, number_of_slits, type_of_simulation, close):
    bins = np.linspace(min(histogram), max(histogram), num=len(set(histogram)) + 1)
    hist, bins = np.histogram(histogram, bins=bins)
    plt.bar(bins[:-1], hist, width=(bins[1] - bins[0]), align='edge')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Histogram')
    plt.savefig(f"{number_to_words(type_of_simulation)}_particle_slit_{close}_wall_probability_discrete_result.png")

    hist, bins = np.histogram(histogram, bins=30)
    center = (bins[:-1] + bins[1:]) / 2
    smooth = np.linspace(center.min(), center.max(), num_particles * number_of_slits)
    spl = make_interp_spline(center, hist, k=3)
    smooth_hist = spl(smooth)
    plt.plot(smooth, smooth_hist, '-b', label='Smooth Line')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Smoothed Line Graph from Histogram')
    plt.savefig(f"{number_to_words(type_of_simulation)}_particle_slit_{close}_wall_probability_smooth_result.png")

def main(number_of_slits, slit_distance, wall_distance, skewness, close, num_particles, thres):
    particles = init_particle(number_of_slits, slit_distance, close, skewness, num_particles)
    histogram = update_particle_position(wall_distance, particles, thres)
    generate_histogram(histogram, num_particles, number_of_slits, number_of_slits, close)

main(number_of_slits = 2, slit_distance = 8 * np.pi, wall_distance = 40,
     skewness = 0, close = 'none', num_particles = 10_000, thres = 1_000)