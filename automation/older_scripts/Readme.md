## Targets2Carrot
Converts a list of MZ/RT targets into a yml file to use in carrot

### Files
- Launcher: targets2carrot/target2carrot.py

### Usage
```bash
python3 targets2carrot.py -f <file> -s <name> [-o <filename>] [-i <instrument>] [-c <column>] [-m <ion-mode>] 

Parameters:
    * '-f', '--file': csv file with the list of targets (one per line) and with headers: 'Metabolite name,Average Mz,Average Rt(min),istd'. Required
    * '-o', '--output': name of the yml file to be created
    * '-s', '--study': name of the study/experiment. Required
    * '-i', '--instrument': name of the instrument for the library. Default='test'
    * '-c', '--column': name of the column for the library. Default='test'
    * '-m', '--mode': ion mode. Choices='positive' or 'negative']. Default='positive'
```
---
## AgilentTimes
Extracts the acquisition timestamp of agilent samples directly from the raw data

### Files
- Launcher: agilentTimes.py

### Usage
```bash
python3 agilentTimes.py -s <file> -o <folder>

Parameters:
    * '-s', '--raw_data_sources': File containing a list of folders (one per line) where the raw data lives. Required
    * '-o', '--output_folder': Folder were to save the results. Required
```
---
## FileCheck
Written specifically for Jenny's _Tribe_ experiment, due to the ammount of folders with raw data and the variability on sample filenames.
Compares and produces feedback for several topics:
- Checks the provided worklist agains the actual raw data files, saving a list of missing raw data files
- Checks the list of raw data files against the converted mzml files, saving a list of missing conversions
- Checks the list of converted files vs the mzml files in aws, saving a list of file to upload to aws
- Checks the results on aws agains a previous list of result files (obtained with the aws-cli app)

### Usage
If you _REALLY, REALLY!_ want to use this, refer to the code.

---
## Old incomplete and unused scripts
Like the title implies: older, incomplete and/or obsolete files. **DO NOT USE**. 
- experimentAnalyzer.py
