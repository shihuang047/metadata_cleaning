#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from os.path import join
import pandas as pd
import pytest
import glob

from pandas.util.testing import assert_frame_equal

from metadata_cleaning._df_utils import (
    validate_fp,
    validate_pd,
    read_input_metadata,
    parse_metadata_file
)


def test_validate_fp():
    with pytest.raises(FileNotFoundError) as e:
        validate_fp('string_not_file')
    assert ' do not exist.' in str(e.value)

    for md_fp in glob.glob(join("test_datasets", "input", "metadata", "*")):
        assert md_fp == validate_fp(md_fp)


def test_validate_pd():
    def assert_it(tab):
        with pytest.raises(ValueError) as e:
            validate_pd('FILE', tab)
        assert 'May only have one row in the metadata file FILE' in str(e.value) or\
               'May only have one column in the metadata file FILE' in str(e.value)
    assert_it(pd.DataFrame())
    assert_it(pd.DataFrame({'A': [], 'B': []}))
    assert_it(pd.DataFrame({'A': [1], 'B': [2]}))
    assert_it(pd.DataFrame({'A': [1,2,3,4]}))


def test_read_input_metadata():
    md_fp = join("test_datasets", "input", "metadata", "metadata_test_XYSampleDtypes.tsv")
    md_pd = pd.DataFrame({'X': ['1', '2', '3'],
                          'Y': ['1', '2', '3'],
                          'Z': [1, 2, 3]})
    assert_frame_equal(md_pd, read_input_metadata(md_fp, False, ['X', 'Y']))


def test_parse_metadata_file():
    md_fp = join("test_datasets", "input", "metadata", "metadata_test_XYSampleDtypes.tsv")
    md_pd = pd.DataFrame({'X': ['1', '2', '3'],
                          'Y': ['1', '2', '3'],
                          'Z': [1, 2, 3]})
    assert_frame_equal(md_pd, parse_metadata_file(md_fp, ['X', 'Y']))

    md_fp = join("test_datasets", "input", "metadata", 'metadata_test_full.tsv')
    sample_cols = ['sample_name']
    md_pd = pd.read_csv(md_fp, header=0, sep='\t',
                        dtype=dict((x, 'str') for x in sample_cols))
    assert_frame_equal(md_pd, parse_metadata_file(md_fp, sample_cols))

    sample_cols = ['sample_name', 'sample_id', '#SampleID', 'sample', '#SampleName', 'sam']
    md_fp = join("test_datasets", "input", "metadata", 'metadata_test_allSamID.tsv')
    md_pd = pd.read_csv(md_fp, header=0, sep='\t',
                        dtype=dict((x, 'str') for x in sample_cols))
    assert_frame_equal(md_pd, parse_metadata_file(md_fp, sample_cols))
