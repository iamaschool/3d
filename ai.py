import plotext as plt
import math
import numpy as np
import random
import sys
import tty
import termios
import select

# Camera position
camera_x, camera_y, camera_z = 0, 0, 300
camera_rotation_y = 0  # Rotation around Y axis (left/right look)

sunx, suny, sunz = 0, 0, 0

def get_key():
    """Non-blocking keyboard input that reads full escape sequences"""
    if select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # ESC sequence
            # Try to read the rest of the escape sequence
            import time
            time.sleep(0.001)
            if select.select([sys.stdin], [], [], 0)[0]:
                ch += sys.stdin.read(1)
                if select.select([sys.stdin], [], [], 0)[0]:
                    ch += sys.stdin.read(1)
        return ch
    return None

def project_3d_to_2d(x, y, z, projection='perspective'):
    """
    Project 3D coordinates to 2D screen coordinates with camera position.
    """
    # Translate world coordinates relative to camera
    rel_x = x - camera_x
    rel_y = y - camera_y
    rel_z = z - camera_z
    
    # Apply camera rotation around Y axis
    cos_rot = math.cos(camera_rotation_y)
    sin_rot = math.sin(camera_rotation_y)
    
    rotated_x = rel_x * cos_rot - rel_z * sin_rot
    rotated_z = rel_x * sin_rot + rel_z * cos_rot
    rotated_y = rel_y
    
    if projection == 'perspective':
        focal_length = 200
        
        if rotated_z != 0:
            scale = focal_length / rotated_z
        else:
            scale = 1
            
        screen_x = rotated_x * scale
        screen_y = rotated_y * scale
        
    else:  # orthographic
        screen_x = rotated_x - rotated_z * 0.5
        screen_y = rotated_y + rotated_z * 0.5
    
    return screen_x, screen_y

def trace(x_coords, y_coords, z_coords, d='No', color='green'):
    for coord in range(len(x_coords)):
            if d == 'Yes':
                gradient = ['@', '#', 'o', '+', '×', ';', ':', '.']
            else:
                gradient = ['@', '#', 'o', '+', '-', ';', ':', '.']

            x = x_coords[coord]
            y = y_coords[coord]
            z = z_coords[coord]

            closeness = math.sqrt((sunx - x)**2 + (suny - y)**2 + (sunz - z)**2)
            t = min(closeness / math.dist((-100, 100, 0), (100, -100, 200)), 1.0)

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

            screen_x, screen_y = project_3d_to_2d(x, y, z)
            plt.scatter([screen_x], [screen_y], marker=marker, color=color)

def line(start, end, d='No', color='green', steps=1000):
    """
    Generate coordinates between two points.
    
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

def square(start_x=-40, start_y=-40, start_z=0, side_length=80, d='No', color='green', solid=False):
    line((start_x + side_length, start_y, start_z), (start_x + side_length,  start_y + side_length, start_z), d='No', color=color)
    line((start_x, start_y, start_z), (start_x,  start_y + side_length, start_z), d='No', color=color)
    if solid:
        for i in range(side_length):
            line((start_x, start_y + i, start_z), (start_x + side_length, start_y + i, start_z), d='No', color=color)
    else:
        line((start_x, start_y + side_length, start_z), (start_x + side_length, start_y + side_length, start_z), d='No', color=color)
        line((start_x, start_y, start_z), (start_x + side_length, start_y, start_z), d='No', color=color)

def cube(start_x=-30, start_y=-30, start_z=0, side_length=120, color='green', solid=False):
    # Front square
    square(start_x, start_y, start_z, side_length, d='No', color=color, solid=solid)
    # Back square (moved in z direction by side_length)
    square(start_x, start_y, start_z + side_length, side_length, d='No', color=color, solid=solid)
    if solid:
        for i in range(side_length):
            # Connect front right edge to back right edge
            line((start_x + side_length, start_y + i, start_z), (start_x + side_length, start_y + i, start_z + side_length), 'Yes', color=color)
            # Connect front top edge to back top edge
            line((start_x + i, start_y + side_length, start_z), (start_x + i, start_y + side_length, start_z + side_length), 'Yes', color=color)      
    else:
        # Connect the 4 corners
        line((start_x, start_y, start_z), (start_x, start_y, start_z + side_length), 'Yes', color=color)
        line((start_x + side_length, start_y, start_z), (start_x + side_length, start_y, start_z + side_length), 'Yes', color=color)
        line((start_x, start_y + side_length, start_z), (start_x, start_y + side_length, start_z + side_length), 'Yes', color=color)
        line((start_x + side_length, start_y + side_length, start_z), (start_x + side_length, start_y + side_length, start_z + side_length), 'Yes', color=color)


def circle(center_x=0, center_y=0, center_z=0, radius=30, color='cyan'):
    num_points = 400 # More points improve granularity for segments
    # --- Generate the angles (from 0 to 2*PI) ---
    angles = np.linspace(0, 2 * math.pi, num_points + 1)

# --- Calculate x and y coordinates ---
    for i in range(radius):
        x_coords = np.array([center_x + i * math.cos(angle) for angle in angles])
        y_coords = np.array([center_y + i * math.sin(angle) for angle in angles])
        z_coords = np.array([center_z for _ in angles])
        trace(x_coords, y_coords, z_coords, d='No', color=color)

def draw_scene():
    """Draw the entire scene"""
    plt.clf()  # Clear the plot
    plt.canvas_color("black")
    plt.frame(False)
    plt.xticks([])
    plt.yticks([])
    plt.xlim(-100, 100)
    plt.ylim(-100, 100)
    
    # Draw light
    light_x, light_y = project_3d_to_2d(sunx, suny, sunz)
    plt.scatter([light_x], [light_y], marker='Light', color='red')
    
    # Draw objects
    circle()
    
    # Show camera info
    plt.title(f"Camera: X={camera_x:.0f} Y={camera_y:.0f} Z={camera_z:.0f} Rot={math.degrees(camera_rotation_y):.0f}° | WASD=move QE=up/down Arrow=rotate ESC=quit")
    
    plt.show()

def main():
    global camera_x, camera_y, camera_z, camera_rotation_y
    
    # Set up terminal for raw input
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setcbreak(fd)
        
        print("Controls:")
        print("W/S - Forward/Backward")
        print("A/D - Left/Right")
        print("Q/E - Down/Up")
        print("Arrow Keys - Rotate camera")
        print("ESC - Quit")
        print("\nPress any key to start...")
        sys.stdin.read(1)
        
        running = True
        move_speed = 10
        rotate_speed = 0.1
        
        while running:
            draw_scene()
            
            # Check for input
            key = get_key()
            
            if key:
                if key == '\x1b[A':  # Up arrow
                    pass
                elif key == '\x1b[B':  # Down arrow
                    pass
                elif key == '\x1b[C':  # Right arrow
                    camera_rotation_y -= rotate_speed
                elif key == '\x1b[D':  # Left arrow
                    camera_rotation_y += rotate_speed
                elif key == '\x1b':  # ESC alone
                    running = False
                elif key.lower() == 'w':
                    # Move forward (in direction camera is facing)
                    camera_x += move_speed * math.sin(camera_rotation_y)
                    camera_z -= move_speed * math.cos(camera_rotation_y)
                elif key.lower() == 's':
                    # Move backward
                    camera_x -= move_speed * math.sin(camera_rotation_y)
                    camera_z += move_speed * math.cos(camera_rotation_y)
                elif key.lower() == 'a':
                    # Strafe left
                    camera_x -= move_speed * math.cos(camera_rotation_y)
                    camera_z -= move_speed * math.sin(camera_rotation_y)
                elif key.lower() == 'd':
                    # Strafe right
                    camera_x += move_speed * math.cos(camera_rotation_y)
                    camera_z += move_speed * math.sin(camera_rotation_y)
                elif key.lower() == 'q':
                    camera_y -= move_speed
                elif key.lower() == 'e':
                    camera_y += move_speed
                elif key == 'q' or key == '\x03':  # Ctrl+C
                    running = False
    
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nExited camera control mode")

if __name__ == "__main__":
    main()