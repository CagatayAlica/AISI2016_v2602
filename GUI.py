import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CUFSM_Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Cold-Formed Steel Analysis Tool")
        self.root.geometry("900x600")

        # Main Containers
        left_frame = ttk.Frame(root, padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew")

        right_frame = ttk.Frame(root, padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")

        # --- LEFT PORTION: INPUTS ---
        ttk.Label(left_frame, text="Geometric Properties", font=('bold', 12)).grid(row=0, columnspan=2, pady=10)

        inputs = ["Web Height (h)", "Flange Width (b)", "Lip Length (d)", "Inner Radius (r)", "Thickness (t)"]
        self.entries = {}

        for i, label in enumerate(inputs):
            ttk.Label(left_frame, text=label).grid(row=i + 1, column=0, sticky="w", pady=5)
            entry = ttk.Entry(left_frame)
            entry.grid(row=i + 1, column=1, padx=5)
            self.entries[label] = entry

        ttk.Label(left_frame, text="Steel Grade", font=('bold', 10)).grid(row=7, column=0, pady=20, sticky="w")
        self.grade_combo = ttk.Combobox(left_frame, values=["S235", "S355", "S450", "G550"])
        self.grade_combo.grid(row=7, column=1)

        # --- RIGHT PORTION: CHART & RESULTS ---
        # Signature Curve Placeholder
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.ax.set_title("Signature Curve")
        self.ax.set_xlabel("Half-Wavelength (mm)")
        self.ax.set_ylabel("Load Factor (λ)")
        self.ax.set_xscale('log')

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack()

        # Results Area
        results_frame = ttk.LabelFrame(right_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill="x", pady=20)

        ttk.Label(results_frame, text="Local Buckling (Mcrl): ---").pack(anchor="w")
        ttk.Label(results_frame, text="Distortional Buckling (Mcrd): ---").pack(anchor="w")
        ttk.Label(results_frame, text="Global Buckling (Mcre): ---").pack(anchor="w")

        # --- BOTTOM PORTION: BUTTONS ---
        bottom_frame = ttk.Frame(root, padding="10")
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        ttk.Button(bottom_frame, text="Material Props", command=lambda: self.open_window("Material")).pack(side="left",
                                                                                                           expand=True)
        ttk.Button(bottom_frame, text="Section Analysis", command=lambda: self.open_window("Section")).pack(side="left",
                                                                                                            expand=True)
        ttk.Button(bottom_frame, text="Member Design", command=lambda: self.open_window("Design")).pack(side="left",
                                                                                                        expand=True)

    def open_window(self, name):
        new_window = tk.Toplevel(self.root)
        new_window.title(f"{name} Parameters")
        new_window.geometry("300x200")
        ttk.Label(new_window, text=f"This is the {name} form").pack(pady=50)


if __name__ == "__main__":
    root = tk.Tk()
    app = CUFSM_Interface(root)
    root.mainloop()