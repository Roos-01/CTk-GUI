import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox  # For error popups
import re  # For parsing complex inputs like "5 ft 6 in"
import math

# --- Constants ---
# Conversion factors (using cm as a common intermediate where convenient)
FACTORS = {
    'cm': 1.0,
    'm': 100.0,
    'mm': 0.1,
    'inch': 2.54,
    'ft': 30.48,  # 12 inches * 2.54 cm/inch
    'km': 100000.0,  # 1000 m * 100 cm/m
    'mile': 160934.4,  # Based on international mile definition
}

# --- Helper Functions ---
def parse_feet_inches(value_str):
    """Parses strings like '5 ft 6 in', '5ft6in', '5 6', '5' (feet), '5in' into total cm."""
    value_str = value_str.lower().strip()
    feet = 0.0
    inches = 0.0

    # Try regex for patterns like "X ft Y in", "X' Y\""
    match = re.match(r"(\d+(\.\d+)?)\s*(?:ft|'|feet)?\s*(\d+(\.\d+)?)\s*(?:in|\"|inches)?", value_str)
    if match:
        feet = float(match.group(1))
        inches = float(match.group(3))
        return (feet * FACTORS['ft']) + (inches * FACTORS['inch'])

    # Try regex for patterns like "X ft" or "X'"
    match = re.match(r"(\d+(\.\d+)?)\s*(?:ft|'|feet)", value_str)
    if match:
        feet = float(match.group(1))
        return feet * FACTORS['ft']

    # Try regex for patterns like "Y in" or "Y\""
    match = re.match(r"(\d+(\.\d+)?)\s*(?:in|\"|inches)", value_str)
    if match:
        inches = float(match.group(1))
        return inches * FACTORS['inch']

    # Try splitting by space for "X Y" potentially meaning X feet Y inches
    parts = value_str.split()
    try:
        if len(parts) == 2:
            feet = float(parts[0])
            inches = float(parts[1])
            return (feet * FACTORS['ft']) + (inches * FACTORS['inch'])
        elif len(parts) == 1:
            pass  # Fall through to simple float conversion
    except ValueError:
        pass  # Not a simple number or "X Y" number pair

    # If none of the above, try simple float conversion (could be cm, mm, etc.)
    try:
        return float(value_str)  # Treat as base unit if no structure recognised
    except ValueError:
        raise ValueError("Invalid input format for Feet+Inches.")

def format_cm_to_feet_inches(cm_value):
    """Converts cm to a string 'X ft Y in'."""
    if not isinstance(cm_value, (int, float)) or cm_value < 0:
        return "Invalid Input"
    total_inches = cm_value / FACTORS['inch']
    feet = math.floor(total_inches / 12)
    remaining_inches = round(total_inches % 12, 2)  # Round inches to 2 decimal places
    return f"{feet} ft {remaining_inches} in"

# --- Main Application Class ---
class ConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Unit Converter")
        self.geometry("650x300")  # Adjusted size for converter only

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Converter frame

        # --- Conversion Options ---
        self.conversion_options = [
            "Inches to cm",
            "cm to Inches",
            "Feet to cm",
            "cm to Feet",
            "Feet+Inches to cm",
            "cm to Feet+Inches",
            "Meters to Feet",
            "Feet to Meters",
            "km to Miles",
            "Miles to km",
            "Inches to Feet",
            "Feet to Inches",
            "Inches to mm",
            "mm to Inches",
            "cm to mm",
            "mm to cm",
            "Feet to mm",
            "mm to Feet",
            "Inches to Meters",
            "Meters to Inches",
            "Height Converter (ft+in <-> cm)",
        ]
        self.conversion_options.sort()  # Keep the list sorted alphabetically

        # --- Create Frames ---
        self.converter_frame = ctk.CTkFrame(self, corner_radius=10)
        self.converter_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.converter_frame.grid_columnconfigure(1, weight=1)  # Make entry/results expand

        # --- Converter Widgets ---
        self._create_converter_widgets()

    def _create_converter_widgets(self):
        """Creates and grids the widgets for the unit converter section."""
        # Label
        converter_label = ctk.CTkLabel(self.converter_frame, text="Unit Converter", font=ctk.CTkFont(size=16, weight="bold"))
        converter_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 15))

        # Conversion Type Dropdown
        type_label = ctk.CTkLabel(self.converter_frame, text="Conversion:")
        type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.conversion_type_combo = ctk.CTkComboBox(self.converter_frame, values=self.conversion_options, command=self._update_labels)
        self.conversion_type_combo.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        self.conversion_type_combo.set(self.conversion_options[0])  # Set default

        # Input Value
        self.input_label = ctk.CTkLabel(self.converter_frame, text="Input (Inches):")  # Initial label
        self.input_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.input_entry = ctk.CTkEntry(self.converter_frame, placeholder_text="Enter value or 'X ft Y in'")
        self.input_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        # Convert Button
        convert_button = ctk.CTkButton(self.converter_frame, text="Convert", command=self.perform_conversion)
        convert_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Output/Result
        self.output_label = ctk.CTkLabel(self.converter_frame, text="Result (cm):")  # Initial label
        self.output_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.output_value_label = ctk.CTkLabel(self.converter_frame, text="", font=ctk.CTkFont(size=14), anchor="w")
        self.output_value_label.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        self._update_labels()  # Set initial labels based on default selection

    def _update_labels(self, *args):
        """Updates input/output labels based on selected conversion type."""
        selected_conversion = self.conversion_type_combo.get()

        # Handle special 'Height Converter' alias
        if selected_conversion == "Height Converter (ft+in <-> cm)":
            from_unit = "Feet+Inches or cm"
            to_unit = "cm or Feet+Inches"
        else:
            try:
                from_unit, to_unit = selected_conversion.split(" to ")
            except ValueError:
                # Should not happen with the defined list, but good practice
                from_unit = "Input"
                to_unit = "Result"

        self.input_label.configure(text=f"Input ({from_unit}):")
        self.output_label.configure(text=f"Result ({to_unit}):")
        # Clear previous results when changing conversion type
        self.input_entry.delete(0, 'end')
        self.output_value_label.configure(text="")

    def perform_conversion(self):
        """Gets values, performs calculation, and updates the result label."""
        try:
            input_str = self.input_entry.get()
            conversion_type = self.conversion_type_combo.get()
            result = "Error"  # Default error message

            # Handle special 'Height Converter' alias
            if conversion_type == "Height Converter (ft+in <-> cm)":
                # Try parsing as feet+inches first
                try:
                    cm_value = parse_feet_inches(input_str)
                    # If successful, output is cm
                    result = f"{cm_value:.2f} cm"
                except ValueError:
                    # If parsing as ft+in fails, try parsing as simple cm
                    try:
                        cm_value = float(input_str)
                        # If successful, output is ft+in
                        result = format_cm_to_feet_inches(cm_value)
                    except ValueError:
                        result = "Invalid Input for Height"

            # Handle specific complex cases first
            elif "Feet+Inches to cm" in conversion_type:
                cm_value = parse_feet_inches(input_str)
                result = f"{cm_value:.2f}"  # Keep result clean

            elif "cm to Feet+Inches" in conversion_type:
                cm_value = float(input_str)
                result = format_cm_to_feet_inches(cm_value)

            # Handle general cases
            else:
                from_unit_str, to_unit_str = conversion_type.split(" to ")
                from_unit = from_unit_str.lower().replace(" ", "")  # e.g., 'feet' -> 'ft' if needed
                to_unit = to_unit_str.lower().replace(" ", "")

                # Map user-friendly names to internal keys if necessary (e.g., 'miles' to 'mile')
                unit_map = {'feet': 'ft', 'inches': 'inch', 'meters': 'm', 'miles': 'mile'}
                from_unit_key = unit_map.get(from_unit, from_unit)
                to_unit_key = unit_map.get(to_unit, to_unit)

                if from_unit_key not in FACTORS or to_unit_key not in FACTORS:
                    result = "Unsupported Units"
                else:
                    input_value = float(input_str)
                    # Convert input value to base unit (cm)
                    value_in_cm = input_value * FACTORS[from_unit_key]
                    # Convert from base unit (cm) to target unit
                    converted_value = value_in_cm / FACTORS[to_unit_key]
                    result = f"{converted_value:.4f}"  # Format to 4 decimal places

            self.output_value_label.configure(text=result)

        except ValueError as e:
            self.output_value_label.configure(text="Invalid Input")
            messagebox.showerror("Input Error", f"Please enter a valid number or format.\n({e})")
        except Exception as e:
            self.output_value_label.configure(text="Error")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# --- Run the Application ---
if __name__ == "__main__":
    # Set appearance mode (optional, System/Light/Dark)
    ctk.set_appearance_mode("System")  # or "Dark", "Light"
    ctk.set_default_color_theme("blue")  # or "green", "dark-blue"

    app = ConverterApp()
    app.mainloop()
