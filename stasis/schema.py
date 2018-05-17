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
        'ionisation': {
            'type': 'string'
        },
        'method': {
            'type': 'string'
        },
        'required': ['instrument', 'method']
    },
    'processing': {
        'method': {
            'type': 'string'
        },
        'required': ['method']
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
        'required': ['class', 'species', 'organ']
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

            'required': ['name', 'value']
        }
    },

    'required': ['metadata', 'acquisition', 'sample', 'processing']
}
