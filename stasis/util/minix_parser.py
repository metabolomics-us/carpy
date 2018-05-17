#!/usr/bin/env python

from __future__ import print_function

import untangle


def parse_minix_xml(f):
    """Creates a list of sample descriptions for a given MiniX XML file"""

    x = untangle.parse(f)
    samples = []

    for c in x.experiment.classes.get_elements():
        for sample in c.samples.sample:
            filename = sample['fileName'].split(',')[-1]

            title = x.experiment['title'].split(',')
            method = title[-2].strip() if len(title) > 2 else x.experiment.architecture['name']

            if not filename.startswith('please_change_me'):
                samples.append({
                    'sample': filename,

                    'acquisition': {
                        'instrument': x.experiment.architecture['name'],
                        'name': method,
                        'ionisation': 'positive',  # psotivie || lcms
                        'method': 'gcms'  # gcms || lcms
                    },

                    'metadata': {
                        'class': c['id'],
                        'species': c['species'],
                        'organ': c['organ']
                    },

                    'processing' : {
                        'method' : 'rtx5'
                    },

                    'userdata': {
                        'label': sample['label'],
                        'comment': sample['comment'],
                    },
                })

    return samples
