#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import numpy as np
import getpass


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
    nan_value : str / np.nan
        Value to use for replacement for NaN / declared as such
    """
    if 'nan_value' in rules:
        nan_value = rules['nan_value']
    else:
        nan_value = np.nan

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
    md_pd : pd.DataFrame
        Metadata table in pandas dataframe format.
    """
    if as_str:
        as_str_d = dict([x, 'str'] for x in as_str)
    else:
        as_str_d = {'#SampleID': 'str', 'sample_name': 'str'}

    if is_excel:
        # metadata for the sgotgun selection
        md_pd = pd.read_excel(file_path, header=0,
                              sep='\t', dtype=as_str_d)
    else:
        md_pd = pd.read_csv(file_path, header=0,
                            sep='\t', dtype=as_str_d)
    return md_pd


def write_clean_metadata(file_path, md_pd):
    """
    Write clean metadata file.

    Parameters
    ----------
    file_path : str
        Path to the original metadata file.
    """
    file_path_out = '%s_clean.tsv' % os.path.splitext(file_path)[0]
    md_pd.to_csv(file_path_out, index=False, sep='\t')
    print('Written:', file_path_out)


def write_clean_metadata_user(file_path, md_pd, nan_value_user, nan_value):
    """
    Write clean metadata file with user-specified NaN encoding

    Parameters
    ----------
    file_path : str
        Path to the original metadata file.

    md_pd : pd.DataFrame
        Metadata table in pandas dataframe format.

    nan_value_user : str
        Value to use for replacement for NaN declared by user.

    nan_value : np.nan
        Value to use for replacement for NaN.
    """
    if nan_value_user != nan_value:
        # edit to make another copy of the file with actual np.nan in the numeric columns
        # (so that these columns can be read as numeric)
        if str(getpass.getuser()):
            file_path_out_usr = '%s_%s.tsv' % (os.path.splitext(file_path_out)[0], str(getpass.getuser()))
        else:
            file_path_out_usr = '%s_user.tsv' % os.path.splitext(file_path_out)[0]
        md_pd = md_pd.fillna(nan_value_user)
        md_pd.to_csv(file_path_out_usr, index=False, sep='\t')
        print('Written:', file_path_out_usr)
    return md_pd
