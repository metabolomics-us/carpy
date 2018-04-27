#!/usr/bin/env python

from __future__ import print_function

import datetime
import json
import untangle


def parse_minix_xml(f):
    """Creates a list of sample descriptions for a given MiniX XML file"""

    x = untangle.parse(f)
    samples = []

    for c in x.experiment.classes.get_elements():
        for sample in c.samples.sample:
            filename = sample['fileName'].split(',')[-1]
            
            title = x.experiment['title'].split(',')
            method = title[-2].strip() if len(title) > 2 else ''

            if not filename.startswith('please_change_me'):
                samples.append({
                    'id': filename,
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

                    'acquisition': {
                        'instrument': x.experiment.architecture['name'],
                        'method': method
                    },

                    'metadata': {
                        'class': c['id'],
                        'species': c['species'],
                        'organ': c['organ']
                    },

                    'userdata': {
                        'label': sample['label'],
                        'comment': sample['comment'],
                    },
                })

    return samples


if __name__ == '__main__':
    parse_minix_xml(open('375786.xml'))