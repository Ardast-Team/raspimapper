import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from django.conf import settings

class MappingScriptGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Bots Mapping Script Generator")
        master.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        # Input file selection
        ttk.Label(self.master, text="Input File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.input_file_entry = ttk.Entry(self.master, width=50)
        self.input_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)

        # Output file selection
        ttk.Label(self.master, text="Output File:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.output_file_entry = ttk.Entry(self.master, width=50)
        self.output_file_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Browse", command=self.browse_output_file).grid(row=1, column=2, padx=5, pady=5)

        # Mapping type selection
        ttk.Label(self.master, text="Mapping Type:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.mapping_type = tk.StringVar()
        mapping_types = ["Fixed to XML", "XML to Fixed", "CSV to XML", "XML to CSV"]
        self.mapping_type_combo = ttk.Combobox(self.master, textvariable=self.mapping_type, values=mapping_types)
        self.mapping_type_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.mapping_type_combo.set(mapping_types[0])

        # Generate button
        ttk.Button(self.master, text="Generate Mapping Script", command=self.generate_mapping_script).grid(row=3, column=1, padx=5, pady=20)

    def browse_input_file(self):
        filename = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        self.input_file_entry.delete(0, tk.END)
        self.input_file_entry.insert(0, filename)

    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        self.output_file_entry.delete(0, tk.END)
        self.output_file_entry.insert(0, filename)

    def generate_mapping_script(self):
        input_file = self.input_file_entry.get()
        output_file = self.output_file_entry.get()
        mapping_type = self.mapping_type.get()

        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select both input and output files.")
            return

        # TODO: Implement the actual mapping script generation logic here
        # For now, we'll just create a simple template

        template = f"""# Bots Mapping Script
# Mapping Type: {mapping_type}
# Input File: {input_file}
# Output File: {output_file}

def main(inn, out):
    # TODO: Implement the mapping logic here
    pass

if __name__ == "__main__":
    main(inn, out)
"""

        try:
            with open(output_file, "w") as f:
                f.write(template)
            messagebox.showinfo("Success", f"Mapping script template generated: {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate mapping script: {str(e)}")

def run_mapping_script_generator():
    root = tk.Tk()
    MappingScriptGenerator(root)
    root.mainloop()

def launch_mapping_script_generator(request):
    # This function will be called from the Django view
    run_mapping_script_generator()
    return "Mapping Script Generator launched successfully"

if __name__ == "__main__":
    run_mapping_script_generator()