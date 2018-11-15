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


def getExperimentFiles(experiment) -> [str]:
    """
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


def getSampleTracking(filename):
    """
    Calls the stasis api to get the tracking status for a single file
    :param filename: name of file to get tracking info from
    :return: dictionary with tracking or {error: msg}
    """
    print(f'{time.strftime("%H:%M:%S")} - Getting filename status')
    response = requests.get(stasis_url + "/tracking/" + filename)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "no tracking info"}


def getFileResults(filename):
    """
    Calls the stasis api to get the results for a single file
    :param filename: name of file to get results from
    :return: dictionary with results or {error: msg}
    """

    if filename[-5:] == '.mzml': filename = filename[:-5]

    print(f'{time.strftime("%H:%M:%S")} - Getting results for file \'{filename}\'')
    response = requests.get(stasis_url + "/result/" + filename)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f'no results. {response.reason}'}


def format_sample(data):
    intensities = []
    masses = []
    rts = []
    curve = []

    for k, v in data['injections'].items():
        intensities = {k: [round(r['annotation']['intensity']) for r in v['results']]}
        masses = {k: [r['annotation']['mass'] for r in v['results']]}
        rts = {k: [r['annotation']['retentionIndex'] for r in v['results']]}
        curve = {k: [r for r in v['correction']['curve']]}

    return [intensities, masses, rts, curve]


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
                             'delta': pd.np.nan, AVG_BR_: pd.np.nan, RSD_BR_: pd.np.nan})
    return metadata


def export_excel(intensity, mass, rt, curve, args):
    # saving excel file
    print(f'{time.strftime("%H:%M:%S")} - Exporting excel file')
    file, ext = os.path.splitext(args.input)
    output_name = f'{file}_results.xlsx'

    if args.test:
        output_name = f'{file}_testResults.xlsx'

    intensity.set_index('name')
    mass.set_index('name')
    rt.set_index('name')

    writer = pd.ExcelWriter(output_name)
    intensity.fillna('').to_excel(writer, 'Intensity matrix')
    mass.fillna('NA').to_excel(writer, 'Mass matrix')
    rt.fillna('NA').to_excel(writer, 'Retention index matrix')
    curve.fillna('NA').to_excel(writer, 'Correction curves')
    writer.save()


def calculate_delta(intensity, mass, rt):
    print(f'{time.strftime("%H:%M:%S")} - Calculating ranges for intensity, mass and RT (ignoring missing results)')

    for i in range(len(intensity)):
        intensity.loc[i, 'delta'] = intensity.iloc[i, 4:].max() - intensity.iloc[i, 4:].min()
        mass.loc[i, 'delta'] = mass.iloc[i, 4:].max() - mass.iloc[i, 4:].min()
        rt.loc[i, 'delta'] = rt.iloc[i, 4:].max() - rt.iloc[i, 4:].min()


def calculate_average(intensity, mass, rt, biorecs):
    print(
        f'{time.strftime("%H:%M:%S")} - Calculating average of biorecs for intensity, mass and RT (ignoring missing results)')

    for i in range(len(intensity)):
        intensity.loc[i, AVG_BR_] = intensity.loc[i, biorecs].mean()
        mass.loc[i, AVG_BR_] = mass.loc[i, biorecs].mean()
        rt.loc[i, AVG_BR_] = rt.loc[i, biorecs].mean()


def calculate_rsd(intensity, mass, rt, biorecs):
    print(
        f'{time.strftime("%H:%M:%S")} - Calculating %RDS of biorecs for intensity, mass and RT (ignoring missing results)')
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

    if not os.path.isfile(args.input):
        print(f'Can\'t find the file {args.input}')
        exit(-1)

    with open(args.input) as processed:
        files = [p.strip() for p in processed.readlines() if p]

    if args.test:
        files = files[3:5]

    # creating target section
    first_data = ""
    for file in files:
        if file in ['samples']: continue
        first_data = getFileResults(file)
        if 'error' not in first_data: break

    intensity = format_metadata(first_data)
    mass = format_metadata(first_data)
    rt = format_metadata(first_data)
    curve = format_metadata(first_data)

    # adding intensity matrix
    for chunk in chunker(files, 1000):
        for file in chunk:
            if file in ['samples']: continue
            data = getFileResults(file)
            if 'error' not in data:
                formatted = format_sample(data)
                intensity[file] = pd.DataFrame.from_dict(formatted[0])
                mass[file] = pd.DataFrame.from_dict(formatted[1])
                rt[file] = pd.DataFrame.from_dict(formatted[2])
                curve[file] = pd.DataFrame.from_dict(formatted[3])
            else:
                intensity[file] = pd.np.nan
                mass[file] = pd.np.nan
                rt[file] = pd.np.nan

    biorecs = [br for br in intensity.columns if 'biorec' in str(br).lower()]

    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 1000)

    calculate_delta(intensity, mass, rt)

    calculate_average(intensity, mass, rt, biorecs)

    calculate_rsd(intensity, mass, rt, biorecs)

    export_excel(intensity, mass, rt, curve, args)
