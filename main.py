import plotext as plt
import math
import numpy as np
import random
from pynput import keyboard

camera_x, camera_y, camera_z = 0, 0, 0

def trace(x_coords, y_coords, z_coords, d='No', color='green'):
    """Plot points given x/y/z arrays. z_coords is required.
    """
    for coord in range(len(x_coords)):
            if d == 'Yes':
                gradient = ['@', '#', 'o', '+', '×', ';', ':', '.']
            else:
                gradient = ['@', '#', 'o', '+', '-', ';', ':', '.']

            x = x_coords[coord]
            y = y_coords[coord]
            # z is required and used in calculations
            z = z_coords[coord]

            closeness = math.sqrt((sunx - x)**2 + (suny - y)**2 + (sunz - z)**2)
            t = min(closeness / math.dist((-100, 100), (100, -100)), 1.0)

            # fractional index
            f_idx = t * (len(gradient) - 1)
            low = int(f_idx)
            high = min(low + 1, len(gradient) - 1)
            mix = f_idx - low

            # --- softer, broader blend ---
            if 0.35 < mix < 0.65:
                # blend 50% of the points in a stable pattern
                if (int(x) + int(y)) % 2 == 0:
                    marker = gradient[high]
                else:
                    marker = gradient[low]
            else:
                # normal behavior away from the blend zone
                marker = gradient[high] if mix >= 0.5 else gradient[low]

            plt.scatter([x], [y], marker=marker, color=color)

def line(start, end, d='No', color='green', steps=1000):
    """
    Generate coordinates between two 3D points and plot the projected 2D
    coordinates. start and end should be (x, y, z). z is accepted but the
    current renderer plots x/y only.

    start: (x, y, z)
    end:   (x, y, z)
    steps: number of points along the line
    """
    x0, y0, z0 = start
    x1, y1, z1 = end

    x_coords = np.linspace(x0, x1, steps)
    y_coords = np.linspace(y0, y1, steps)
    z_coords = np.linspace(z0, z1, steps)

    trace(x_coords, y_coords, z_coords, d, color)

def square(start_x=-40, start_y=-40, start_z=0, side_length=50, d='No', color='green', solid=False):
    if (((start_z + (start_z + side_length))/2) - camera_z) > 0:
        side_length = 0
    else:
        side_length = int(side_length * (0.009 + (3 - 0.009) * math.exp(-0.03 * abs(side_length - camera_z))))
    # Draw the four edges (each endpoint is (x,y,z))
    line((start_x + side_length, start_y, start_z), (start_x + side_length,  start_y + side_length, start_z), d='No', color=color)
    line((start_x, start_y, start_z), (start_x,  start_y + side_length, start_z), d='No', color=color)
    if solid == True:
        for i in range(side_length):
            line((start_x, start_y + i, start_z), (start_x + side_length, start_y + i, start_z), d='No', color=color)
    else:
        line((start_x, start_y + side_length, start_z), (start_x + side_length, start_y + side_length, start_z), d='No', color=color)
        line((start_x, start_y, start_z), (start_x + side_length, start_y, start_z), d='No', color=color)

def cube(start_x=-30, start_y=-30, start_z=0, side_length=60, color='green', solid=False):
    # Draw front and back squares (back square offset in x/y/z by side_length - 30)
    square(start_x, start_y, start_z, side_length, d='No', color=color, solid=solid)
    back_offset = side_length - 30
    square(start_x + back_offset, start_y + back_offset, start_z + back_offset, side_length, d='No', color=color, solid=solid)
    if solid == True:
        for i in range(side_length):
            line((start_x + side_length, start_y + i, start_z), (start_x + side_length + side_length - 30, start_y + side_length + i - 30, start_z + back_offset), 'Yes', color=color)
            line((start_x + i, start_y + side_length, start_z), (start_x + side_length + i - 30, start_y + side_length + side_length - 30, start_z + back_offset), 'Yes', color=color)
    else:
        line((start_x, start_y, start_z), (start_x + side_length - 30, start_y + side_length - 30, start_z + back_offset), 'Yes', color=color)
        line((start_x + side_length, start_y, start_z), (start_x + side_length + side_length - 30, start_y + side_length - 30, start_z + back_offset), 'Yes', color=color)
        line((start_x, start_y + side_length, start_z), (start_x + side_length - 30, start_y + side_length + side_length - 30, start_z + back_offset), 'Yes', color=color)
        line((start_x + side_length, start_y + side_length, start_z), (start_x + side_length + side_length - 30, start_y + side_length + side_length - 30, start_z + back_offset), 'Yes', color=color)

def circle(center_x=0, center_y=0, center_z=0, radius=30, color='cyan'):
    if (center_z - camera_z) > 0:
        radius = 0
    else:
        radius = int(radius * (0.009 + (3 - 0.009) * math.exp(-0.03 * abs(center_z - camera_z))))
    num_points = 400 # More points improve granularity for segments
    # --- Generate the angles (from 0 to 2*PI) ---
    angles = np.linspace(0, 2 * math.pi, num_points + 1)

# --- Calculate x, y (and z) coordinates ---
    for i in range(radius):
        x_coords = np.array([center_x + i * math.cos(angle) for angle in angles])
        y_coords = np.array([center_y + i * math.sin(angle) for angle in angles])
        # make z a constant ring height (center_z + i)
        z_coords = np.full_like(x_coords, center_z + i, dtype=float)
        trace(x_coords, y_coords, z_coords, 'No', color)

def visual():
    # Remove x-axis tick numbers
    plt.xticks([])  
    # Remove y-axis tick numbers
    plt.yticks([])
    # First, define the plot limits so we know the max/min coordinates
    plt.xlim(-100, 100)
    plt.ylim(-100, 100)
    plt.canvas_color("black")
    plt.frame(False)
    plt.show()

def shapes():
    cube()
    plt.scatter([sunx], [suny], marker = 'Light', color = 'red')

def render():
    plt.clf()
    shapes()
    visual()



# Show the plot

# circle(-50, 50, 20)
sunx, suny, sunz = 30, 30, 40
camera_x, camera_y, camera_z = 0, 0, 0

render()

def on_press(key, injected):
    global camera_x, camera_y, camera_z
    try:
        if key.char == 's':
            camera_z += 5
            render()
        elif key.char == 'w':
            camera_z -= 5
            render()
    except AttributeError:
        return None
        

# Collect events until released
with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()
listener.start()