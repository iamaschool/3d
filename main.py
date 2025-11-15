import plotext as plt
import math
import numpy as np

# --- Circle Parameters ---
center_x = 0
center_y = 0
radius = 5
num_points = 300 # More points improve granularity for segments


# --- Generate the angles (from 0 to 2*PI) ---
angles = np.linspace(0, 2 * math.pi, num_points + 1)


    # --- Calculate x and y coordinates ---
x_coords = np.array([center_x + radius * math.cos(angle) for angle in angles])
y_coords = np.array([center_y + radius * math.sin(angle) for angle in angles])
for coord in len(x_coords):
    x = x_coords[coord]
    y = y_coords[coord]
    
print(x_coords + y_coords)


# --- General Plot Settings ---
plt.title("Multi-Marker Circle Plot")

# Remove x-axis tick numbers
plt.xticks([])

# Remove y-axis tick numbers
plt.yticks([])

# First, define the plot limits so we know the max/min coordinates
plt.xlim(-100, 100)
plt.ylim(-100, 100)

plt.scatter([-99], [99], marker = '%', color = 'white')
# Show the plot
plt.show()
