from algorithms import *

from tkinter import StringVar

import matplotlib.pyplot as plt
import numpy as np

import json
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog

saved = True

def setup():
    root = tk.Tk()
    root.title("Ingressus")
    root.wm_iconwindow()

    def unsave():
        root.title("Ingressus*")
        global saved
        saved = False

    def resave():
        root.title("Ingressus")
        global saved
        saved = True

    root.option_add("*Font", "Courier 10")
    
    u_adding: StringVar = StringVar(value="Hydrogen")

    m_name: StringVar = StringVar()

    i_radius: StringVar = StringVar()
    i_temperature: StringVar = StringVar()
    i_mass: StringVar = StringVar()

    m_name.trace("w", lambda name, index, mode, sv=m_name: unsave())
    i_radius.trace("w", lambda name, index, mode, sv=i_radius: unsave())
    i_temperature.trace("w", lambda name, index, mode, sv=i_temperature: unsave())
    i_mass.trace("w", lambda name, index, mode, sv=i_mass: unsave())
    
    def load_preset():
        m_name.set("Sol")
        i_radius.set("6.96e8")
        i_temperature.set("5778")
        i_mass.set("1.989e30")
        resave()

    def cleanup():
        if not saved:
            if not messagebox.askyesno("Warning", "Unsaved data, are you sure you want to continue?"):
                return
        m_name.set("")
        i_radius.set("")
        i_temperature.set("")
        i_mass.set("")
        resave()

    def exit_cleanly():
        if not saved:
            if not messagebox.askyesno("Warning", "Unsaved data, are you sure you want to exit?"):
                return
        root.destroy()

    def save():
        f = tk.filedialog.asksaveasfile(mode="w", defaultextension=".json")
        if f is None:
            return
        save_object = {
            "name": m_name.get(),
            "radius": i_radius.get(),
            "temperature": i_temperature.get(),
            "mass": i_mass.get()
        }
        f.write(json.dumps(save_object))
        f.close()
        resave()

    def load():
        f = tk.filedialog.askopenfile(mode="r", defaultextension=".json")
        if f is None:
            return
        save_object = json.loads(f.read())
        f.close()
        m_name.set(save_object["name"])
        i_radius.set(save_object["radius"])
        i_temperature.set(save_object["temperature"])
        i_mass.set(save_object["mass"])
        resave()

    def about():
        ui_about = tk.Tk()
        ui_about.title("About")
        ui_about.option_add("*Font", "Courier 10")

        root_frame = tk.Frame(ui_about)
        root_frame.pack(padx=10, pady=10)

        tk.Label(root_frame, text="Ingressus", font=("Courier", 15)).pack()
        tk.Label(root_frame, text="Tool for generating and cataloging information about astral objects.").pack()
        ui_about.mainloop()

    load_preset()

    root.protocol("WM_DELETE_WINDOW", exit_cleanly)

    menubar = tk.Menu(root)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=cleanup)
    file_menu.add_command(label="Open", command=load)
    file_menu.add_command(label="Save", command=save)
    file_menu.add_command(label="Exit", command=exit_cleanly)

    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Enable / Disable Functions", command=lambda: print("Enable / Disable Functions"))
    edit_menu.add_command(label="Load Preset", command=load_preset)

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=about)
    
    root.config(menu=menubar)

    master_frame = tk.Frame(root)
    master_frame.pack(pady=10)

    text_frame = tk.Frame(master_frame)
    text_frame.pack(side=tk.LEFT, anchor=tk.W)

    input_frame = tk.Frame(master_frame)
    input_frame.pack(side=tk.LEFT, anchor=tk.W)

    def add_input(name: str, variable: StringVar):
        tk.Label(text_frame, text=name, width=24, anchor=tk.W).pack(side=tk.TOP, padx=4)
        tk.Entry(input_frame, textvariable=variable, width=20).pack(side=tk.TOP, padx=4)

    def add_empty():
        tk.Label(text_frame, text="", width=24, anchor=tk.W).pack(side=tk.TOP, padx=4)
        tk.Label(input_frame, text="", width=20).pack(side=tk.TOP, padx=4)

    add_input("Name", m_name)
    add_empty()
    add_input("Body Radius (m)", i_radius)
    add_input("Surface Temperature (K)", i_temperature)
    add_input("Mass (kg)", i_mass)
    
    frame_elements = tk.Frame(root, width=44)
    frame_elements.pack(anchor=tk.W, padx=4, pady=4)
    elements_controls = tk.Frame(frame_elements, width=44)
    elements_controls.pack(side=tk.TOP)

    tk.Label(elements_controls, width=18, text="Elements").pack()

    elements = ["Hydrogen", "Helium"]

    om = tk.OptionMenu(elements_controls, u_adding, *elements)
    om.config(width=18)
    om.pack()

    elements_list = tk.Frame(frame_elements, width=44, height=40, relief=tk.SUNKEN)
    elements_list.pack(side=tk.TOP)

    frame_controls = tk.Frame(root)
    frame_controls.pack(anchor=tk.W, padx=4, pady=4)
    tk.Button(frame_controls, text="Calculate", command=lambda: render(float(i_radius.get()), float(i_temperature.get()), float(i_mass.get()), m_name.get())).pack(side=tk.LEFT, padx=4)

    root.mainloop()

def render(radius, temperature, mass, name):
    print("Radius:", radius, "m")
    print("Temperature:", temperature, "K")
    print("Mass:", mass, "kg")

    # Generate spectrum
    spec = spectrum_range(temperature, resolution=300)
    normalize_range(spec)

    wavelengths = sorted([wl for wl in spec.points.keys()])
    intensities = [spec.get(wl) for wl in wavelengths]
    colors = [tuple(c / 255.0 for c in wavelength_to_rgb(wl)) for wl in wavelengths]  # Convert to float RGB

    # Plot spectrum line
    plt.figure(figsize=(10, 5))

    # Intensity curve with colorized segments
    for i in range(1, len(wavelengths)):
        plt.plot(
            [wavelengths[i - 1] * 1e9, wavelengths[i] * 1e9],
            [intensities[i - 1], intensities[i]],
            color=colors[i],
            linewidth=2
        )

    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity")
    plt.title(f"Blackbody Spectrum of {name} at {temperature}K")
    plt.grid(True)

    # Show the spectrum bar below
    ax = plt.gca()
    inset_ax = ax.inset_axes((0.0, -0.25, 1.0, 0.1))  # x, y, width, height

    # Create a horizontal RGB bar (10px tall image)
    spectrum_bar = np.array([colors] * 10)  # shape: (10, 300, 3)
    inset_ax.imshow(spectrum_bar, aspect='auto', extent=(380, 700, 0, 1))
    inset_ax.axis('off')

    plt.tight_layout()
    plt.show()

    perceived = perceived_color(spec)
    plt.figure(figsize=(2, 2))
    plt.imshow([[perceived]])
    plt.axis('off')
    plt.title("Perceived Color")
    plt.show()

if __name__ == "__main__":
    setup()
