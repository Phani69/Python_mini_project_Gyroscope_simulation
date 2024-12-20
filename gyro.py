import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tkinter import Tk, Scale, Label, Button

# Constants for the Gyroscope
MASS = 1  # Mass of the gyroscope (kg)
RADIUS = 0.2  # Radius of the gyroscope (m)
SPIN_RATE = 100  # Initial spin rate in RPM (revolutions per minute)
TORQUE = 0.05  # Torque applied (N·m)
TIME_STEP = 0.01  # Time step for simulation (seconds)

# Create a figure for plotting
fig, ax = plt.subplots()
ax.set_title("Torque vs Precession Angle")
ax.set_xlabel("Applied Torque (N·m)")
ax.set_ylabel("Precession Angle (radians)")
line, = ax.plot([], [], 'bo', label="Precession vs Torque")
ax.legend()

# Initialize precession parameters
precession_angle = 0
precession_rate = 0
torque_angle = 0
angular_velocity = 2 * np.pi * SPIN_RATE / 60  # Convert RPM to radians per second

# Create a GUI for user input (using Tkinter)
root = Tk()
root.title("Gyroscope Simulation Controls")

# Spin rate slider
spin_rate_slider = Scale(root, from_=10, to_=1000, orient='horizontal', label="Spin Rate (RPM)")
spin_rate_slider.set(SPIN_RATE)
spin_rate_slider.pack()

# Torque slider
torque_slider = Scale(root, from_=0, to_=1, orient='horizontal', label="Applied Torque (N·m)")
torque_slider.set(TORQUE)
torque_slider.pack()

# Label to show current precession angle and torque
precession_label = Label(root, text=f"Precession Angle: {precession_angle:.2f} radians")
precession_label.pack()

torque_label = Label(root, text=f"Applied Torque: {TORQUE:.2f} N·m")
torque_label.pack()

# Spin rate label
spin_rate_label = Label(root, text=f"Spin Rate: {SPIN_RATE} RPM")
spin_rate_label.pack()

# Pause and resume control
is_paused = False

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    pause_button.config(text="Resume" if is_paused else "Pause")

# Pause button
pause_button = Button(root, text="Pause", command=toggle_pause)
pause_button.pack()

# Reset the simulation to initial values
def reset_simulation():
    global precession_angle, angular_velocity
    precession_angle = 0
    angular_velocity = 2 * np.pi * spin_rate_slider.get() / 60  # Reset angular velocity
    precession_label.config(text=f"Precession Angle: {precession_angle:.2f} radians")
    torque_label.config(text=f"Applied Torque: {torque_slider.get():.2f} N·m")
    spin_rate_label.config(text=f"Spin Rate: {spin_rate_slider.get()} RPM")

# Reset button
reset_button = Button(root, text="Reset", command=reset_simulation)
reset_button.pack()

# Update parameters in real-time
def update_parameters():
    global angular_velocity, TORQUE
    angular_velocity = 2 * np.pi * spin_rate_slider.get() / 60  # Convert RPM to radians per second
    TORQUE = torque_slider.get()  # Apply the selected torque value
    precession_label.config(text=f"Precession Angle: {precession_angle:.2f} radians")
    torque_label.config(text=f"Applied Torque: {TORQUE:.2f} N·m")
    spin_rate_label.config(text=f"Spin Rate: {spin_rate_slider.get()} RPM")

# Function to simulate the gyroscopic effect and update the graph
def gyroscope_simulation(i):
    global precession_angle, precession_rate, torque_angle
    
    # Check if the simulation is paused
    if is_paused:
        return line,

    # Update parameters based on slider values
    update_parameters()

    # Calculate precession rate
    precession_rate = TORQUE / (MASS * RADIUS ** 2 * angular_velocity)

    # Apply precession to the gyroscope's angle
    precession_angle += precession_rate * TIME_STEP

    # Update the scatter plot with torque vs precession angle
    line.set_data(torque_slider.get(), precession_angle)
    
    # Update the precession angle display
    precession_label.config(text=f"Precession Angle: {precession_angle:.2f} radians")

    return line,

# Function to update the plot in real-time
def animate():
    # Create an animation of the precession vs torque plot
    ani = FuncAnimation(fig, gyroscope_simulation, frames=200, interval=100, blit=True)
    plt.show()

# Start the animation in a separate thread
import threading
animation_thread = threading.Thread(target=animate)
animation_thread.daemon = True
animation_thread.start()

# Start the Tkinter GUI for controls
root.mainloop()
