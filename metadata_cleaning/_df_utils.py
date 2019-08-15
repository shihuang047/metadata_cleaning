#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd


def get_nan_value_and_sampleID_cols(rules):
    """
    Get the default "NaN" values that will be used
    in the per_column rules.

    Parameters
    ----------
    rules : dict
        All rules in the following keys:
            ['booleans', 'combinations', 'nans',
            'per_column', 'sample_id', 'time_format']

    Returns
    -------
    nan_value : str
        Value to use as default in offending condition
        when not specified explicitly.
    """
    if 'nan_value' in rules:
        nan_value = rules['nan_value']
    else:
        nan_value = 'Missing'

    if 'sample_id' in rules:
        if 'sample_id_cols' in rules['sample_id']:
            return nan_value, rules['sample_id']['sample_id_cols']
    return nan_value, None


def read_input_metadata(file_path, is_excel=False, as_str=None):
    """
    Read metadata file.

    Parameters
    ----------
    file_path : str
        Path to the metadata file.

    is_excel : bool
        Whether the file is an excel file.

    as_str : list
        Metadata columns containing samples IDs.

    Returns
    -------
    tab_pd : pd.DataFrame
        Metadata table in pandas dataframe format.
    """
    if as_str:
        as_str_d = dict([x, 'str'] for x in as_str)
    else:
        as_str_d = {'#SampleID': 'str', 'sample_name': 'str'}

    if is_excel:
        # metadata for the sgotgun selection
        tab_pd = pd.read_excel(file_path, header=0,
                               sep='\t', dtype=as_str_d)
    else:
        tab_pd = pd.read_csv(file_path, header=0,
                             sep='\t', dtype=as_str_d)
    return tab_pd