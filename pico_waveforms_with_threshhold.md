Capture a defined number of waveforms using a PicoScope when the voltage
exceeds a threshold, and store the results in an HDF5 file using
[<span class="underline">picosdk</span>](https://github.com/picotech/picosdk-python-wrappers)

Example:
```
python3 pico\_waveforms\_with\_threshhold.py ./Your-Directory/ pico\_test.h5
```

```
python3 pico\_waveforms\_with\_threshhold.py -h
```

# Notes

The program executes in **Block-Mode** on the Picoscope. If the
threshold was not surpassed in the measurement time interval, the
current state is recorded as a wave form. That restricts the maximum
runtime and avoids infinite measurement loops.

To add
[<span class="underline">picosdk</span>](https://github.com/picotech/picosdk-python-wrappers)
to your installation you can just download it from the GitHub link above
and move it to a folder where your machine finds libraries manually.

# Parser

## Required

<table>
<tbody>
<tr class="odd">
<td><p>file_path: Path to the directory where the log file will be saved</p>
<p>file_name: Name of the log file (must be a .h5 file)</p>
<p>voltage_trigger: The voltage threshold (in mV) that triggers waveform capture</p></td>
</tr>
</tbody>
</table>

## Optional

<table>
<tbody>
<tr class="odd">
<td><p>--num_waveforms: Number of waveforms to capture (integer). Default: 10</p>
<p>--voltage_range: Voltage range for the PicoScope. Default: PS5000_200MV</p>
<p>--preTriggerSamples: Number of samples to capture before the voltage trigger (integer). Default: 200. With a timebase of 8 (80 ns per sample), this corresponds to 16 µs of pre-trigger data</p>
<p>--postTriggerSamples: Number of samples to capture after the voltage trigger (integer). Default: 800. With a timebase of 8 (80 ns per sample), this corresponds to 64 µs of post-trigger data</p></td>
</tr>
</tbody>
</table>

# Important Functions

### save\_waveform\_data(file\_address, waveform\_data, metadata): 

<table>
<tbody>
<tr class="odd">
<td><p>Save waveform data and associated metadata to an HDF5 file.</p>
<p>Args:</p>
<p>file_address (str): Path to the HDF5 file</p>
<p>waveform_data (numpy.ndarray): Waveform data to be saved</p>
<p>metadata (dict): Metadata to be saved as attributes of the root group</p></td>
</tr>
</tbody>
</table>

### get\_waveform\_data(file\_address):

<table>
<tbody>
<tr class="odd">
<td><p>Read the waveform data from the .h5 file and return an numpy array</p>
<p>Args:</p>
<p>file_address (str): The file path and name for the new file.</p>
<p>Returns:</p>
<p>waveform_data (numpy.ndarray): The file address of the created file</p>
<p>timebase (int): oparating sample timebase in 10s of us</p>
<p>metadata (dict): Metadata to be saved as attributes of the root group</p></td>
</tr>
</tbody>
</table>
