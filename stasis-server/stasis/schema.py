# this file contains all our schemas

# defines the schema of the incoming data object
__ACQUISITION_SCHEMA__ = {
    'sample': {
        'type': 'string',
        'minLength': 1
    },
    'experiment': {
        'type': 'string',
        'minLength': 1
    },
    'acquisition': {
        'instrument': {
            'type': 'string',
            'minLength': 1
        },
        'ionisation': {
            'type': 'string',
            'minLength': 1
        },
        'method': {
            'type': 'string',
            'minLength': 1
        },
        'required': ['instrument', 'method']
    },
    'processing': {
        'method': {
            'type': 'string',
            'minLength': 1
        },
        'required': ['method']
    },
    'metadata': {
        'class': {
            'type': 'string',
            'minLength': 1
        },
        'species': {
            'type': 'string',
            'minLength': 1
        },
        'organ': {
            'type': 'string',
            'minLength': 1
        },
        'required': ['class', 'species', 'organ']
    },
    'userdata': {
        'label': {
            'type': 'string',
            'minLength': 1
        },
        'comment': {
            'type': 'string',
            'minLength': 1
        }
    },
    'references': {
        'type': 'array',
        'items': {
            'type': 'object',
            'name': {
                'type': 'string',
                'minLength': 1
            },
            'value': {
                'type': 'string',
                'minLength': 1
            },
            'required': ['name', 'value']
        }
    },

    'required': ['metadata', 'acquisition', 'sample', 'processing']
}

# defines the incomming tracking schema
__TRACKING_SCHEMA__ = {
    '$id': 'http://example.com/example.json',
    'type': 'object',
    'definitions': {},
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'properties': {
        'sample': {
            'type': 'string',
            'minLength': 1
        },
        'status': {
            'type': 'string',
            'minLength': 1
        },
        'fileHandle': {
            'type': 'string',
            'minLength': 1
        }},
    'required': ['sample', 'status']
}

# defines the incomming tracking schema
__JOB_SCHEMA__ = {

    '$id': 'http://example.com/example.json',
    'type': 'object',
    'definitions': {},
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'properties': {
        'samples': {
            'type': 'array',
            'minItems': 1,
            'uniqueItems': True,
            'items': {
                'type': 'string',
                'minLength': 1
            }
        },
        'status': {
            'type': 'string',
            'minLength': 1

        },
        'method': {
            'type': 'string',
            'minLength': 1
        },
        'profile': {
            'type': 'string',
            'minLength': 1
        },
        'resource': {
            'type': 'string',
            'minLength': 1
        },
        'env': {
            'type': 'string',
            'minLength': 1
        },
        'id': {
            'type': 'string',
            'minLength': 1
        },
        'notify': {
            'type': 'object',
            'properties': {
                'email': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'minLength': 1
                    }
                }
            }
        },
        'meta': {
            'type': 'object',
            'properties': {
                'tracking': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'state': {
                                'type': 'string',
                                'minLength': 1
                            },
                            'extension': {
                                'type': 'string',
                                'minLength': 1
                            }
                        },
                        'required': [
                            'state'
                        ]
                    }
                }
            }
        }
    }
    ,
    'required': [
        'samples',
        'profile',
        'method',
        'env',
        'id'
    ]
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
    '$id': 'http://example.com/example.json',
    'type': 'object',
    'definitions': {},
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'properties': {
        'profile': {
            '$id': '/properties/profile',
            'type': 'string',
            'title': 'The Profile Schema ',
            'default': '',
            'examples': [
                'lcms',
                'gcms'
            ]
        },
        'env': {
            '$id': '/properties/env',
            'type': 'string',
            'title': 'The Env Schema ',
            'default': '',
            'examples': [
                'prod',
                'test',
                'dev'

            ]
        },
        'sample': {
            '$id': '/properties/sample',
            'type': 'string',
            'title': 'The Sample Schema ',
            'default': '',
            'examples': [
                'abc'
            ]
        },
        'method': {
            '$id': '/properties/method',
            'type': 'string',
            'title': 'The Method Schema ',
            'default': '',
            'examples': [
                'method name | instrument | column | ion mode'
            ]
        }
    }
}
