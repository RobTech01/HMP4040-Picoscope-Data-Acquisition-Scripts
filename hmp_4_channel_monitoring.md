# hmp_4_channel_monitoring

Searches visa connections through
[<span class="underline">pyvisa</span>](https://pyvisa.readthedocs.io/en/latest/)
to read out a HMP4040 to a log file (human readable .txt.) and visually
displays all channels with actual measured current

values using
[<span class="underline">tkinter</span>](https://docs.python.org/3/library/tkinter.html)
and [<span class="underline">matplotlib</span>](https://matplotlib.org/)

Example:

```
python3 hmp\_4\_channel\_monitoring.py ./Your-Directory/ hmp\_test.txt
```

```
python3 hmp\_4\_channel\_monitoring.py -h
```

## Notes

The directory and file name to save the logged data to is separated by a
space in the command line. Do not use spaces when naming stuff.

Use load\_data\_into\_dataframe() to read the created .txt file into a
pandas DataFrame for further investigation.

## Parser

### Required

<table>
<tbody>
<tr class="odd">
<td><p>file_path: Path to the directory where the log file will be saved</p>
<p>file_name: Name of the log file (must be a .txt file)</p></td>
</tr>
</tbody>
</table>

### Optional

<table>
<tbody>
<tr class="odd">
<td><p>--plot_size: Size of the plot. Must be an integer between 1 and 9. Default: 1</p>
<p>--max_displayed_samples: Maximum number of samples to display on the plot. Must be a positive integer. Default: 20</p>
<p>--update_rate: Rate of measurements in ms. Must be a positive integer. Default: 1000 (1 second)</p></td>
</tr>
</tbody>
</table>

## Important Functions

#### connect\_to\_device():

<table>
<tbody>
<tr class="odd">
<td><p>Establishes a connection to the HMP4040 power supply device.</p>
<p>Returns:</p>
<p>object: An instance of the connected HMP4040 power supply.</p></td>
</tr>
</tbody>
</table>

#### load\_data\_into\_dataframe(file\_address):

<table>
<tbody>
<tr class="odd">
<td><p>Loads the logged data from a text file into a Pandas DataFrame.</p>
<p>Args:</p>
<p>file_address (str): The file path and name of the existing log file.</p>
<p>Returns:</p>
<p>pd.DataFrame: A Pandas DataFrame containing the logged data.</p></td>
</tr>
</tbody>
</table>
