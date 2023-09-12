# HMP4040-Picoscope-Data-Acquisition-Scripts
The following scripts were created as part of a bachelor thesis.
All scripts incorporate Google docstring style documentation.

Start with:
```
python3 hmp_4_channel_monitoring.py ./logging/ data.txt --plot_size=1 --max_displayed_samples=20 --update_rate_ms=1000
```
and
```
python3 pico_waveforms_with_threshhold.py ./logging/ pico.h5 100 --num_waveforms=10 --voltage_range=PS5000_500MV --timebase_10ns=8 --preTriggerSamples=200 --postTriggerSamples=800 --waveform_type='signal' --user='beam test zagreb'
```
use ```-h``` for explanations.
