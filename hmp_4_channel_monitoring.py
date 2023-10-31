"""
HMP4040 4 Channel Power Supply Monitoring Program

This script allows for monitoring and logging of voltage and current data from an HMP4040 power supply.
It uses the PyMeasure library for instrument control and Tkinter for the GUI.

Command line arguments:
    file_path: Path to the directory where the log file will be saved
    file_name: Name of the log file (must be a .txt file)
    plot_size: Size of the plot (default=1)
    max_displayed_samples: Maximum number of samples to display on the plot (default=20)
    update_rate_ms: Rate of measurements in ms (default=1000)
"""

### Flash red on comliance

import argparse
import os
from pymeasure.instruments.rohdeschwarz import HMP4040
import pyvisa
import pyvisa.errors
import time
import tkinter as tk
from tkinter import messagebox
import pandas as pd

#for plots
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

#import logging
##logging config
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.debug('This log message appears on the screen.')


def plot_current(channel_frame, current_data, fig, plot, max_displayed_samples):

    """
    Plots the current data for a specific channel.

    Args:
        channel_frame (tk.Frame): The Tkinter frame for the channel plot.
        current_data (list): List of current data points for the channel.
        fig (Figure): The Matplotlib Figure object for the channel plot.
        plot (Axes): The Matplotlib Axes object for the channel plot.
    """

    plot.clear()
    #plot most recent points, or all points if smaller than max_displayed_samples
    try:
        current_data = current_data[-max_displayed_samples:]
    except:
        current_data = current_data
    
    plot.plot(current_data)

    #remove all x, y-ticks
    plot.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, left=False, right=False, labelleft=False)
    plot.set_ylim(0,3) #fixed- y-axis   
    # write most recent value at center and BIG
    current_value = current_data[-1] 
    plot.text(0.5, 0.5, f'{current_value}', ha='center', va='center', transform=plot.transAxes, fontsize=22)

    fig.canvas.draw()


def handle_file(file_address, attempts=0): # human readable & some formatting

    """
    Handles file creation and existing file scenarios, with a limit of 2 attempts.
    
    :param str file_address: The file path and name for the new or existing file
    :param int attempts: The number of attempts made so far to handle the file
    :returns: File address or exits the program
    :rtype: str
    """

    if attempts >= 2:
        print("Maximum number of attempts reached. Exiting program.")
        exit()

    if not os.path.exists(file_address):
        with open(file_address, "w") as file:
            pass
        return file_address


    else:
        choice = input(f"The file '{file_address}' already exists. Delete it (D) or specify a new location and name (N)? Enter 'D' or 'N': ").upper()
        if choice == 'D':
            os.remove(file_address)
            return handle_file(file_address)
        elif choice == 'N':
            print('Please restart and provide a valid file_path & file_name')
            exit()
        else:
            print("Invalid input. Please enter 'D' or 'N'.")
            return handle_file(file_address, attempts + 1)


def connect_to_device():

    """
    Establishes a connection to the HMP4040 power supply device.

    Returns:
        object: An instance of the connected HMP4040 power supply.
    """

    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    identities = []
    
    for i,resource in enumerate(resources):
        try:
            identity = rm.open_resource(resource).query('*IDN?')
            identities.append([resource,identity])
            print('attempting connection to '+resource+' ('+str(i+1)+'/'+str(len(resources))+')')
            power_supply = HMP4040(resource)
            power_supply.beep()
            print('connection established to: '+identity)
            
        except:
            print('next')
        
    try:
        assert len(identities) > 0, 'no HMP4040 Connections found. Check connections'
    except AssertionError as e:
        print(f"Error: {e}")
        print('all available HMP4040 devices: '+str(identities))
        exit()

    if len(identities) > 1:
        print('Multiple connections found. Choose one')
        print(connection for connection in identities)
        try:
            chosen_power_supply = int(input('choose one (Numer 1-{}): '.format(len(identities)+1)))
        except: 
            print('number must be int')
            chosen_power_supply = int(input('choose one (Numer 1-{}): '.format(len(identities)+1)))
        try:
            assert chosen_power_supply <= len(identities)+1, 'number out of bounds, chosen_power_supply must be smaller than available devices'
            assert chosen_power_supply > 0, 'number out of bounds, chosen_power_supply must be > 0 (1, 2, ...)'
            assert type(chosen_power_supply) == int, 'number must be int and > 0 (1, 2, ...)' # should never happen int() above
        except AssertionError as e:
            print(f"Error: {e}")
            print("all available HMP4040 devices: "+str(identities))
            exit()
        print('connecting to ',identities[chosen_power_supply-1][0],"at ",identities[chosen_power_supply-1][1])
        power_supply = HMP4040(identities[chosen_power_supply-1][1])
    else: 
        print('connecting to ',identities[0][1],"at ",identities[0][0])
        power_supply = HMP4040(identities[0][0])

    try:
        assert isinstance(power_supply,HMP4040), "power_supply is not an instance of HMP4040"
    except AssertionError as e:
        print(f"Error: {e}")
        exit()

    return power_supply


def measure_and_log_voltage_current(power_supply, voltage_labels, current_labels, current_data, file_address):
    """
    Measures and logs the voltage and current for each channel of the power supply.
    The data is logged in a way that it can be easily read into a DataFrame.
    """

    # Get the current timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Initialize an empty dictionary to hold the data
    data_dict = {'Timestamp': timestamp}

    # Loop through each channel to measure and log voltage and current
    for i in range(1, 5):  # Channels are 1-indexed
        # Select the channel on the power supply
        power_supply.selected_channel = i

        # Measure the voltage and current
        voltage_V = np.round(power_supply.measured_voltage, 3)
        current_mA = np.round(power_supply.measured_current, 6) * 1000

        # Update the GUI labels
        voltage_labels[i-1].config(text=f"Voltage: {voltage_V:.3f} V")
        current_labels[i-1].config(text=f"Current: {current_mA:.3f} mA")

        # Append the current data to the list for plotting
        current_data[i-1].append(current_mA)

        # Add the voltage and current data to the dictionary
        data_dict[f'Ch{i}_Voltage'] = voltage_V
        data_dict[f'Ch{i}_Current'] = current_mA

    # Write the data to the log file
    with open(file_address, "a") as file:
        # If the file is empty, write the header
        if os.stat(file_address).st_size == 0:
            file.write('### Skip the first 3 rows. Format: Timestamp, Ch1 Volt, Ch1 Current, Ch2 ... separated by \\t  and timestamps by \\n\nexpected V/mA ch1 1.85/500, ch2 1.25/150, ch3 3.33/140, ch4 1.95/500\n\n')
            header = '\t'.join(data_dict.keys()) + '\n'
            file.write(header)

        # Write the data
        file.write('\t'.join(map(str, data_dict.values())) + '\n')

def load_data_into_dataframe(file_address):
    """
    Loads the logged data from a text file into a Pandas DataFrame.
    
    :param str file_address: The file path and name of the existing log file.
    :returns: A Pandas DataFrame containing the logged data.
    :rtype: pd.DataFrame
    """
    
    # Skip the first 3 rows and read the tab-separated values into a DataFrame
    df = pd.read_csv(file_address, sep='\t', skiprows=3)
    
    # Convert 'Timestamp' column to datetime format for better manipulation
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    return df


def beep(power_supply):
    """
    Triggers a beep sound on the power supply.
    """
    power_supply.beep()


def update(root, power_supply, voltage_labels, current_labels, current_data, channel_frames, channel_plots, file_address, max_displayed_samples, update_rate_ms):
    """
    Updates the measurements, logs the data, and redraws the plots.
    """
    measure_and_log_voltage_current(power_supply, voltage_labels, current_labels, current_data, file_address)
    [plot_current(frame, data, fig, plot, max_displayed_samples) for frame, data, (fig, plot) in zip(channel_frames, current_data, channel_plots)]
    root.after(update_rate_ms, lambda: update(root, power_supply, voltage_labels, current_labels, current_data, channel_frames, channel_plots, file_address, max_displayed_samples, update_rate_ms))


def validate_args(args):
    try:
        assert args.file_name.endswith('.txt'), "The provided file name must be a .txt file"
        assert args.plot_size > 0 and args.plot_size < 10, "Plot size must be between 1 and 9"
        assert args.max_displayed_samples > 0, "max_displayed_samples must be greater than 0"
        assert args.update_rate_ms > 0, "update_rate_ms must be greater than 0"
    except AssertionError as e:
        print(f"Error: {e}")
        exit()






### Program Start
def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description="HMP4040 4 Channel Power Supply Monitoring Program. Make sure to separate path and file name with a space character")
    parser.add_argument("file_path", help="Path to the directory where the log file will be saved")
    parser.add_argument("file_name", help='Name of the log file (must be a .txt file)')
    parser.add_argument('--plot_size', type=int, default=1, help='Size of the plot. Must be an integer between 1 and 9. Default: 1')
    parser.add_argument('--max_displayed_samples', type=int, default=20, help='Maximum number of samples to display on the plot. Must be a positive integer. Default: 20')
    parser.add_argument('--update_rate_ms', type=int, default=1000, help='Rate of measurements in ms. Must be a positive integer. Default: 1000 (1 second)')

    args = parser.parse_args()
    validate_args(args)

    # validate and store command line arguments
    #  file I/O parameters
    file_path = args.file_path
    file_name = args.file_name

    file_address = os.path.join(file_path, file_name)
    catch_file_creation = handle_file(file_address)

    #  plotting controls
    plot_size = args.plot_size
    max_displayed_samples = args.max_displayed_samples
    update_rate_ms = args.update_rate_ms


    # create main tkinter window
    root = tk.Tk()
    root.title("Power Supply Monitoring")


    # connect to the power supply device
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    print(resources)
    identities = []
        
    power_supply = connect_to_device()


    # initialize current data for all channels
    current_data = [[0], [0], [0], [0]]


    # create control buttons (Connect and Beep) and add them to the control frame
    control_buttons = [['Connect', lambda: connect_to_device()], ['Beep', lambda: beep(power_supply)]]

    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.TOP, pady=10)

    control_buttons_widgets = [tk.Button(control_frame, text=button[0], command=button[1]) for button in control_buttons]
    for button_widget in control_buttons_widgets:
        button_widget.pack(side=tk.LEFT)

    # create 4 channel frames for displaying voltage and current data
    channel_frames = [tk.Frame(root) for _ in range(4)]
    for channel_frame  in channel_frames:
        channel_frame.pack(side=tk.TOP, pady=10)

    # initialize the Figure and Axes objects for each channel
    channel_plots = []
    for i in range(4):
        fig = Figure(figsize=(plot_size, plot_size), dpi=100)
        plot = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=channel_frames[i])
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        channel_plots.append((fig, plot))

    # add voltage and current labels to each channel frame
    for i in range(4):
        fig, plot = channel_plots[i]
        plot_current(channel_frames[i], current_data[i], fig, plot, max_displayed_samples)

    voltage_labels = [tk.Label(channel_frames[_], text="Voltage: ") for _ in range(4)]
    for label in voltage_labels:
        label.pack()

    current_labels = [tk.Label(channel_frames[_], text="Current: ") for _ in range(4)]
    for label in current_labels:
        label.pack()

    # update function to refresh the display
    update(root, power_supply, voltage_labels, current_labels, current_data, channel_frames, channel_plots, file_address, max_displayed_samples, update_rate_ms)
    root.mainloop()


if __name__ == "__main__":
    main()
