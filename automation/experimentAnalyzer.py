import simplejson as json


def get_latest_status(list):
    max = {}
    for status in list:
        if not max:
            max = status['M']
        else:
            if int(max['priority']['N']) < int(status['M']['priority']['N']):
                max = status['M']

    return max['value']['S']


if __name__ == '__main__':
    with open('tracking-info.json', 'r') as json_file:
        experiment = json.load(json_file)

    names = {}
    for samples in experiment['Items']:
        names['%s' % samples['sample']['S']] = get_latest_status(samples['status']['L'])

    # print([(k,v) for k, v in names.items() if v in ['failed', 'exported']])

    processed = []
    with open('/g/study-jenny/processed.txt', 'r') as pfile:
        processed.extend([p.split(" ")[-1].rstrip() for p in pfile.readlines()])

    for k,v in names.items():
        if k in processed:
            print(k, v)
