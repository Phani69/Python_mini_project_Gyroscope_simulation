# Real-Time Gyroscope Precession Simulation

This project simulates the real-time behavior of a gyroscope under precession, including its response to varying spin rates and applied torques. The application offers an intuitive graphical interface with interactive controls, live plots, and 3D visualization to enhance understanding of gyroscopic motion.

## Features

- **Interactive Controls**: 
  - Adjust spin rate (RPM) and applied torque (N·m) using sliders.
  - Pause, reset, and generate reports via buttons.
  
- **Live Visualization**:
  - 3D gyroscope model updated in real time.
  - Graphs for:
    - Torque vs. Precession
    - Precession vs. Time

- **Data History**:
  - A table to display real-time simulation data (time, torque, precession angle).
  - Saves simulation data to a CSV file.

- **Report Generation**:
  - Provides statistical summaries (average, max, min) of torque and precession.
  - Displays the report in the GUI and optionally exports to a file.

## Requirements

- Python 3.7 or higher
- Required Python packages:
  - `numpy`
  - `matplotlib`
  - `pandas`
  - `tkinter`

Install dependencies using pip:

```bash
pip install numpy matplotlib pandas
