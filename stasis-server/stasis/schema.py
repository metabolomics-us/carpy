# this file contains all our schemas

# defines the schema of the incoming data object
__ACQUISITION_SCHEMA__ = {
    'sample': {
        'type': 'string'
    },
    'experiment': {
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
        }
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

# defines the incomming tracking schema
__TRACKING_SCHEMA__ = {
    'sample': {
        'type': 'string'
    },
    'status': {
        'type': 'string'
    },
    'fileHandle': {
        'type': 'string'
    },
    'required': ['sample', 'status']
}

# defines the schema of the incoming data object
__RESULT_SCHEMA__ = {
    'sample': {
        'type': 'string'
    },
    'injections': {
        'type': 'object',
        'patterProperties': {
            '^.*$': {
                'type': 'object',
                'logid': 'string',
                'correction': {
                    'polynomial': {
                        'type': 'integer'
                    },
                    'sampleUsed': {
                        'type': 'string'
                    },
                    'curve': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'x': {
                                'type': 'number'
                            },
                            'y': {
                                'type': 'number'
                            }
                        }
                    }
                },
                'results': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'target': {
                            'retentionIndex': {
                                'type': 'number'
                            },
                            'name': {
                                'type': 'string'
                            },
                            'id': {
                                'type': 'string'
                            },
                            'mass': {
                                'type': 'number'
                            }
                        },
                        'annotation': {
                            'retentionIndex': {
                                'type': 'number'
                            },
                            'intensity': {
                                'type': 'integer'
                            },
                            'replaced': {
                                'type': 'boolean'
                            },
                            'mass': {
                                'type': 'number'
                            }
                        }
                    }
                }
            },
            'required': ['correction']
        }
    },
    'required': ['sample', 'injections']
}

__SCHEDULE__ = {

    "$id": "http://example.com/example.json",
    "type": "object",
    "definitions": {},
    "$schema": "http://json-schema.org/draft-07/schema#",
    "properties": {
        "profile": {
            "$id": "/properties/profile",
            "type": "string",
            "title": "The Profile Schema ",
            "default": "",
            "examples": [
                "lcms",
                "gcms"
            ]
        },
        "env": {
            "$id": "/properties/env",
            "type": "string",
            "title": "The Env Schema ",
            "default": "",
            "examples": [
                "prod",
                "test",
                "dev"

            ]
        },
        "sample": {
            "$id": "/properties/sample",
            "type": "string",
            "title": "The Sample Schema ",
            "default": "",
            "examples": [
                "abc.mzml"
            ]
        },
        "method": {
            "$id": "/properties/method",
            "type": "string",
            "title": "The Method Schema ",
            "default": "",
            "examples": [
                "method name | instrument | column | ion mode"
            ]
        }
    }
}

# defines the input schema for a target
__TARGET_SCHEMA__ = {
    'properties': {
        'method': {
            'type': 'string'
        },
        'mz_rt': {
            'type': 'string'
        },
        'sample': {
            'type': 'string'
        },
        'name': {
            'type': 'string'
        }
    },
    'required': ['method', 'mz_rt', 'sample']
}
