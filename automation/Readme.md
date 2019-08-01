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
    * '-t', '--test': Test run. Do not submit any data but prints operations.
    * '-v', '--version': Only used in development. Selects the executable version to run.
```

_file_ must be a text file or csv with a header 'samples' followed by the list of sample filenames, one per line.

### Example
```bash
python3 runner.py -e teddy -i 6530 -m csh -n positive -c c18 -s human -o plasma -p -a -r /home/user/docs/samples.txt
```