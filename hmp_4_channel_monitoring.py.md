---
title: '[]{#_njssfog6er0w .anchor}hmp\_4\_channel\_monitoring'
---

Searches visa connections through
[[pyvisa]{.underline}](https://pyvisa.readthedocs.io/en/latest/) to read
out a HMP4040 to a log file (human readable .txt.) and visually displays
all channels with actual measured current

values using
[[tkinter]{.underline}](https://docs.python.org/3/library/tkinter.html)
and [[matplotlib]{.underline}](https://matplotlib.org/)

Example:

  ------------------------------------------------------------------------
  python3 hmp\_4\_channel\_monitoring.py ./Your-Directory/ hmp\_test.txt
  ------------------------------------------------------------------------

  -------------------------------------------
  python3 hmp\_4\_channel\_monitoring.py -h
  -------------------------------------------

Notes
=====

The directory and file name to save the logged data to is separated by a
space in the command line. Do not use spaces when naming stuff.

Use load\_data\_into\_dataframe() to read the created .txt file into a
pandas DataFrame for further investigation.

Parser
======

Required
--------

+--------------------------------------------------------------------+
| file\_path: Path to the directory where the log file will be saved |
|                                                                    |
| file\_name: Name of the log file (must be a .txt file)             |
+--------------------------------------------------------------------+

Optional
--------

+----------------------------------------------------------------------+
| \--plot\_size: Size of the plot. Must be an integer between 1 and 9. |
| Default: 1                                                           |
|                                                                      |
| \--max\_displayed\_samples: Maximum number of samples to display on  |
| the plot. Must be a positive integer. Default: 20                    |
|                                                                      |
| \--update\_rate: Rate of measurements in ms. Must be a positive      |
| integer. Default: 1000 (1 second)                                    |
+----------------------------------------------------------------------+

Important Functions
===================

### connect\_to\_device():

+--------------------------------------------------------------+
| Establishes a connection to the HMP4040 power supply device. |
|                                                              |
| Returns:                                                     |
|                                                              |
| object: An instance of the connected HMP4040 power supply.   |
+--------------------------------------------------------------+

### load\_data\_into\_dataframe(file\_address):

+-----------------------------------------------------------------------+
| Loads the logged data from a text file into a Pandas DataFrame.       |
|                                                                       |
| Args:                                                                 |
|                                                                       |
| file\_address (str): The file path and name of the existing log file. |
|                                                                       |
| Returns:                                                              |
|                                                                       |
| pd.DataFrame: A Pandas DataFrame containing the logged data.          |
+-----------------------------------------------------------------------+
