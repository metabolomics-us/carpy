# this file contains all our schemas

# defines the schema of the incoming data object
__ACQUISITION_SCHEMA__ = {
    'sample': {
        'type': 'string'
    },
    'acquisition': {
        'instrument': {
            'type': 'string'
        },
        'name': {
            'type': 'string'
        },
        'ionisation': {
            'type': 'string'
        },
        'method': {
            'type': 'string'
        },
    },
    'metadata': {
        'class': {
            'type': 'string'
        },
        'species': {
            'type': 'string'
        },
        'organ': {
            'type': 'string'
        },
    },
    'userdata': {
        'label': {
            'type': 'string'
        },
        'comment': {
            'type': 'string'
        },
    },

    'references': {
        'type': 'array',
        'items': {
            'type': 'object',
            'name': {
                'type': 'string'
            },
            'value': {
                'type': 'string'
            },
        }
    },

    'required': ['userdata', 'metadata', 'acquisition', 'sample']
}
