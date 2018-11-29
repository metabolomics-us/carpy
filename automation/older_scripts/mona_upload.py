import argparse
import os
import requests
import simplejson as json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-H', '--host', help='mona hostname', default='lambic.fiehnlab.ucdavis.edu')
    parser.add_argument('-P', '--port', help='mona port', default='9090')
    parser.add_argument('-u', '--user', help='mona username', default='admin')
    parser.add_argument('-p', '--password', help='mona password', default='admin')
    args = parser.parse_args()

    MONA_URL = f'http://{args.host}:{args.port}'

    token = \
    requests.post(MONA_URL + '/rest/auth/login', json={'username': args.user, 'password': args.password}).json()[
        'token']
    header = {'Authorization': 'Bearer %s' % token}

    print('Uploading to', MONA_URL)
    print('Authenticated with token: %s' % token)

    hash_map = {}

    if os.path.exists(args.filename.replace('.json', '.hashmap.json')):
        hash_map = json.load(open(args.filename.replace('.json', '.hashmap.json')))

    success_count = 0
    failed_spectra = []
    output_uploaded = False

    with open(args.filename) as f:
        data = json.load(f)

        for i, spectrum in enumerate(data):
            spectrum_id = spectrum['id'] if 'id' in spectrum else ''
            print(i + 1, '/', len(data), spectrum_id)

            if spectrum_id and 'checksum' in spectrum and spectrum_id in hash_map and hash_map[spectrum_id] == spectrum[
                'checksum']:
                print('\tSkipping...')
                continue

            r = requests.post(MONA_URL + '/rest/spectra/', headers=header, json=spectrum)

            if r.status_code == 200:
                success_count += 1

                if 'id' not in spectrum:
                    output_uploaded = True
                    spectrum['id'] = r.json()['id']
                    print('\tAssigned id %s' % spectrum['id'])
            else:
                print('\tError with status code %d' % r.status_code)
                print('\t%s' % r.text)
                failed_spectra.append(spectrum)

    print('Successes %d, Failures %d' % (success_count, len(failed_spectra)))

    basename = args.filename.rsplit('.', 1)[0]

    if output_uploaded:
        with open(basename + '_uploaded.json', 'w') as fout:
            print(json.dumps(data, indent=4), file=fout)

    if failed_spectra:
        with open(basename + '_upload_failures.json', 'w') as fout:
            print(json.dumps(failed_spectra, indent=4), file=fout)
        print('Dumped %d failures to %s' % (len(failed_spectra), args.filename + '_delete_failures.json'))
