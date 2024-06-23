import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox, colorchooser, filedialog
from datetime import datetime
import json
import os
import random

class DisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lamp Display")

        # Path to save lamp data
        self.data_file = "lamp_data.json"
        self.icon_file = "Lampe.ico"

        # Save lamp Data in Dictionary 
        self.lamp_data = {}
        
        # No lamp should be selected
        self.current_lamp = None

        # Load lamp data from json file 
        self.load_lamp_data()

        # Set default or saved icon
        self.set_window_icon()

        # Create widgets
        self.create_widgets()
        
        # Create slider
        self.slider_widget()

        # Check connections to lamps on startup
        self.check_lamp_connections()

    def slider_widget(self):
        
        # Frame for UV slider
        uv_frame = tk.Frame(self.root)
        uv_frame.pack(anchor="w", padx=20, pady=5)
        
        # Create Label for slider 
        self.slider_label_UV = tk.Label(uv_frame, text="UV-Slider:")
        self.slider_label_UV.pack(side=tk.LEFT)
        
        #Creating the slider
        self.current_value_uv = tk.DoubleVar()
        self.slider_uv = ttk.Scale(uv_frame, from_=0, to=100, orient="horizontal", variable=self.current_value_uv, command=self.slider_changed)
        self.slider_uv.pack(side=tk.LEFT, padx=10)

        # Frame for White slider
        white_frame = tk.Frame(self.root)
        white_frame.pack(anchor="w", padx=20, pady=5)
   
       # Create Label for slider 
        self.slider_label_W = tk.Label(white_frame, text="White-Slider:")
        self.slider_label_W.pack(side=tk.LEFT)

        #Creating the slider
        self.current_value_w = tk.DoubleVar()
        self.slider_w = ttk.Scale(white_frame, from_=0, to=100, orient="horizontal", variable=self.current_value_w, command=self.slider_changed)
        self.slider_w.pack(side=tk.LEFT, padx=10)


    def slider_changed(self, event):
        # Update or print slider values as needed
        print("UV Slider value:", self.slider_uv.get())
        print("White Slider value:", self.slider_w.get())
    
    def create_widgets(self):
        # Create menu with sub menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Create Submenu for settings
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        settings_menu.add_command(label="Search Lamp", command=self.search_lamps)
        settings_menu.add_command(label="Remove Lamp", command=self.remove_lamp)
        settings_menu.add_command(label="Change Icon", command=self.change_icon)
        
        # Create Submenu for mode
        mode_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Mode", menu=mode_menu)
        mode_menu.add_command(label="Party Mode", command=self.party_mode)
        mode_menu.add_command(label="Normal Mode", command=self.normal_mode)
        mode_menu.add_command(label="Alert", command=self.alert_mode)
        
        # Create lamp buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, pady=10)

        self.lamp_buttons = {}

        # Create display labels
        self.brightness_label = tk.Label(self.root, text="Brightness: ")
        self.brightness_label.pack(anchor="w", padx=20)

        self.humidity_label = tk.Label(self.root, text="Humidity: ")
        self.humidity_label.pack(anchor="w", padx=20)

        self.temperature_label = tk.Label(self.root, text="Temperature: ")
        self.temperature_label.pack(anchor="w", padx=20)
        
        # Create ID label
        self.ID_label = tk.Label(self.root, text="ID:")
        self.ID_label.pack(anchor="w", padx=20)

        # Create frame for color label and button
        color_frame = tk.Frame(self.root)
        color_frame.pack(anchor="w", padx=20, pady=5)

        self.color_label = tk.Label(color_frame, text="Color: ")
        self.color_label.pack(side=tk.LEFT)

        self.color_button = tk.Button(color_frame, text="Choose Color", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=10)
        
        # Create label for datetime
        self.datetime_label = tk.Label(self.root, text="DateTime: ")
        self.datetime_label.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
              
        # Update datetime every second
        self.update_datetime()

        # Update lamp buttons
        self.update_lamp_buttons()

    def update_lamp_buttons(self):
        # winfo_children: list of children created from self.button_frame 1) delete old button 2) create new button 3) choose lamp
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # item() gives key-lock-pair for creating button with the name in the Dictionary 
        for lamp_number, lamp_info in self.lamp_data.items():
            # lambda gives the Loop Variable to the Method
            btn = tk.Button(self.button_frame, text=lamp_info["name"], command=lambda ln=lamp_number: self.display_lamp_data(ln))
            if not self.check_connection(lamp_number):
                btn.config(highlightbackground="red", highlightthickness=2)
            btn.pack(side=tk.LEFT, padx=5)
            self.lamp_buttons[lamp_number] = btn

        if self.lamp_data and self.current_lamp is None:
            self.display_lamp_data(next(iter(self.lamp_data.keys())))

    def display_lamp_data(self, lamp_number):
        self.current_lamp = lamp_number
        data = self.lamp_data[lamp_number]

        self.brightness_label.config(text=f"Brightness: {self.get_bright(lamp_number)} Lux")
        self.humidity_label.config(text=f"Humidity: {data['humidity']}%")
        self.temperature_label.config(text=f"Temperature: {self.get_temp(lamp_number)} °C")
        self.color_label.config(text=f"Color: {data['color']}")

    def update_datetime(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.config(text=f"DateTime: {current_time}")
        self.root.after(1000, self.update_datetime)

    def search_lamps(self):
        # This function should be implemented to search for new lamps via WLAN
        new_lamps = self.find_new_lamps()  # Placeholder for the search function
        for lamp_id in new_lamps:
            lamp_name = simpledialog.askstring("New Lamp Found", f"Enter the name for the new lamp (ID: {lamp_id}):")
            if lamp_name:
                self.lamp_data[lamp_id] = self.get_lamp_data(lamp_name)
        self.update_lamp_buttons()
        self.save_lamp_data()

    def find_new_lamps(self):
        # Placeholder for the actual WLAN search logic
        # This should return a list of new lamp IDs found via WLAN
        return [random.randint(100, 999)]  # Example of a new lamp ID

    def check_lamp_connections(self):
        # Check if lamps are connected on startup
        for lamp_id in self.lamp_data.keys():
            if not self.check_connection(lamp_id):
                self.lamp_buttons[lamp_id].config(highlightbackground="red", highlightthickness=2)

    def check_connection(self, lamp_id):
        # Placeholder for the function to check if the lamp is connected
        return random.choice([True, False])  # Randomly simulating connection status
    
    def remove_lamp(self):
        if len(self.lamp_data) == 0:
            messagebox.showwarning("Remove Lamp", "No lamps to remove.")
            return

        lamp_names = [info["name"] for info in self.lamp_data.values()]
        lamp_to_remove = simpledialog.askstring("Remove Lamp", "Enter the name of the lamp to remove:", initialvalue=lamp_names[0])

        if lamp_to_remove:
            lamp_id_to_remove = None
            for lamp_id, info in self.lamp_data.items():
                if info["name"] == lamp_to_remove:
                    lamp_id_to_remove = lamp_id
                    break

            if lamp_id_to_remove:
                del self.lamp_data[lamp_id_to_remove]
                self.update_lamp_buttons()
                self.save_lamp_data()
                if self.current_lamp == lamp_id_to_remove:
                    self.current_lamp = next(iter(self.lamp_data.keys()), None)
                    if self.current_lamp:
                        self.display_lamp_data(self.current_lamp)
                    else:
                        self.clear_display()
            else:
                messagebox.showerror("Remove Lamp", "Lamp not found.")

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code and self.current_lamp is not None:
            self.lamp_data[self.current_lamp]["color"] = color_code
            self.color_label.config(text=f"Color: {color_code}")
            self.save_lamp_data()
            self.send_color_to_lamp(self.current_lamp, color_code)  # Send the color to the lamp

    def send_color_to_lamp(self, lamp_id, color_code):
        # Placeholder for the communication to send the color to the lamp
        print(f"Sending color {color_code} to lamp {lamp_id}")
        # self.query_lamp(lamp_id, "color", color_code)

    def change_icon(self):
        icon_path = filedialog.askopenfilename(title="Choose Icon", filetypes=[("ICO files", "*.ico")])
        if icon_path:
            self.icon_file = icon_path
            self.set_window_icon()
            self.save_icon_path()

    def set_window_icon(self):
        if os.path.exists(self.icon_file):
            self.root.iconbitmap(self.icon_file)

    def get_lamp_data(self, name):
        new_lamp_data = {
            "name": name,
            "brightness": random.randint(0, 100),
            "humidity": random.randint(0, 100),
            "temperature": random.randint(15, 30),
            "color": random.choice(["#FFFFFF", "#FFFF00", "#0000FF", "#FF0000", "#00FF00"])
        }
        return new_lamp_data

    def get_temp(self, lamp_id):
        # Placeholder function to return temperature value from the lamp
        return self.query_lamp(lamp_id, "temperature")
    
    def get_bright(self, lamp_id):
        # Placeholder function to return brightness value from the lamp
        return self.query_lamp(lamp_id, "brightness")

    def query_lamp(self, lamp_id, parameter, value=None):
        # Placeholder for the actual query logic
        # Implement the communication with the lamp
        # Right now the values are random generated
        if value is not None:
            print(f"Setting {parameter} to {value} for lamp {lamp_id}")
        return random.randint(0, 100)
    
    def party_mode(self):
        print("Party Mode selected")
        if self.current_lamp is not None:
            self.send_mode_to_lamp(self.current_lamp, "party")

    def normal_mode(self):
        print("Normal Mode selected")
        if self.current_lamp is not None:
            self.send_mode_to_lamp(self.current_lamp, "normal")

    def alert_mode(self):
        print("Alert Mode selected")
        if self.current_lamp is not None:
            self.send_mode_to_lamp(self.current_lamp, "alert")
    
    def send_mode_to_lamp(self, lamp_id, mode):
        # Placeholder for the communication to send the mode to the lamp
        print(f"Sending mode {mode} to lamp {lamp_id}")
        # Implement the communication with the lamp
        # self.query_lamp(lamp_id, "mode", mode)
    
    def clear_display(self):
        self.brightness_label.config(text="Brightness: ")
        self.humidity_label.config(text="Humidity: ")
        self.temperature_label.config(text="Temperature: ")
        self.color_label.config(text="Color: ")

    def save_lamp_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.lamp_data, f)

    def save_icon_path(self):
        with open("icon_path.json", 'w') as f:
            json.dump({"icon_file": self.icon_file}, f)

    def load_lamp_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.lamp_data = json.load(f)
        if (icon_path := "icon_path.json") and os.path.exists(icon_path):
            with open(icon_path, 'r') as f:
                data = json.load(f)
                self.icon_file = data.get("icon_file")

if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayApp(root)
    root.mainloop()
