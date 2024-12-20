import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import Tk, Scale, Label, Button, ttk, Frame
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import pandas as pd
from tkinter import messagebox

class GyroscopeSimulation:
    def __init__(self):
        # Constants
        self.MASS = 1.0
        self.RADIUS = 0.2
        self.SPIN_RATE = 100  # Initial RPM
        self.TORQUE = 0.05
        self.TIME_STEP = 0.01
        
        # State variables
        self.precession_angle = 0
        self.precession_rate = 0
        self.time_data = []
        self.precession_data = []
        self.torque_data = []
        self.history_data = []  # New variable for history
        self.is_paused = False
        self.start_time = time.time()
        
        self.setup_gui()
        self.setup_plots()
        self.setup_3d_gyroscope()

    def setup_gui(self):
        self.root = Tk()
        self.root.title("Real-Time Gyroscope Precession Simulation")
        self.root.configure(bg='#2b2b2b')

        # Create main frames
        control_frame = Frame(self.root, bg='#2b2b2b', padx=15, pady=15)
        control_frame.pack(side='left', fill='y', padx=10, pady=10)

        # Style configuration
        style = ttk.Style()
        style.configure("TScale", background='#2b2b2b', sliderlength=25, width=30)
        style.configure("TLabel", background='#2b2b2b', foreground='white')
        style.configure("TButton", font=('Helvetica', 12), padding=10, width=15)

        # Controls
        self.spin_rate_slider = Scale(
            control_frame, from_=10, to=1000, orient='horizontal',
            label="Spin Rate (RPM)", bg='#2b2b2b', fg='white', length=300
        )
        self.spin_rate_slider.set(self.SPIN_RATE)
        self.spin_rate_slider.pack(pady=10)

        self.torque_slider = Scale(
            control_frame, from_=0, to=1, orient='horizontal',
            label="Applied Torque (N·m)", resolution=0.01,
            bg='#2b2b2b', fg='white', length=300
        )
        self.torque_slider.set(self.TORQUE)
        self.torque_slider.pack(pady=10)

        # Labels with real-time data
        self.precession_label = Label(
            control_frame,
            text="Precession Angle: 0.00 rad", font=('Helvetica', 14),
            bg='#2b2b2b', fg='white'
        )
        self.precession_label.pack(pady=5)

        # Control buttons
        btn_frame = Frame(control_frame, bg='#2b2b2b')
        btn_frame.pack(pady=15)

        self.pause_button = Button(
            btn_frame, text="Pause", command=self.toggle_pause,
            bg='#4a4a4a', fg='white'
        )
        self.pause_button.pack(side='left', padx=15)

        self.reset_button = Button(
            btn_frame, text="Reset", command=self.reset_simulation,
            bg='#4a4a4a', fg='white'
        )
        self.reset_button.pack(side='left', padx=15)

        # Report button to generate report
        self.report_button = Button(
            btn_frame, 
            text="Generate Report", 
            command=self.generate_report,
            bg='#4a4a4a', 
            fg='white'
        )
        self.report_button.pack(side='left', padx=15)

        # History table (Treeview) for displaying data
        self.history_frame = Frame(control_frame, bg='#2b2b2b', padx=10, pady=10)
        self.history_frame.pack(side='bottom', fill='both', expand=True, padx=10, pady=10)

        self.history_tree = ttk.Treeview(self.history_frame, columns=("Time", "Torque", "Precession"), show="headings")
        self.history_tree.heading("Time", text="Time (s)", anchor="w")
        self.history_tree.heading("Torque", text="Torque (N·m)", anchor="w")
        self.history_tree.heading("Precession", text="Precession (rad)", anchor="w")

        self.history_tree.column("Time", width=150, anchor="w")
        self.history_tree.column("Torque", width=150, anchor="w")
        self.history_tree.column("Precession", width=150, anchor="w")

        self.history_tree.pack(side='left', fill='both', expand=True)

        # Add professional styling for the title
        title_label = Label(
            self.root,
            text="Real-Time Gyroscope Precession And Simulation",
            font=('Helvetica', 24, 'bold'),
            bg='#2b2b2b',
            fg='#00ff99',
            pady=20
        )
        title_label.pack(side='top')

        # Enhanced tree view styling
        style.configure(
            "Treeview",
            background="#3d3d3d",
            foreground="white",
            fieldbackground="#3d3d3d",
            rowheight=25
        )
        style.configure(
            "Treeview.Heading",
            background="#4a4a4a",
            foreground="white",
            relief="flat"
        )
        style.map("Treeview", background=[('selected', '#007acc')])

        # Add gradient effect to buttons
        def on_enter(e):
            e.widget.config(bg='#007acc')

        def on_leave(e):
            e.widget.config(bg='#4a4a4a')

        for button in [self.pause_button, self.reset_button, self.report_button]:
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            button.config(
                relief='raised',
                borderwidth=3,
                font=('Helvetica', 11, 'bold')
            )

        # Add tooltips for controls
        tooltip_style = {
            'bg': '#1e1e1e',
            'fg': 'white',
            'pady': 5,
            'padx': 5,
            'relief': 'solid'
        }

        def create_tooltip(widget, text):
            tip = Label(self.root, text=text, **tooltip_style)
            def enter(event):
                tip.place(x=widget.winfo_rootx(), y=widget.winfo_rooty() - 30)
            def leave(event):
                tip.place_forget()
            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)

        create_tooltip(self.spin_rate_slider, "Adjust the gyroscope's rotation speed")
        create_tooltip(self.torque_slider, "Control the applied torque magnitude")

        # Optimize history table size
        self.history_tree.configure(height=6)  # Reduce number of visible rows
        self.history_tree.column("Time", width=120)
        self.history_tree.column("Torque", width=120)
        self.history_tree.column("Precession", width=120)

    def setup_plots(self):
        self.fig = plt.figure(figsize=(15, 10))
        gs = gridspec.GridSpec(2, 2)

        graph_title_style = {'color': 'white', 'fontsize': 14, 'fontweight': 'bold', 'fontfamily': 'Helvetica'}
        axis_label_style = {'color': 'white', 'fontsize': 10, 'fontfamily': 'Helvetica'}

        # Torque vs Precession plot
        self.ax_torque = self.fig.add_subplot(gs[0, 0])
        self.ax_torque.set_title("Torque vs Precession", **graph_title_style)
        self.ax_torque.set_xlabel("Torque (N·m)", **axis_label_style)
        self.ax_torque.set_ylabel("Precession (rad)", **axis_label_style)
        self.torque_line, = self.ax_torque.plot([], [], 'g-', lw=2)

        # Time vs Precession plot
        self.ax_time = self.fig.add_subplot(gs[0, 1])
        self.ax_time.set_title("Precession vs Time", **graph_title_style)
        self.ax_time.set_xlabel("Time (s)", **axis_label_style)
        self.ax_time.set_ylabel("Precession (rad)", **axis_label_style)
        self.time_line, = self.ax_time.plot([], [], 'b-', lw=2)

        # 3D Gyroscope visualization
        self.ax_3d = self.fig.add_subplot(gs[1, :], projection='3d')
        self.ax_3d.set_title("3D Gyroscope", **graph_title_style)

        # Style the plots
        self.fig.patch.set_facecolor('#2b2b2b')
        for ax in [self.ax_torque, self.ax_time, self.ax_3d]:
            ax.set_facecolor('#2b2b2b')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')

        # Add subtle padding and margins to graphs
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1, wspace=0.3, hspace=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='right', fill='both', expand=True)

    def setup_3d_gyroscope(self):
        # Initialize 3D gyroscope components
        self.disk_radius = 1
        theta = np.linspace(0, 2*np.pi, 100)
        self.disk_x = self.disk_radius * np.cos(theta)
        self.disk_y = self.disk_radius * np.sin(theta)
        self.disk_z = np.zeros_like(theta)

        # Initial axis
        self.axis_length = 2
        self.axis_x = np.array([0, 0])
        self.axis_y = np.array([0, 0])
        self.axis_z = np.array([-self.axis_length, self.axis_length])

    def update_3d_gyroscope(self):
        self.ax_3d.cla()

        # Update rotation matrix based on precession
        c = np.cos(self.precession_angle)
        s = np.sin(self.precession_angle)

        # Rotate disk and axis
        rotated_x = self.disk_x * c - self.disk_y * s
        rotated_y = self.disk_x * s + self.disk_y * c

        # Plot disk
        self.ax_3d.plot(rotated_x, rotated_y, self.disk_z, 'g-', lw=2)

        # Plot axis
        rotated_axis_x = self.axis_x * c - self.axis_y * s
        rotated_axis_y = self.axis_x * s + self.axis_y * c
        self.ax_3d.plot(rotated_axis_x, rotated_axis_y, self.axis_z, 'r-', linewidth=2)

        # Set view limits and labels
        self.ax_3d.set_xlim(-2, 2)
        self.ax_3d.set_ylim(-2, 2)
        self.ax_3d.set_zlim(-2, 2)
        self.ax_3d.set_xlabel('X', fontsize=12)
        self.ax_3d.set_ylabel('Y', fontsize=12)
        self.ax_3d.set_zlabel('Z', fontsize=12)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.config(text="Resume" if self.is_paused else "Pause")

    def reset_simulation(self):
        self.precession_angle = 0
        self.time_data = []
        self.precession_data = []
        self.torque_data = []
        self.history_data = []  # Reset history
        self.start_time = time.time()
        self.update_display()

    def update_display(self):
        self.precession_label.config(
            text=f"Precession Angle: {self.precession_angle:.2f} rad"
        )

    def update_history(self):
        """Update the history table with new data."""
        current_time = time.time() - self.start_time
        torque = self.torque_slider.get()
        self.history_data.append([round(current_time, 2), round(torque, 2), round(self.precession_angle, 2)])

        # Update the table with new data
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        for row in self.history_data[-10:]:  # Show only the last 10 entries
            self.history_tree.insert('', 'end', values=row)

    def simulate(self):
        if not self.is_paused:
            # Update physics
            angular_velocity = 2 * np.pi * self.spin_rate_slider.get() / 60
            torque = self.torque_slider.get()
            
            self.precession_rate = torque / (self.MASS * self.RADIUS**2 * angular_velocity)
            self.precession_angle += self.precession_rate * self.TIME_STEP
            
            # Update data arrays
            current_time = time.time() - self.start_time
            self.time_data.append(current_time)
            self.precession_data.append(self.precession_angle)
            self.torque_data.append(torque)
            
            # Update plots
            self.torque_line.set_data(self.torque_data, self.precession_data)
            self.time_line.set_data(self.time_data, self.precession_data)

            # Update axis limits
            self.ax_torque.relim()
            self.ax_torque.autoscale_view()
            self.ax_time.relim()
            self.ax_time.autoscale_view()

            # Update 3D visualization
            self.update_3d_gyroscope()

            # Update display
            self.update_display()

            # Update history
            self.update_history()

            self.canvas.draw()

        self.root.after(int(self.TIME_STEP * 1000), self.simulate)

    def run(self):
        self.simulate()
        self.root.mainloop()

    def generate_report(self):
        if not self.history_data:
            messagebox.showinfo("Report", "No data available yet!")
            return
            
        df = pd.DataFrame(self.history_data, columns=['Time', 'Torque', 'Precession'])
        
        stats = {
            'Torque': {
                'Average': df['Torque'].mean(),
                'Maximum': df['Torque'].max(),
                'Minimum': df['Torque'].min()
            },
            'Precession': {
                'Average': df['Precession'].mean(),
                'Maximum': df['Precession'].max(),
                'Minimum': df['Precession'].min()
            }
        }
        
        report = "Simulation Report\n\n"
        report += "Torque Statistics (N·m):\n"
        report += f"  Average: {stats['Torque']['Average']:.2f}\n"
        report += f"  Maximum: {stats['Torque']['Maximum']:.2f}\n"
        report += f"  Minimum: {stats['Torque']['Minimum']:.2f}\n\n"
        report += "Precession Statistics (rad):\n"
        report += f"  Average: {stats['Precession']['Average']:.2f}\n"
        report += f"  Maximum: {stats['Precession']['Maximum']:.2f}\n"
        report += f"  Minimum: {stats['Precession']['Minimum']:.2f}\n"
        
        messagebox.showinfo("Simulation Report", report)
        
        # Optionally save to CSV
        df.to_csv('gyroscope_simulation_data.csv', index=False)

if __name__ == "__main__":
    sim = GyroscopeSimulation()
    sim.run()
