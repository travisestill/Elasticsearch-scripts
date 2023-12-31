# Check future dates script

This script checks for any indices that have the `@timestamp` field set to a date in the future. If there are any that are detected, the resulting output will be a csv file with the Index name, Doc ID, Timestamp value, and the difference (how far in the future it is)

Dependencies: 
- Python3,
  - TKinter
  - elasticsearch python client
  - python-dateutil
  - pytz

#Installation instructions:

1. Make sure you have python3 installed:
```
python --version
```
or
```
python3 --version
```
2. Download the ZIP file from https://github.com/travisestill/Elasticsearch-scripts/releases (you can probably clone the repo too)
3. extract files to a location of your choice
4. cd to the extracted folder, then run `pip3 install .` to resolve dependencies
5. Run with `python3 check_future_dates.py`
6. Follow the interactive prompts to supply connection parameters

# Troubleshooting

If you get an error like:
```
    import _tkinter # If this fails your Python may not be configured for Tk
    ^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named '_tkinter'
```
That means you're probably using a newer version of python, or installed a different version than what ships with mac through home brew. If so, run:
```
brew install python-tk@3.##
```
Where ## matches your python version


TO-DO:
- allow users to specify fields other than `@timestamp`
- check for other fields with date mappings (default format) that can be used to replace future date values in the `@timestampt field`
- Give users options on what they want to do to fix the future dates.
