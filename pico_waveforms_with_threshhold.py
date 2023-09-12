import ctypes
import numpy as np
import matplotlib.pyplot as plt
import h5py
import os
import argparse
from picosdk.ps5000 import ps5000 as ps
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc

## ToDo make a Package of reuseable parts
## buffer
## timeout
## timebase in ns
## plot every 10th or sth like that live
## filepath and filename to file address in parser

def handle_file(file_address, attempts=0): # human readable & some formatting
    """
    Handles file creation and existing file scenarios, with a limit of 2 attempts.

    Args:
        file_address (str): The file path and name for the new or existing file.
        attempts (int): The number of attempts made so far to handle the file.

    Returns:
        str: File address or exits the program.
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


def save_waveform_data(file_address, waveform_data, metadata):
    """Save waveform data and associated metadata to an HDF5 file.

    Args:
        file_address (str): Path to the HDF5 file
        waveform_data (numpy.ndarray): Waveform data to be saved
        metadata (dict): Metadata to be saved as attributes of the root group
    """

    with h5py.File(file_address, 'w') as f:
        # Convert waveform data to float32
        waveform_data = waveform_data.astype('float32', copy=False)

        waveform_dataset = f.create_dataset('waveform_data', data=waveform_data)
        f.attrs.update(metadata)

def get_waveform_data(file_address):
    """Read the waveform data from the .h5 file
    
    Args:
        file_address (str): The file path and name for the new file.
    Returns:
        waveform_data (numpy.ndarray): The file address of the created file
        timebase (int): oparating sample timebase in 10s of us
        metadata (dict): Metadata to be saved as attributes of the root group
    """
    with h5py.File(file_address, 'r') as f:
        waveform_data = f['waveform_data'][:]

        metadata = f.attrs
        timebase = metadata['timebase'] # date, user, waveform_type
        num_waveforms = metadata['num_waveforms']

        #for key, value in metadata.items():
        #    print(f'{key}: {value}')

    
    return waveform_data, timebase, num_waveforms


def validate_args(args):
    try:
        # Check file extension
        assert args.file_name.endswith('.h5'), "The provided file name must be a .h5 file"
        
        # Check voltage_trigger
        assert args.voltage_trigger_mv > 0, "The voltage_trigger must be greater than 0 mV"
        
        # Check num_waveforms
        assert args.num_waveforms > 0 and args.num_waveforms < 100, "num_waveforms must be between 1 and 99"
        
        # Check voltage_range
        valid_voltage_ranges = [
            "PS5000_100MV", "PS5000_200MV", "PS5000_500MV",
            "PS5000_1V", "PS5000_2V", "PS5000_5V",
            "PS5000_10V", "PS5000_20V"
        ]
        assert args.voltage_range in valid_voltage_ranges, "voltage_range must be valid, try -h for help"
        
        # Check preTriggerSamples and postTriggerSamples
        assert args.preTriggerSamples > 0, "preTriggerSamples must be greater than 0"
        assert args.postTriggerSamples > 0, "postTriggerSamples must be greater than 0"
        
        # Check timebase
        assert args.timebase_10ns >= 0, "timebase must be non-negative"
        
        # Check waveform_type and user
        assert isinstance(args.waveform_type, str), "waveform_type must be a string"
        assert isinstance(args.user, str), "user must be a string"
        
    except AssertionError as e:
        print(f"Error: {e}")
        exit()



def main():
    """Capture a defined number of waveforms using a PicoScope when the voltage exceeds a threshold,
    and store the results in an HDF5 file. The script also plots the captured waveforms.
    
    The script accepts several command line arguments, such as file_path, file_name, voltage_trigger,
    num_waveforms, voltage_range, preTriggerSamples, postTriggerSamples, waveform_type, and user.
    
    The captured waveforms are saved in an HDF5 file with metadata, including date, user, waveform_type,
    timebase, and num_waveforms. After saving the waveforms, the script plots them in a grid layout.
    """
    
    # file storage location, name and num waveforms from parser
    parser = argparse.ArgumentParser(description='Capture a defined number of waveforms using a PicoScope when the voltage exceeds a threshold, and store the results in an HDF5 file.')

    parser.add_argument('file_path', help='Path to the directory where the log file will be saved.')
    parser.add_argument('file_name', help='Name of the log file (must be a .h5 file)')
    parser.add_argument('voltage_trigger_mv', type=int, help='The voltage threshold (in mV) that triggers waveform capture')

    parser.add_argument('--num_waveforms', type=int, default=10, help='Number of waveforms to capture (integer). Default: 10')
    parser.add_argument('--voltage_range', type=str, default='PS5000_200MV', help='Voltage range for the PicoScope. Default: "PS5000_200MV". Available ranges: PS5000_100MV, PS5000_200MV, PS5000_500MV, PS5000_1V, PS5000_2V, PS5000_5V, PS5000_10V, PS5000_20V')
    parser.add_argument('--timebase_10ns', type=int, default=8, help='Sampling interval in 10s of ns (int). Default: 8')
    parser.add_argument('--preTriggerSamples', type=int, default=200, help='Number of samples to capture before the voltage trigger (integer). Default: 200. With a timebase of 8 (80 ns per sample), this corresponds to 16 µs of pre-trigger data')
    parser.add_argument('--postTriggerSamples', type=int, default=800, help='Number of samples to capture after the voltage trigger (integer). Default: 800. With a timebase of 8 (80 ns per sample), this corresponds to 64 µs of post-trigger data')
    parser.add_argument('--waveform_type', type=str, default='generated', help='Type of measurement for metadata (string). Default: "generated"')
    parser.add_argument('--user', type=str, default='expert_user', help='Name of the Author / Measurement by for metadata (string). Default: "expert_user"')


    args = parser.parse_args()
    validate_args(args)

    # log file creation
    file_path = args.file_path
    file_name = args.file_name
    file_extension = os.path.splitext(file_name)[1]
    file_address = os.path.join(file_path, file_name)

    catch_file_creation = handle_file(file_address)

    voltage_trigger_mv = args.voltage_trigger_mv

    num_waveforms = args.num_waveforms

    voltage_range = args.voltage_range

    # Set number of pre and post trigger samples to be collected
    preTriggerSamples = args.preTriggerSamples
    postTriggerSamples = args.postTriggerSamples
    maxSamples = preTriggerSamples + postTriggerSamples
    
    # Set sampling interval
    timebase_10ns = args.timebase_10ns
    print('pre-trigger samples: {}, post-trigger samples: {}, timebase: {}'.format(preTriggerSamples,postTriggerSamples,timebase_10ns))

    # Set the number of waveforms to capture
    print('saving {} waveforms'.format(num_waveforms))

    # Metadata for future analysis
    waveform_type = args.waveform_type
    user = args.user

    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}

    # Open 5000 series PicoScope
    status['openunit'] = ps.ps5000OpenUnit(ctypes.byref(chandle))
    assert_pico_ok(status['openunit'])

    # Set up channel A
    channel = ps.PS5000_CHANNEL['PS5000_CHANNEL_A']
    coupling_type = 1 # DC
    chARange = ps.PS5000_RANGE[voltage_range]
    status['setChA'] = ps.ps5000SetChannel(chandle, channel, 1, coupling_type, chARange)
    assert_pico_ok(status['setChA'])

    # find maximum ADC count value
    maxADC = ctypes.c_int16(32512)

    # Set up single trigger
    # direction = PS5000_RISING = 2
    # delay = 0 s
    # auto Trigger = 1000 ms
    source = ps.PS5000_CHANNEL['PS5000_CHANNEL_A']
    threshold = int(mV2adc(voltage_trigger_mv, chARange, maxADC))
    status['trigger'] = ps.ps5000SetSimpleTrigger(chandle, 1, source, threshold, 2, 0, 1000)
    assert_pico_ok(status['trigger'])

    # Get timebase information
    #timebase = 8   # 80ns
    oversample = 1
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    status['getTimebase'] = ps.ps5000GetTimebase(chandle, timebase_10ns, maxSamples, ctypes.byref(timeIntervalns), oversample, ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(status['getTimebase'])

    # Run rapid block capture and retrieve data for each waveform
    adc2mVChAMax = np.zeros((num_waveforms, maxSamples), dtype=float)

    for waveform in range(num_waveforms):
        status['runBlock'] = ps.ps5000RunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase_10ns, oversample, None, 0, None, None)
        assert_pico_ok(status['runBlock'])

        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            status['isReady'] = ps.ps5000IsReady(chandle, ctypes.byref(ready))

        bufferAMax = (ctypes.c_int16 * maxSamples)()
        source = ps.PS5000_CHANNEL['PS5000_CHANNEL_A']
        status['setDataBuffersA'] = ps.ps5000SetDataBuffers(chandle, source, ctypes.byref(bufferAMax), None, maxSamples)
        assert_pico_ok(status['setDataBuffersA'])

        overflow = ctypes.c_int16()
        cmaxSamples = ctypes.c_int32(maxSamples)
        status['getValues'] = ps.ps5000GetValues(chandle, 0, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
        assert_pico_ok(status['getValues'])

        adc2mVChAMax[waveform, :] = adc2mV(bufferAMax, chARange, maxADC)

    # Create time data
    time = np.linspace(0, (cmaxSamples.value - 1) * timeIntervalns.value, cmaxSamples.value)




    waveform_data = adc2mVChAMax
    metadata = {'date': '2023-05-25', 'user': user, 'waveform_type': waveform_type, 'timebase': timebase_10ns, 'num_waveforms': num_waveforms}
    save_waveform_data(file_address, waveform_data, metadata)
        

    # Stop the scope
    status['stop'] = ps.ps5000Stop(chandle)
    assert_pico_ok(status['stop'])

    # Close unit Disconnect the scope
    status['close'] = ps.ps5000CloseUnit(chandle)
    assert_pico_ok(status['close'])


    waveform, timebase_10ns, num_waveforms = get_waveform_data(file_address) # timebase is in 10 of ns

    # Plot data from channel A in different subplots
    num_rows = int(num_waveforms / 5) + num_waveforms % 5
    num_columns = int(num_waveforms / num_rows)

    time = np.linspace(0, timebase_10ns*10*waveform.shape[1]/1000, waveform[0].size)

    # Find the global minimum and maximum values across all waveforms
    global_min = np.min(waveform)-5
    global_max = np.max(waveform)+5

    for i in range(waveform.shape[0]):
        plt.subplot(num_rows, num_columns, i + 1)
        plt.plot(time, waveform[i, :])
        # Remove x labels except for the ones at the lower edge
        if i < num_waveforms - num_columns:
            plt.xticks([])
        else:
            plt.xlabel('Time (us)')

        # Remove y labels except for the ones at the left edge
        if i % num_columns != 0:
            plt.yticks([])
        else:
            plt.ylabel('Voltage (mV)')
        plt.title(f'Waveform {i + 1}')
        
        # Set the y-axis limits to the global minimum and maximum values
        plt.ylim(global_min, global_max)

    #plt.tight_layout()  # Adjust spacing between plots
    plt.show()


    print('Closing..')
    

if __name__ == "__main__":
    main()