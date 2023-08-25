# Check future dates script

This script checks for any indices that have the `@timestamp` field set to a date in the future. If there are any that are detected, the resulting output will be a csv file with the Index name, Doc ID, Timestamp value, and the difference (how far in the future it is)

Dependencies: Python3

# Usage
```
python3 ./check-future-dates.py
```

Follow the interactive prompts to supply connection parameters

TO-DO:
- allow users to specify fields other than `@timestamp`
- check for other fields with date mappings (default format) that can be used to replace future date values in the `@timestampt field`
- Give users options on what they want to do to fix the future dates.
