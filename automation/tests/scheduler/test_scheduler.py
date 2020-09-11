#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint


def test_add_metadata(scheduler, stasis_cli, data):
    scheduler.create_metadata(data['sample'], scheduler.config['experiment']['chromatography'][0],
                              {'class': 'plasma', 'specie': 's-test', 'organ': 'o-test'})

    metadata = stasis_cli.sample_acquisition_get('test-file')
    assert metadata is not None
    pprint.pprint(metadata)


def test_add_tracking(scheduler, stasis_cli, data):
    scheduler.add_tracking('test-file')

    status = stasis_cli.sample_state('test-file')
    assert status is not None
    assert 3 == len(status)


def test_process(scheduler, config):
    result = scheduler.process('../../resources/')

    assert result is not None
