import os
import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from VSMWizard.menu_gui import MenuGUI
import xml.etree.ElementTree as ET
import json

class TestMenuGUI(unittest.TestCase):
    def setUp(self):
        # Set up the GUI for testing
        self.app = MenuGUI()
        self.app.root.update()  # Update the GUI to reflect changes

    def tearDown(self):
        # Destroy the GUI after each test
        self.app.root.destroy()

    @patch('VSMWizard.menu_gui.filedialog.askopenfilename')
    @patch('VSMWizard.menu_gui.webbrowser.open')
    def test_view_latest(self, mock_webbrowser_open, mock_askopenfilename):
        # Mock the alias and file existence
        test_file = 'latest.svg'
        with patch('os.path.islink', return_value=True), \
             patch('os.path.exists', return_value=True), \
             patch('os.readlink', return_value=test_file):
            self.app.view_latest()
            expected_path = 'file://' + os.path.abspath(test_file)
            mock_webbrowser_open.assert_called_once_with(expected_path)

    @patch('VSMWizard.menu_gui.filedialog.askopenfilename')
    @patch('VSMWizard.menu_gui.webbrowser.open')
    def test_search_vsm(self, mock_webbrowser_open, mock_askopenfilename):
        # Mock the file dialog to return a specific file path
        test_file = 'test.svg'
        mock_askopenfilename.return_value = test_file
        self.app.search_vsm()
        expected_path = 'file://' + os.path.abspath(test_file)
        mock_webbrowser_open.assert_called_once_with(expected_path)

    @patch('VSMWizard.menu_gui.filedialog.askopenfilename')
    @patch('VSMWizard.menu_gui.messagebox.showinfo')
    @patch('VSMWizard.menu_gui.messagebox.askyesno')  # Add mock for askyesno dialog
    @patch('VSMWizard.menu_gui.os.makedirs')
    @patch('VSMWizard.menu_gui.os.path.exists')  # Add mock for file existence check
    @patch('VSMWizard.menu_gui.open', create=True)
    def test_generate_file(self, mock_open, mock_exists, mock_makedirs, mock_askyesno, mock_showinfo, mock_askopenfilename):
        # Mock the file dialog and JSON file creation
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_askopenfilename.return_value = "test.yaml"
        
        # Test both overwrite scenarios
        test_scenarios = [
            (True, 1),   # User clicks "Yes" to overwrite
            (False, 0)   # User clicks "No" to overwrite
        ]
        
        for should_overwrite, expected_writes in test_scenarios:
            # Reset all mocks for each scenario
            mock_open.reset_mock()
            mock_showinfo.reset_mock()
            mock_exists.reset_mock()
            mock_askyesno.reset_mock()
            
            # Setup mocks for this scenario
            mock_exists.return_value = True  # File exists
            mock_askyesno.return_value = should_overwrite

            # Open the configuration window
            self.app.open_config_window()

            # Get the first row's entries
            pipeline_entry = self.app.root.nametowidget("!toplevel.!canvas.!frame.!entry")
            yaml_frame = self.app.root.nametowidget("!toplevel.!canvas.!frame.!frame")
            yaml_entry = yaml_frame.winfo_children()[0]

            # Fill in the pipeline name and YAML file path
            pipeline_entry.insert(0, "Pipeline1")
            yaml_entry.insert(0, "test.yaml")

            # Find and click the Generate File button
            generate_button = None
            for widget in self.app.root.nametowidget("!toplevel.!canvas.!frame").winfo_children():
                if isinstance(widget, tk.Button) and widget.cget('text') == "Generate File":
                    generate_button = widget
                    break
            
            if not generate_button:
                self.fail("Generate File button not found")
                
            generate_button.invoke()

            # Verify the behavior based on the overwrite choice
            mock_askyesno.assert_called_once_with(
                "Overwrite File",
                "A configuration file named 'yml_url_config.json' already exists. Do you want to overwrite it?"
            )
            
            if should_overwrite:
                # If user chose to overwrite, verify file was written
                mock_open.assert_called_once_with(os.path.join(os.getcwd(), "config", "yml_url_config.json"), "w")
                mock_showinfo.assert_called_once_with("Success", unittest.mock.ANY)
            else:
                # If user chose not to overwrite, verify file was not written
                mock_open.assert_not_called()
                mock_showinfo.assert_not_called()

    @patch('VSMWizard.menu_gui.filedialog.askopenfilename')
    @patch('VSMWizard.menu_gui.shutil.copyfile')
    def test_upload_config(self, mock_copyfile, mock_askopenfilename):
        # Mock the file dialog to return a specific file path
        test_config = 'config.json'
        mock_askopenfilename.return_value = test_config
        test_dir = '/test'
        with patch('os.makedirs'), patch('os.getcwd', return_value=test_dir):
            self.app.upload_config()
            expected_dest = os.path.join(test_dir, 'config', 'yml_url_config.json')
            mock_copyfile.assert_called_once_with(test_config, expected_dest)

    @patch('VSMWizard.menu_gui.simpledialog.askstring')
    @patch('VSMWizard.menu_gui.messagebox.showerror')
    @patch('VSMWizard.menu_gui.MenuGUI.update_button_state')
    @patch('VSMWizard.menu_gui.MenuGUI.view_latest')
    @patch('VSMWizard.main.generate')
    def test_use_existing(self, mock_generate, mock_view_latest, mock_update_button_state, mock_showerror, mock_askstring):
        # Mock the dialog to return a VSM name
        mock_askstring.return_value = 'test_vsm'
        # Mock generate to return None (success case)
        mock_generate.return_value = None
        
        self.app.use_existing()
        
        # Verify generate was called with correct name
        mock_generate.assert_called_once_with('test_vsm')
        # Verify button state was updated
        mock_update_button_state.assert_called_once()
        # Verify view_latest was called
        mock_view_latest.assert_called_once()
        
        # Test error case
        mock_generate.reset_mock()
        mock_update_button_state.reset_mock()
        mock_view_latest.reset_mock()
        
        # Mock generate to return an error message
        mock_generate.return_value = "Error message"
        
        self.app.use_existing()
        
        # Verify error message was shown
        mock_showerror.assert_called_once_with("Error", "Error message")
        # Verify view_latest and update_button_state were not called
        mock_view_latest.assert_not_called()
        mock_update_button_state.assert_not_called()

    @patch('VSMWizard.menu_gui.filedialog.askopenfilename')
    @patch('VSMWizard.menu_gui.webbrowser.open')
    @patch('VSMWizard.menu_gui.ET.parse')
    def test_update_vsm(self, mock_et_parse, mock_webbrowser_open, mock_askopenfilename):
        # Mock file selection dialogs
        mock_askopenfilename.side_effect = [
            'test.svg',  # First call for SVG file
            'positions.json'  # Second call for JSON file
        ]

        # Mock JSON data
        test_json_data = [
            {"id": "rect_50_50", "x": "100", "y": "100"},
            {"id": "rect_150_150", "x": "200", "y": "200"}
        ]
        
        # Mock XML elements and tree
        mock_root = MagicMock()
        mock_tree = MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_et_parse.return_value = mock_tree
        
        # Mock element finding with proper attribute returns
        mock_element = MagicMock()
        mock_element.attrib = {'id': 'post_rect_50_50_pre_rect_150_150'}
        mock_element.get.side_effect = lambda attr: {
            'id': 'post_rect_50_50_pre_rect_150_150',
            'x': '50',
            'y': '50'
        }.get(attr)
        mock_element.set = MagicMock()
        
        # Mock findall to return elements with proper attributes
        mock_root.findall.return_value = [mock_element]
        mock_root.find.return_value = mock_element

        # Mock groups finding
        mock_group = MagicMock()
        mock_group.findall.return_value = [mock_element]
        mock_root.findall.side_effect = lambda path, ns=None: {
            ".//{http://www.w3.org/2000/svg}g": [mock_group],
            ".//*[@id]": [mock_element]
        }.get(path, [])

        # Mock open for JSON file reading
        with patch('builtins.open', unittest.mock.mock_open(read_data=str(test_json_data))), \
             patch('json.load', return_value=test_json_data), \
             patch('os.getcwd', return_value='/test'):
            
            self.app.update_vsm()

            # Verify files were selected
            self.assertEqual(mock_askopenfilename.call_count, 2)
            
            # Verify SVG was parsed
            mock_et_parse.assert_called_once_with('test.svg')
            
            # Verify element positions were updated
            # Check that x and y coordinates were updated
            mock_element.set.assert_any_call('x', '100')
            mock_element.set.assert_any_call('y', '100')
            # Check that ID was updated with new coordinates
            mock_element.set.assert_any_call('id', 'rect_100_100')
            
            # Verify the updated SVG was opened in browser
            mock_webbrowser_open.assert_called_once()
            expected_path = 'file://' + os.path.join('/test', 'test_updated.svg')
            mock_webbrowser_open.assert_called_once_with(expected_path)

    @patch('VSMWizard.menu_gui.filedialog.askopenfilename')
    def test_update_vsm_cancelled(self, mock_askopenfilename):
        # Test cancellation of file selection
        mock_askopenfilename.return_value = ''
        self.app.update_vsm()
        # Verify no further processing occurred
        self.assertEqual(mock_askopenfilename.call_count, 1)

    def generate_file(self):
        # Ensure the directory exists
        config_dir = os.path.join(os.getcwd(), "config")
        os.makedirs(config_dir, exist_ok=True)

        # Write to the JSON file
        config_path = os.path.join(config_dir, "yml_url_config.json")
        with open(config_path, "w") as json_file:
            json_file.write("{}")  # Example content, replace with actual logic

    def test_remove_pipeline_row(self):
        # Open the configuration window
        self.app.open_config_window()
        
        # Get the config window and its frame
        config_window = self.app.root.nametowidget("!toplevel")
        scrollable_frame = config_window.nametowidget("!canvas.!frame")
        
        # Add two pipeline rows
        add_row_button = scrollable_frame.grid_slaves(row=0, column=0)[0]
        add_row_button.invoke()  # This will add a second row
        
        # Verify we have two rows
        initial_pipeline_entries = len([w for w in scrollable_frame.grid_slaves() if isinstance(w, tk.Entry)])
        self.assertEqual(initial_pipeline_entries, 2, "Should have two pipeline entries before removal")
        
        # Remove a row
        remove_row_button = scrollable_frame.grid_slaves(row=0, column=1)[0]
        remove_row_button.invoke()
        
        # Verify one row was removed
        final_pipeline_entries = len([w for w in scrollable_frame.grid_slaves() if isinstance(w, tk.Entry)])
        self.assertEqual(final_pipeline_entries, 1, "Should have one pipeline entry after removal")
        
        # Verify the remaining row is labeled correctly
        pipeline_label = scrollable_frame.grid_slaves(row=1, column=0)[0]
        yaml_label = scrollable_frame.grid_slaves(row=1, column=2)[0]
        self.assertEqual(pipeline_label.cget("text"), "Pipeline 1 Name:", "First row should be labeled as Pipeline 1")
        self.assertEqual(yaml_label.cget("text"), "YAML File Path 1:", "First row should be labeled as YAML File Path 1")

    def test_delete_row(self):
        # Open the configuration window
        self.app.open_config_window()
        
        # Get the config window and its frame
        config_window = self.app.root.nametowidget("!toplevel")
        scrollable_frame = config_window.nametowidget("!canvas.!frame")
        
        # Add three pipeline rows total
        add_row_button = scrollable_frame.grid_slaves(row=0, column=0)[0]
        add_row_button.invoke()  # Add second row
        add_row_button.invoke()  # Add third row
        
        # Verify we have three rows
        initial_pipeline_entries = len([w for w in scrollable_frame.grid_slaves() if isinstance(w, tk.Entry)])
        self.assertEqual(initial_pipeline_entries, 3, "Should have three pipeline entries before deletion")
        
        # Delete the second row (row_num=2)
        delete_button = scrollable_frame.grid_slaves(row=2, column=4)[0]
        delete_button.invoke()
        
        # Verify one row was deleted
        remaining_pipeline_entries = len([w for w in scrollable_frame.grid_slaves() if isinstance(w, tk.Entry)])
        self.assertEqual(remaining_pipeline_entries, 2, "Should have two pipeline entries after deletion")
        
        # Verify the remaining rows are labeled correctly
        # Check first row
        first_pipeline_label = scrollable_frame.grid_slaves(row=1, column=0)[0]
        first_yaml_label = scrollable_frame.grid_slaves(row=1, column=2)[0]
        self.assertEqual(first_pipeline_label.cget("text"), "Pipeline 1 Name:", "First row should be labeled as Pipeline 1")
        self.assertEqual(first_yaml_label.cget("text"), "YAML File Path 1:", "First row should be labeled as YAML File Path 1")
        
        # Check second row (previously third row)
        second_pipeline_label = scrollable_frame.grid_slaves(row=2, column=0)[0]
        second_yaml_label = scrollable_frame.grid_slaves(row=2, column=2)[0]
        self.assertEqual(second_pipeline_label.cget("text"), "Pipeline 2 Name:", "Second row should be labeled as Pipeline 2")
        self.assertEqual(second_yaml_label.cget("text"), "YAML File Path 2:", "Second row should be labeled as YAML File Path 2")
        
        # Test minimum row requirement
        # Try to delete when only one row remains
        delete_button = scrollable_frame.grid_slaves(row=2, column=4)[0]
        delete_button.invoke()
        delete_button.invoke()  # Try to delete again
        
        # Verify at least one row remains
        final_pipeline_entries = len([w for w in scrollable_frame.grid_slaves() if isinstance(w, tk.Entry)])
        self.assertEqual(final_pipeline_entries, 1, "Should maintain at least one pipeline entry")

    @patch('tkinter.filedialog.askopenfilename')
    @patch('webbrowser.open')
    def test_update_vsm(self, mock_webbrowser, mock_filedialog):
        # Setup test files
        test_svg = """<?xml version="1.0" encoding="UTF-8"?>
        <svg xmlns="http://www.w3.org/2000/svg">
            <g>
                <rect id="rect_100_100" x="100" y="100" width="50" height="30"/>
                <text x="110" y="120">Test Text</text>
                <circle cx="125" cy="115" r="5"/>
                <a><text x="105" y="125">Link Text</text></a>
            </g>
            <rect id="rect_200_200" x="200" y="200" width="50" height="30"/>
            <path id="post_rect_100_100_pre_rect_200_200_arrow" d="M150,115 L200,215"/>
        </svg>"""
        
        # Fixed JSON structure - removed the "positions" wrapper
        test_json = [
            {"id": "rect_100_100", "x": 150, "y": 150},
            {"id": "rect_200_200", "x": 250, "y": 250}
        ]

        # Create temporary test files
        with open('test.svg', 'w') as f:
            f.write(test_svg)
        with open('test.json', 'w') as f:
            json.dump(test_json, f)

        # Mock file dialog responses
        mock_filedialog.side_effect = ['test.svg', 'test.json']

        # Run update_vsm
        self.app.update_vsm()

        # Verify the output SVG
        tree = ET.parse('test_updated.svg')
        root = tree.getroot()
        ns = {"svg": "http://www.w3.org/2000/svg"}

        # Test group element movement
        group = root.find(".//{http://www.w3.org/2000/svg}g")
        rect = group.find(".//{http://www.w3.org/2000/svg}rect")
        self.assertEqual(rect.get("x"), "150")
        self.assertEqual(rect.get("y"), "150")
        self.assertEqual(rect.get("id"), "rect_150_150")

        # Test text movement inside group
        text = group.find(".//{http://www.w3.org/2000/svg}text")
        self.assertEqual(text.get("x"), "160")
        self.assertEqual(text.get("y"), "170")

        # Test circle movement inside group
        circle = group.find(".//{http://www.w3.org/2000/svg}circle")
        self.assertEqual(circle.get("cx"), "175")
        self.assertEqual(circle.get("cy"), "165")

        # Test anchor text movement
        anchor = group.find(".//{http://www.w3.org/2000/svg}a")
        anchor_text = anchor.find(".//{http://www.w3.org/2000/svg}text")
        self.assertEqual(anchor_text.get("x"), "155")
        self.assertEqual(anchor_text.get("y"), "175")

        # Test standalone rectangle
        standalone_rect = root.find(".//*[@id='rect_250_250']")
        self.assertEqual(standalone_rect.get("x"), "250")
        self.assertEqual(standalone_rect.get("y"), "250")

        # Test connection path ID update
        # Instead of using contains(), we'll iterate through all paths
        path = None
        for element in root.findall(".//{http://www.w3.org/2000/svg}path"):
            if "post_rect" in element.get("id", ""):
                path = element
                break
            
        expected_id = "post_rect_150_150_pre_rect_250_250_arrow"
        self.assertIsNotNone(path, "Path element not found")
        self.assertEqual(path.get("id"), expected_id)

        # Clean up test files
        os.remove('test.svg')
        os.remove('test.json')
        os.remove('test_updated.svg')

        # Verify browser was called to open the file
        mock_webbrowser.assert_called_once()

if __name__ == '__main__':
    unittest.main()
