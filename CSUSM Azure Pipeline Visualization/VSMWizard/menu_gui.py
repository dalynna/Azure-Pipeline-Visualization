import tkinter as tk
import os
import shutil
import webbrowser
from tkinter import filedialog, messagebox, simpledialog
import xml.etree.ElementTree as ET
import json
import re

class MenuGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VSM Wizard")

        # Label for the latest VSM (Initially hidden)
        self.label_latest_vsm = tk.Label(self.root, text="", font=("Arial", 14))
        self.label_latest_vsm.pack(pady=5)  # Pack at the top initially

        # Frame for the top row buttons
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        # Create buttons
        self.btn_view_latest = tk.Button(top_frame, text="View Latest VSM", command=self.view_latest, state=tk.DISABLED, disabledforeground='red')
        self.btn_view_latest.pack(side=tk.LEFT, padx=5)

        self.btn_search_vsm = tk.Button(top_frame, text="Search VSM", command=self.search_vsm)
        self.btn_search_vsm.pack(side=tk.LEFT, padx=5)
        self.btn_search_vsm.pack_forget()  # Hide initially

        btn_use_existing = tk.Button(self.root, text="Generate VSM from Existing Configuration", command=self.use_existing)
        btn_generate_config = tk.Button(self.root, text="Generate Configuration File", command=self.open_config_window)  # Updated button
        btn_upload_config = tk.Button(self.root, text="Upload VSM Configuration File", command=self.upload_config)
        btn_update_vsm = tk.Button(self.root, text="Update VSM with Save File", command=self.update_vsm)

        # Arrange buttons vertically
        btn_use_existing.pack(pady=10)
        btn_generate_config.pack(pady=10)  # Pack the updated button
        btn_upload_config.pack(pady=10)
        btn_update_vsm.pack(pady=10)

        # Bring window to front
        self.root.focus_force()

        # Center the window
        self.center_window(380, 290)

        # Update button state based on file existence
        self.update_button_state()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def update_button_state(self):
        alias = 'latest.svg'
        vsm_files = [f for f in os.listdir() if f.endswith('.svg')]

        # Check if a VSM exists
        if os.path.islink(alias) and os.path.exists(os.readlink(alias)):
            latest_vsm = os.readlink(alias)
            self.btn_view_latest.config(state=tk.NORMAL)  # Enable button
            self.label_latest_vsm.config(text=f"Latest: {latest_vsm}")  # Update label text
        else:
            self.btn_view_latest.config(state=tk.DISABLED)  # Disable button
            self.label_latest_vsm.config(text="")  # Clear label text

        # Show "Search VSM" button if more than two VSM files exist
        if len(vsm_files) >= 2:
            self.btn_search_vsm.pack(side=tk.LEFT, padx=5)
        else:
            self.btn_search_vsm.pack_forget()

    def search_vsm(self):
        file_path = filedialog.askopenfilename(filetypes=[("VSM Files", "*.svg")])
        if file_path:
            webbrowser.open('file://' + os.path.abspath(file_path))

    def view_latest(self):
        alias = 'latest.svg'
        if os.path.islink(alias) and os.path.exists(os.readlink(alias)):
            webbrowser.open('file://' + os.path.abspath(os.readlink(alias)))
        else:
            print("The alias does not exist or is broken. Try running as administrator.")

    def open_config_window(self):
        # Create a new Toplevel window
        config_window = tk.Toplevel(self.root)
        config_window.title("Generate Configuration File")
        config_window.geometry("1100x500")  # Adjusted size for larger input boxes

        # Add a canvas and scrollbar for scrolling
        canvas = tk.Canvas(config_window)
        scrollbar = tk.Scrollbar(config_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Configure the canvas and scrollbar
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store entries for later use
        pipeline_entries = []
        yaml_entries = []
        template_entry = None

        # Add "Plus" and "Minus" buttons above the pipeline rows
        btn_add_row = tk.Button(scrollable_frame, text="+ Add Pipeline", command=lambda: add_pipeline_row())
        btn_add_row.grid(row=0, column=0, padx=5, pady=10)  # Adjusted column span and padding

        btn_remove_row = tk.Button(scrollable_frame, text="- Remove Pipeline", command=lambda: remove_pipeline_row())
        btn_remove_row.grid(row=0, column=1, padx=5, pady=10)  # Placed in the next column with reduced padding

        # Function to add a new row
        def add_pipeline_row():
            row = len(pipeline_entries) + 1  # Start rows after the buttons
            tk.Label(scrollable_frame, text=f"Pipeline {row} Name:", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry_pipeline_name = tk.Entry(scrollable_frame, width=20)
            entry_pipeline_name.grid(row=row, column=1, padx=10, pady=5)
            pipeline_entries.append(entry_pipeline_name)

            tk.Label(scrollable_frame, text=f"YAML File Path {row}:", font=("Arial", 12)).grid(row=row, column=2, sticky="w", padx=10, pady=5)
            frame_yaml = tk.Frame(scrollable_frame)
            frame_yaml.grid(row=row, column=3, padx=10, pady=5, sticky="w")
            entry_yaml_path = tk.Entry(frame_yaml, width=45)
            entry_yaml_path.pack(side=tk.LEFT, padx=5)
            btn_select_yaml = tk.Button(frame_yaml, text="Select File", command=lambda e=entry_yaml_path: self.select_file(e))
            btn_select_yaml.pack(side=tk.LEFT)
            yaml_entries.append(entry_yaml_path)

            # Add delete button for all rows except the first one
            if row > 1:
                btn_delete = tk.Button(scrollable_frame, text="×", command=lambda r=row: delete_row(r))
                btn_delete.grid(row=row, column=4, padx=5, pady=5)

        # Function to remove the last row
        def remove_pipeline_row():
            print("remove_pipeline_row called")
            print(f"Current entries: {len(pipeline_entries)}")
            if pipeline_entries and yaml_entries and len(pipeline_entries) > 1:  # Only allow removal if more than 1 row exists
                print("Condition passed, removing row")
                # Remove the last pipeline name label and entry
                last_pipeline_entry = pipeline_entries.pop()
                last_pipeline_entry.grid_forget()  # Remove the entry
                last_pipeline_entry_label = scrollable_frame.grid_slaves(row=len(pipeline_entries) + 1, column=0)[0]
                last_pipeline_entry_label.grid_forget()  # Remove the label

                # Remove the last YAML file path label, entry, and button
                last_yaml_entry = yaml_entries.pop()
                last_yaml_entry.master.grid_forget()  # Remove the frame containing the entry and button
                last_yaml_label = scrollable_frame.grid_slaves(row=len(yaml_entries) + 1, column=2)[0]
                last_yaml_label.grid_forget()  # Remove the label

                # Remove the delete button if it exists
                delete_buttons = scrollable_frame.grid_slaves(row=len(pipeline_entries) + 1, column=4)
                if delete_buttons:
                    delete_buttons[0].grid_forget()

                # Update the row numbers in the remaining labels
                for i in range(1, len(pipeline_entries) + 1):
                    # Update Pipeline label
                    pipeline_label = scrollable_frame.grid_slaves(row=i, column=0)[0]
                    pipeline_label.config(text=f"Pipeline {i} Name:")
                    # Update YAML label
                    yaml_label = scrollable_frame.grid_slaves(row=i, column=2)[0]
                    yaml_label.config(text=f"YAML File Path {i}:")

        def delete_row(row_num):
            if len(pipeline_entries) <= 1:  # Keep at least one row
                return

            # Remove entries from lists
            index = row_num - 1  # Convert row number to zero-based index
            if index >= len(pipeline_entries):
                return  # Prevent out of range errors
            
            pipeline_entries.pop(index)
            yaml_entries.pop(index)

            # Remove all widgets in the row
            for widget in scrollable_frame.grid_slaves(row=row_num):
                widget.grid_forget()
                if isinstance(widget, tk.Frame):  # For the YAML frame containing entry and button
                    for child in widget.winfo_children():
                        child.destroy()
                    widget.destroy()

            # Shift up remaining rows and update their numbers and delete buttons
            for i in range(row_num + 1, len(pipeline_entries) + 2):
                # Update row number for all widgets in this row
                for widget in scrollable_frame.grid_slaves(row=i):
                    # Move the widget up one row
                    widget.grid(row=i-1)
                    
                    # Update the labels with new row numbers
                    if isinstance(widget, tk.Label):
                        if "Pipeline" in widget.cget("text"):
                            widget.config(text=f"Pipeline {i-1} Name:")
                        elif "YAML" in widget.cget("text"):
                            widget.config(text=f"YAML File Path {i-1}:")

            # Update delete button commands
            for i in range(2, len(pipeline_entries) + 1):
                delete_buttons = scrollable_frame.grid_slaves(row=i, column=4)
                if delete_buttons:
                    delete_buttons[0].configure(command=lambda r=i: delete_row(r))

        # Add initial row
        add_pipeline_row()

        # Add a blank row for spacing above "Template Dictionary"
        tk.Label(scrollable_frame, text="").grid(row=101, column=0, pady=10)  # Blank row for spacing

        # Add a text box for the template dictionary
        tk.Label(scrollable_frame, text="Template Dictionary:", font=("Arial", 12)).grid(row=102, column=0, sticky="w", padx=10, pady=5)
        frame_template = tk.Frame(scrollable_frame)
        frame_template.grid(row=102, column=1, columnspan=3, padx=10, pady=5, sticky="w")
        template_entry = tk.Entry(frame_template, width=50)
        template_entry.pack(side=tk.LEFT, padx=5)
        btn_select_template = tk.Button(frame_template, text="Select File", command=lambda: self.select_file(template_entry))
        btn_select_template.pack(side=tk.LEFT)

        # Add a blank row for spacing
        tk.Label(scrollable_frame, text="").grid(row=103, column=0)  # Blank row for spacing

        # Add a button to generate the JSON file
        def generate_file():
            # Collect pipeline names and YAML file paths
            pipelines = []
            for i, (pipeline_entry, yaml_entry) in enumerate(zip(pipeline_entries, yaml_entries)):
                pipeline_name = pipeline_entry.get()
                yaml_path = yaml_entry.get()
                if not pipeline_name or not yaml_path:
                    messagebox.showerror("Error", f"Pipeline {i + 1}: Both fields are required.")
                    return
                pipelines.append([pipeline_name, yaml_path])

            # Create the JSON structure
            json_data = {
                "yml_filepath": pipelines,
                "template_dictionary": [
                    "tests/input/reusableTemplates/echo_hello_world.yml"
                ]
            }

            # Define the file path for the config file
            project_root = os.getcwd()
            config_folder = os.path.join(project_root, "config")
            os.makedirs(config_folder, exist_ok=True)  # Ensure the config folder exists
            config_file_path = os.path.join(config_folder, "yml_url_config.json")

            # Check if the file already exists
            if os.path.exists(config_file_path):
                overwrite = messagebox.askyesno(
                    "Overwrite File",
                    "A configuration file named 'yml_url_config.json' already exists. Do you want to overwrite it?"
                )
                if not overwrite:
                    return

            # Save the JSON file with custom formatting
            try:
                with open(config_file_path, "w") as json_file:
                    json_string = json.dumps(json_data, indent=2)
                    # Replace newlines in nested lists with compact formatting
                    json_string = json_string.replace("[\n      ", "[").replace("\n    ]", "]").replace("\n      ", "")
                    json_file.write(json_string)
                messagebox.showinfo("Success", f"Configuration file saved successfully:\n{config_file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration file: {e}")

        # Add the "Generate File" button to the bottom-right corner
        btn_generate = tk.Button(scrollable_frame, text="Generate File", command=generate_file)
        btn_generate.grid(row=104, column=3, sticky="e", padx=10, pady=20)

        # Add the "Close" button to the bottom-left corner
        btn_close = tk.Button(scrollable_frame, text="Close", command=config_window.destroy)
        btn_close.grid(row=104, column=0, sticky="w", padx=10, pady=20)

    def select_file(self, entry_field):
        # Open file dialog and set the selected file path in the entry field
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_field.delete(0, tk.END)
            entry_field.insert(0, file_path)

    def upload_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                cwd = os.getcwd()
                dest_path = os.path.join(cwd, "config", "yml_url_config.json")
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copyfile(file_path, dest_path)
                self.show_success_dialog(dest_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to replace configuration file: {e}")

    def show_success_dialog(self, dest_path):
        success_dialog = tk.Toplevel(self.root)
        success_dialog.title("Success")
        success_dialog.geometry("300x150")

        label = tk.Label(
            success_dialog,
            text=f"Configuration file has been replaced:\n{dest_path}",
            wraplength=280,
            justify="center"
        )
        label.pack(pady=10)

        btn_view_vsm = tk.Button(
            success_dialog,
            text="Generate VSM",
            command=lambda: self.generate_and_close(success_dialog)
        )
        btn_view_vsm.pack(side="left", padx=20, pady=20)

        btn_close = tk.Button(success_dialog, text="Close", command=success_dialog.destroy)
        btn_close.pack(side="right", padx=20, pady=20)

    def generate_and_close(self, dialog):
        dialog.destroy()
        self.use_existing()
    
    def use_existing(self):
        vsm_name = simpledialog.askstring("VSM Name", "Enter a name for the VSM (leave blank for default name):")

        if vsm_name is None:
            return

        if not vsm_name:
            vsm_name = ""
        
        from VSMWizard.main import generate
        error_msg = generate(vsm_name)
        if isinstance(error_msg, str):
            messagebox.showerror("Error", error_msg)
        else:
            self.update_button_state()  # Update button state after generating VSM
            self.view_latest()

    def update_vsm(self):
        ET.register_namespace("","http://www.w3.org/2000/svg")

        # Open file dialog to select SVG and JSON files
        root = tk.Tk()
        root.withdraw()

        # Open file dialog and go to project root
        project_root = os.getcwd()
        svg_file = filedialog.askopenfilename(
            title="Select VSM (SVG File)", 
            filetypes=[("SVG Files", "*.svg")], 
            initialdir=project_root
        )
        if not svg_file:
            print("No SVG file selected.")
            return
        
        json_file = filedialog.askopenfilename(title="Select Save (JSON File)", filetypes=[("JSON Files", "*.json")])
        if not json_file:
            print("No JSON file selected.")
            return

        # Load JSON data
        with open(json_file, "r") as f:
            positions = json.load(f)

        # Parse the SVG file
        tree = ET.parse(svg_file)
        root = tree.getroot()

        ns = {"svg": "http://www.w3.org/2000/svg"}  # Namespace support

        id_updates = {}

        # Find all <g> groups in the SVG
        groups = root.findall(".//{http://www.w3.org/2000/svg}g")

        # Update elements based on JSON
        for item in positions:
            element_id = item["id"]
            new_x = int(item["x"])
            new_y = int(item["y"])

            # Find element by ID
            element = root.find(f".//*[@id='{element_id}']", ns)
            if element is None:
                print(f"Element with id {element_id} not found.")
                continue

            # Find the parent <g> container
            parent_group = None
            for group in groups:
                if element in list(group):
                    parent_group = group
                    break

            if parent_group is not None:
                print(f"Moving group for {element_id}")

                # Find original position
                old_x = int(float(element.get("x", "0")))
                old_y = int(float(element.get("y", "0")))
                dx, dy = new_x - old_x, new_y - old_y

                # Move everything inside <g>
                for child in parent_group:
                    # Update x and y attributes for elements that have them
                    if "x" in child.attrib and "y" in child.attrib:
                        child.set("x", str(int(float(child.get("x"))) + dx))
                        child.set("y", str(int(float(child.get("y"))) + dy))

                    elif "cx" in child.attrib and "cy" in child.attrib:  # for circles
                        child.set("cx", str(int(float(child.get("cx"))) + dx))
                        child.set("cy", str(int(float(child.get("cy"))) + dy))

                    # check children inside anchor for x and y
                    if child.tag.endswith("a"):  # Check if it's an anchor tag
                        for sub_child in child:
                            if "x" in sub_child.attrib and "y" in sub_child.attrib:
                                sub_child.set("x", str(int(float(sub_child.get("x"))) + dx))
                                sub_child.set("y", str(int(float(sub_child.get("y"))) + dy))

                    print(f"Moved {child.tag} inside <g>")

                # Store ID changes for renaming related elements
                new_element_id = f"rect_{new_x}_{new_y}"
                id_updates[element_id] = new_element_id
                element.set("id", new_element_id)

            else:
                # If no <g>, move just the element
                element.set("x", str(new_x))
                element.set("y", str(new_y))
                new_element_id = f"rect_{new_x}_{new_y}"
                id_updates[element_id] = new_element_id
                element.set("id", new_element_id)
                print(f"Updated {element_id}: x={new_x}, y={new_y}")

        # Update related element IDs (post_ and pre_)
        for elem in root.findall(".//*[@id]", ns):
            old_id = elem.get("id")
            if not old_id:
                continue

            # Match both post and pre components
            match = re.match(r"(post_(rect_\d+_\d+))_(pre_(rect_\d+_\d+))(.*)", old_id)
            if match:
                post_full, post_rect_id, pre_full, pre_rect_id, suffix = match.groups()

                new_post_id = id_updates.get(post_rect_id, post_rect_id)
                new_pre_id = id_updates.get(pre_rect_id, pre_rect_id)

                new_id = f"post_{new_post_id}_pre_{new_pre_id}{suffix}"
                elem.set("id", new_id)
                print(f"Updated ID: {old_id} → {new_id}")

        # Save and open the updated SVG
        base_name = os.path.splitext(os.path.basename(svg_file))[0]
        output_file = os.path.join(project_root, f"{base_name}_updated.svg")
        tree.write(output_file)
        print(f"Updated SVG saved as {output_file}")
        webbrowser.open(f'file://{output_file}')


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MenuGUI()
    app.run()
