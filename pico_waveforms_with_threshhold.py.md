---
title: '[]{#_412ni9eccnta .anchor}pico\_waveforms\_with\_threshhold.py'
---

Capture a defined number of waveforms using a PicoScope when the voltage
exceeds a threshold, and store the results in an HDF5 file using
[[picosdk]{.underline}](https://github.com/picotech/picosdk-python-wrappers)

Example:

  ------------------------------------------------------------------------------
  python3 pico\_waveforms\_with\_threshhold.py ./Your-Directory/ pico\_test.h5
  ------------------------------------------------------------------------------

  -------------------------------------------------
  python3 pico\_waveforms\_with\_threshhold.py -h
  -------------------------------------------------

Notes
=====

The program executes in **Block-Mode** on the Picoscope. If the
threshold was not surpassed in the measurement time interval, the
current state is recorded as a wave form. That restricts the maximum
runtime and avoids infinite measurement loops.

To add
[[picosdk]{.underline}](https://github.com/picotech/picosdk-python-wrappers)
to your installation you can just download it from the GitHub link above
and move it to a folder where your machine finds libraries manually.

Parser
======

Required
--------

+----------------------------------------------------------------------+
| file\_path: Path to the directory where the log file will be saved   |
|                                                                      |
| file\_name: Name of the log file (must be a .h5 file)                |
|                                                                      |
| voltage\_trigger: The voltage threshold (in mV) that triggers        |
| waveform capture                                                     |
+----------------------------------------------------------------------+

Optional
--------

+----------------------------------------------------------------------+
| \--num\_waveforms: Number of waveforms to capture (integer).         |
| Default: 10                                                          |
|                                                                      |
| \--voltage\_range: Voltage range for the PicoScope. Default:         |
| PS5000\_200MV                                                        |
|                                                                      |
| \--preTriggerSamples: Number of samples to capture before the        |
| voltage trigger (integer). Default: 200. With a timebase of 8 (80 ns |
| per sample), this corresponds to 16 µs of pre-trigger data           |
|                                                                      |
| \--postTriggerSamples: Number of samples to capture after the        |
| voltage trigger (integer). Default: 800. With a timebase of 8 (80 ns |
| per sample), this corresponds to 64 µs of post-trigger data          |
+----------------------------------------------------------------------+

Important Functions
===================

### save\_waveform\_data(file\_address, waveform\_data, metadata): 

+-----------------------------------------------------------------------+
| Save waveform data and associated metadata to an HDF5 file.           |
|                                                                       |
| Args:                                                                 |
|                                                                       |
| file\_address (str): Path to the HDF5 file                            |
|                                                                       |
| waveform\_data (numpy.ndarray): Waveform data to be saved             |
|                                                                       |
| metadata (dict): Metadata to be saved as attributes of the root group |
+-----------------------------------------------------------------------+

### get\_waveform\_data(file\_address):

+-----------------------------------------------------------------------+
| Read the waveform data from the .h5 file and return an numpy array    |
|                                                                       |
| Args:                                                                 |
|                                                                       |
| file\_address (str): The file path and name for the new file.         |
|                                                                       |
| Returns:                                                              |
|                                                                       |
| waveform\_data (numpy.ndarray): The file address of the created file  |
|                                                                       |
| timebase (int): oparating sample timebase in 10s of us                |
|                                                                       |
| metadata (dict): Metadata to be saved as attributes of the root group |
+-----------------------------------------------------------------------+
