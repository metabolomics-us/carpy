import requests

bins = [13, 127]

for bin in bins:
    data = requests.get("https://binvestigate.fiehnlab.ucdavis.edu/rest/bin/{}".format(bin)).json()
    classifications = requests.get(
        "https://binvestigate.fiehnlab.ucdavis.edu/rest/bin/classificationTree/{}".format(bin)).json()

    id = data['id']
    name = data['name']
    inchikey = data['inchikey']
    retentionIndex = data['retentionIndex']
    kovats = data['kovats']
    quant = data['quantMass']
    spectra = data['spectra']

    data = []
    for species in classifications['value']:
        for organ in classifications['value'][species]:
            sample_count = classifications['value'][species][organ]['count']
            intensity = classifications['value'][species][organ]['intensity']

            data.append(
                {
                    'id': id,
                    'ri': retentionIndex,
                    'inchi': inchikey,
                    'kovats': kovats,
                    'quant': quant,
                    'spectra': spectra,
                    'species': species,
                    'organ': organ,
                    'samples': sample_count,
                    'avg intensity': intensity
                }
            )

    print(data)
