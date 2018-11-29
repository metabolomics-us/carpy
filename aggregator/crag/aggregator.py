import numpy
import os
import pandas as pd
import re
import requests
import time

AVG_BR_ = 'AVG (br)'

# RSD_SA_ = '% RSD (sa)'
RSD_BR_ = '% RSD (br)'

stasis_url = "https://api.metabolomics.us/stasis"
test_url = "https://test-api.metabolomics.us/stasis"


def get_experiment_files(experiment) -> [str]:
    """
    NOT USED ATM
    Calls the stasis api to get a list files for an experiment
    :param experiment: name of experiment for which to get the list of files
    :return: dictionary with results or {error: msg}
    """
    print(f'{time.strftime("%H:%M:%S")} - Getting experiment files')
    response = requests.get(stasis_url + '/experiment/' + experiment)

    files = []
    if response.status_code == 200:
        files = [item['sample'] for item in response.json()]

    return files


def get_sample_tracking(filename):
    """
    NOT USED ATM
    Calls the stasis api to get the tracking status for a single file
    :param filename: name of file to get tracking info from
    :return: dictionary with tracking or {error: msg}
    """
    print(f'{time.strftime("%H:%M:%S")} - Getting filename status')
    response = requests.get(stasis_url + '/tracking/' + filename)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "no tracking info"}


def get_sample_metadata(filename, log):
    """
    Calls the stasis api to get the metadata for a single file
    :param filename: name of file to get metadata from
    :param log:
    :return: dictionary with metadata or {error: msg}
    """
    response = requests.get(stasis_url + '/acquisition/' + filename)

    if log:
        print(response)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "no metadata info"}



def getFileResults(filename, log):
    """
    Calls the stasis api to get the results for a single file
    :param filename: name of file to get results from
    :param log:
    :return: dictionary with results or {error: msg}
    """

    if filename[-5:] == '.mzml': filename = filename[:-5]

    print(f'{time.strftime("%H:%M:%S")} - Getting results for file \'{filename}\'')
    response = requests.get(stasis_url + "/result/" + filename)

    if response.status_code == 200:
        data = response.json()
        data['metadata'] = get_sample_metadata(filename, log)

    else:
        data = {'error': f'no results. {response.reason}'}

    if log:
        print(response.json())

    return data


def findReplaced(value):
    """
    Returns the intensity value only for replaced data
    :param value: the entire annotation object
    :return: intensity value if replaced or 0 if not replaced
    """
    if value['replaced']:
        return round(value["intensity"])
    else:
        return 0


def format_sample(data):
    """
    filters the incoming sample data separating intensity, mass, retention index and replacement values
    :param data:
    :return:
    """
    intensities = []
    masses = []
    rts = []
    curve = []
    replaced = []

    for k, v in data['injections'].items():
        intensities = {k: [round(r['annotation']['intensity']) for r in v['results']]}
        masses = {k: [round(r['annotation']['mass'], 4) for r in v['results']]}
        rts = {k: [round(r['annotation']['retentionIndex'], 2) for r in v['results']]}
        curve = {k: [r for r in v['correction']['curve']]}
        replaced = {k: [findReplaced(r['annotation']) for r in v['results']]}

    return [intensities, masses, rts, curve, replaced]


def format_metadata(data):
    names = []
    rts = []
    masses = []

    pattern = re.compile(".*?_[A-Z]{14}-[A-Z]{10}-[A-Z]")

    for k, v in data['injections'].items():
        names = [r['target']['name'] for r in v['results']]
        rts = [r['target']['retentionIndex'] for r in v['results']]
        masses = [r['target']['mass'] for r in v['results']]

    inchikeys = [name.split('_')[-1] if pattern.match(name) else None for name in names]
    names2 = [name.rsplit('_', maxsplit=1)[0] if pattern.match(name) else name for name in names]

    metadata = pd.DataFrame({'name': names2, 'ri(s)': rts, 'mz': masses, 'inchikey': inchikeys,
                             AVG_BR_: pd.np.nan, RSD_BR_: pd.np.nan})
    return metadata


def export_excel(intensity, mass, rt, curve, replaced, infile, test):
    # saving excel file
    print(f'{time.strftime("%H:%M:%S")} - Exporting excel file')
    file, ext = os.path.splitext(infile)
    output_name = f'{file}_results.xlsx'

    if test:
        output_name = f'{file}_testResults.xlsx'

    intensity.set_index('name')
    mass.set_index('name')
    rt.set_index('name')
    replaced.set_index('name')

    writer = pd.ExcelWriter(output_name)
    intensity.fillna('').to_excel(writer, 'Intensity matrix')
    mass.fillna('').to_excel(writer, 'Mass matrix')
    rt.fillna('').to_excel(writer, 'Retention index matrix')
    replaced.fillna('').to_excel(writer, 'Replaced values')
    curve.fillna('').to_excel(writer, 'Correction curves')
    writer.save()


def calculate_delta(intensity, mass, rt):
    """
    NOT USED ANYMORE
    :param intensity:
    :param mass:
    :param rt:
    :return:
    """
    print(f'{time.strftime("%H:%M:%S")} - Calculating ranges for intensity, mass and RT (ignoring missing results)')
    numpy.seterr(invalid='log')

    for i in range(len(intensity)):
        intensity.loc[i, 'delta'] = intensity.iloc[i, 4:].max() - intensity.iloc[i, 4:].min()
        mass.loc[i, 'delta'] = mass.iloc[i, 4:].max() - mass.iloc[i, 4:].min()
        rt.loc[i, 'delta'] = rt.iloc[i, 4:].max() - rt.iloc[i, 4:].min()


def calculate_average(intensity, mass, rt, biorecs):
    """
    Calculates the average intensity, mass and retention index of biorecs
    :param intensity:
    :param mass:
    :param rt:
    :param biorecs:
    :return:
    """
    print(f'{time.strftime("%H:%M:%S")} - Calculating average of biorecs for intensity, mass and RT (ignoring missing '
          f'results)')
    numpy.seterr(invalid='log')

    for i in range(len(intensity)):
        intensity.loc[i, AVG_BR_] = intensity.loc[i, biorecs].mean()
        mass.loc[i, AVG_BR_] = mass.loc[i, biorecs].mean()
        rt.loc[i, AVG_BR_] = rt.loc[i, biorecs].mean()


def calculate_rsd(intensity, mass, rt, biorecs):
    """
    Calculates intensity, mass and retention index Relative Standard Deviation of biorecs
    :param intensity:
    :param mass:
    :param rt:
    :param biorecs:
    :return:
    """
    print(f'{time.strftime("%H:%M:%S")} - Calculating %RDS of biorecs for intensity, mass and RT (ignoring missing '
          f'results)')
    size = range(len(intensity))
    numpy.seterr(invalid='log')

    for i in size:
        try:
            intensity.loc[i, RSD_BR_] = (intensity.loc[i, biorecs].std() / intensity.loc[i, biorecs].mean()) * 100
        except Exception as e:
            print(f'{time.strftime("%H:%M:%S")} - Can\'t calculate % RSD for target {intensity.loc[i, "name"]}.'
                  f' Sum of intensities = {intensity.loc[i, biorecs].sum()}')
        mass.loc[i, RSD_BR_] = (mass.loc[i, biorecs].std() / mass.loc[i, biorecs].mean()) * 100
        rt.loc[i, RSD_BR_] = (rt.loc[i, biorecs].std() / rt.loc[i, biorecs].mean()) * 100


def chunker(list, size):
    """
    Splits a list in 'pages'
    :param list: original list to split
    :param size: amount of items in each 'page'
    :return: list of splits
    """
    return (list[pos:pos + size] for pos in range(0, len(list), size))


def aggregate(args):
    """
    Collects information on the experiment and decides if aggregation of the full experiment is possible

    :param args: parameters containing the experiment name
    :return: the filename of the aggregated (excel) file
    """

    # commented since it returns partial list of experiment files
    # print(f"Aggregating results for experiment '{args.experiment}'")
    # files = getExperimentFiles(args.experiment)
    # print(files)

    for file in args.infiles:
        process_file(file, args)


def process_file(infile, args):
    if not os.path.isfile(infile):
        print(f'Can\'t find the file {infile}')
        exit(-1)

    with open(infile) as processed:
        samples = [p.strip() for p in processed.readlines() if p]

    if args.test:
        samples = samples[3:7]

    # creating target section
    first_data = ""
    for sample in samples:
        if sample in ['samples']: continue
        first_data = getFileResults(sample, False)
        if 'error' not in first_data: break
    intensity = format_metadata(first_data)
    mass = format_metadata(first_data)
    rt = format_metadata(first_data)
    curve = format_metadata(first_data)
    replaced = format_metadata(first_data)
    # adding intensity matrix
    for chunk in chunker(samples, 1000):
        for sample in chunk:
            if sample in ['samples']: continue
            data = getFileResults(sample, False)
            if 'error' not in data:
                formatted = format_sample(data)
                intensity[sample] = pd.DataFrame.from_dict(formatted[0])
                mass[sample] = pd.DataFrame.from_dict(formatted[1])
                rt[sample] = pd.DataFrame.from_dict(formatted[2])
                curve[sample] = pd.DataFrame.from_dict(formatted[3])
                replaced[sample] = pd.DataFrame.from_dict(formatted[4])
            else:
                intensity[sample] = pd.np.nan
                mass[sample] = pd.np.nan
                rt[sample] = pd.np.nan
                replaced[sample] = pd.np.nan

    biorecs = [br for br in intensity.columns if 'biorec' in str(br).lower() or 'qc' in str(br).lower()]
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 1000)

    #    calculate_delta(intensity, mass, rt)
    try:
        calculate_average(intensity, mass, rt, biorecs)
    except Exception as e:
        print("Error in average calculation: " + e)
    try:
        calculate_rsd(intensity, mass, rt, biorecs)
    except Exception as e:
        print("Error in average calculation: " + e)
    try:
        export_excel(intensity, mass, rt, curve, replaced, infile, args.test)
    except Exception as e:
        print("Error in average calculation: " + e)
