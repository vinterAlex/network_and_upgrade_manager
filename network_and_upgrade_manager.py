import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import re

# Function to resize the window if the Treeview content exceeds its height
def resize_window(treeview):
    # Calculate the number of rows in the Treeview
    row_count = len(treeview.get_children())
    
    # Each row height can be estimated. You might need to adjust this based on your font size
    row_height = 25  # Height of each row in pixels
    header_height = 30  # Height of the header in pixels
    
    # Calculate the new height
    new_height = header_height + (row_count * row_height)
    
    # Set a minimum height and limit the maximum height to the screen height
    min_height = 400
    max_height = 600
    new_height = max(min_height, min(new_height, max_height))

    # Update the window size
    root.geometry(f"{root.winfo_width()}x{new_height}")

# Function to get network info (ipconfig on Windows)
def get_network_info():
    try:
        # Run ipconfig command
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)

        # Clear previous data in the Treeview
        for row in network_tree.get_children():
            network_tree.delete(row)

        # Split output into lines and populate the Treeview
        lines = result.stdout.splitlines()
        for line in lines:
            if line.strip():  # Check for non-empty lines
                network_tree.insert("", tk.END, values=(line.strip(),))  # Insert line into the tree

        resize_window(network_tree)  # Resize window based on Treeview content

        messagebox.showinfo("Network Info", "Network information retrieved successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to get windows apps upgrade info (winget upgrade)
def get_windows_apps_upgrade():
    try:
        # Run the winget upgrade command
        result = subprocess.run(
            ["winget", "upgrade"], capture_output=True, text=True
        )

        # Clear previous data in the Treeview
        for row in winget_tree.get_children():
            winget_tree.delete(row)

        # Print the raw output for debugging
        print("Raw Output from winget upgrade:")
        print(result.stdout)  # Debug output

        # Extract relevant lines from the command output
        lines = result.stdout.splitlines()

        # Initialize a flag to track if any data was added
        has_results = False

        # Find the start of the actual data in the output
        data_start = False
        for line in lines:
            if line.startswith("---"):  # This marks the start of the actual data
                data_start = True
                continue
            
            if data_start and line.strip():  # Ensure we're processing only non-empty lines
                # Use regex to extract the relevant columns
                match = re.match(r'^(.*?)\s+([a-zA-Z0-9.-]+)\s+([0-9.]+)\s+([0-9.]+)\s+(.+)$', line)
                if match:
                    # Using groups to get data
                    name, id_, version, available, source = match.groups()

                    # Insert the data into the treeview
                    winget_tree.insert("", tk.END, values=(
                        name.strip(),
                        id_.strip(),
                        version.strip(),
                        available.strip(),
                        source.strip()
                    ))
                    has_results = True  # Mark that we found some results

        # If no results were found, show "No results" in the Treeview
        if not has_results:
            winget_tree.insert("", tk.END, values=("No results", "", "", "", ""))
            upgrade_button.pack_forget()  # Hide the button if there are no results
        else:
            # Show notification that upgrades are found
            messagebox.showinfo("Upgrades Available", "I've found upgrades! Check the table.")
            upgrade_button.pack(side=tk.LEFT, padx=5)  # Show the button if there are results

        resize_window(winget_tree)  # Resize window based on Treeview content

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to perform upgrades using winget
def upgrade_selected_apps():
    try:
        # Run the winget upgrade --all command to upgrade all apps
        upgrade_button.config(state=tk.DISABLED)  # Disable the button during upgrade
        result = subprocess.run(
            ["winget", "upgrade", "--all"], capture_output=True, text=True
        )

        # Check if any message is returned in stderr (warnings or errors)
        stderr_output = result.stderr.strip()
        if stderr_output:
            # Show a warning message box with the content of stderr
            messagebox.showwarning("Upgrade Warning", stderr_output)

        # Check stdout for specific messages about packages that cannot be upgraded
        if "have version numbers that cannot be determined" in result.stdout:
            messagebox.showwarning("Upgrade Warning", result.stdout)

        # Show popup notification once the upgrade is done without issues
        elif not stderr_output:
            messagebox.showinfo("Upgrade Completed", "All selected apps have been upgraded successfully without issues!")

        # Clear previous data in the Treeview
        for row in winget_tree.get_children():
            winget_tree.delete(row)

        # Optionally, repopulate the tree or just leave it empty.
        winget_tree.insert("", tk.END, values=("No upgrades available", "", "", "", ""))

    except Exception as e:
        messagebox.showerror("Upgrade Failed", f"An error occurred during upgrade: {str(e)}")
    finally:
        upgrade_button.config(state=tk.NORMAL)  # Re-enable the button after the process

# Create the main window
root = tk.Tk()
root.title("Network and Upgrade Manager")

# Set initial window size
root.geometry("800x400")  # Set initial size to be wider and taller

# Create the Notebook (tabs container)
tab_control = ttk.Notebook(root)

# Create the tabs
network_tab = tk.Frame(tab_control)
upgrade_tab = tk.Frame(tab_control)  # New tab for Windows Apps Check/Upgrade

# Add tabs to the notebook
tab_control.add(network_tab, text="Network Info")
tab_control.add(upgrade_tab, text="Windows Apps Check/Upgrade")  # Adding the new tab
tab_control.pack(expand=1, fill="both")

# Create a frame for the buttons in the Network Info tab
network_button_frame = tk.Frame(network_tab)
network_button_frame.pack(pady=10)

# Create a button to show network info
network_info_button = tk.Button(network_button_frame, text="Show Network Info", command=get_network_info)
network_info_button.pack(side=tk.LEFT, padx=5)

# Create a Treeview for displaying network info
network_tree = ttk.Treeview(network_tab, columns=("Info",), show="headings")
network_tree.heading("Info", text="Network Info")
network_tree.pack(expand=True, fill='both')

# Create a frame for the buttons in the Windows Apps Check/Upgrade tab
upgrade_button_frame = tk.Frame(upgrade_tab)
upgrade_button_frame.pack(pady=10)

# Button to show Windows apps that need upgrade
winget_button = tk.Button(upgrade_button_frame, text="Show Windows apps that need upgrade", command=get_windows_apps_upgrade)
winget_button.pack(side=tk.LEFT, padx=5)

# The new button to perform additional actions, initially hidden
upgrade_button = tk.Button(upgrade_button_frame, text="Upgrade Selected Apps", command=upgrade_selected_apps)
upgrade_button.pack_forget()  # Hide this button initially

# Create the Treeview for Winget List
winget_tree = ttk.Treeview(upgrade_tab, columns=("Name", "Id", "Version", "Available", "Source"), show="headings")
winget_tree.heading("Name", text="Name")
winget_tree.heading("Id", text="Id")
winget_tree.heading("Version", text="Version")
winget_tree.heading("Available", text="Available")
winget_tree.heading("Source", text="Source")
winget_tree.pack(expand=True, fill='both')

# Run the main loop
root.mainloop()
