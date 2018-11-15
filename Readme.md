# Carrot Automation Scripts

---
## Scheduler
This imitates the full Carrot Control Panel workflow by having options to:
- Add initial experiment acquisition data to the MetaData table in Dynamo and the _entered_ status to the Tracking table
- Add the first 2 statuses (_acquired_, _converted_) for each sample to the Tracking table in Dynamo
- Schedule all the samples in the input file

### Files
- Launcher: runner.py
- Main code: convert folder

### Usage
```bash
python3 runner.py <file> -e <exp_name> -i <instrument> -m <method> [-n <ion-mode>] [-c <column>] [-s <specie>] [-o <organ>] [-x <profile>] [-a] [-p] [-r] [-t]

Parameters:
    * 'file': Filename with list of samples to prepare/schedule
    * '-e', '--experiment': Name of the experiment. Required
    * '-i', '--instrument': Name of the instrument used. Required
    * '-c', '--column': Name of the column used. Default='test'
    * '-m', '--method': Annotation library name. Required
    * '-n', '--ion_mode': Ionization mode. Choices='positive' or 'negative' - Default='positive'
    * '-s', '--species': Species the sample comes from. Default='human'
    * '-o', '--organ': Organ from which the sample was extracted. Default='plasma'
    * '-a', '--acquisition': Creates acquisition metadata for each file.
    * '-v', '--task_version': Submits the sample to a specific task revision. Default='86'
    * '-x', '--extra_profiles': Comma separated list of extra profiles to pass to springboot.
    * '-p', '--prepare': Preloads the acquisition data of samples.
    * '-r', '--schedule': Schedules the processing of samples.
    * '-t', '--test': Test run. Do not submit but print any data.
```

_file_ must be a text file or csv with a header 'samples' followed by the list of sample filenames (preferably without extension), one per line.

---
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
If you _REALY, REALY!_ want to use this, refer to the code.

---
## Old incomplete and unused scripts
Like the title implies: older, incomplete and/or obsolete files. **DO NOT USE**. 
- experimentAnalyzer.py
- older_scripts/ folder
