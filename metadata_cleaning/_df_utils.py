#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os
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
    if 'na_value' in rules:
        nan_value = rules['na_value']
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


def write_clean_metadata(metadata_pd, metadata_fp, output_fp):
    """
    Write clean metadata file.

    Parameters
    ----------
    metadata_pd : str
        Clean metadata table.

    metadata_fp : str
        Path to the original metadata file.

    output_fp : str
        Path to the output metadata file.

    Returns
    -------
    output_fp : str
        Path to the output metadata file.
    """
    if not output_fp:
        output_fp = '%s_clean.tsv' % os.path.splitext(output_fp)[0]
    elif '.' not in output_fp or len(output_fp.split('.')[-1])>15:
        output_fp = '%s_clean.tsv' % output_fp
    metadata_pd.to_csv(output_fp, index=False, sep='\t')
    return output_fp


def write_clean_metadata_user(metadata_pd, metadata_fp, output_fp, nan_value_user):
    """
    Write clean metadata file with user-specified NaN encoding

    Parameters
    ----------
    metadata_pd : str
        Clean metadata table.

    metadata_fp : str
        Path to the original metadata file.

    output_fp : str
        Path to the output metadata file.

    nan_value_user : str
        Value to use for replacement for NaN declared by user.


    Returns
    -------
    output_fp : str
        Path to the output metadata file.
    """
    # edit to make another copy of the file with actual np.nan in the numeric columns
    # (so that these columns can be read as numeric)
    if not output_fp:
        if str(getpass.getuser()):
            output_fp = '%s_%s.tsv' % (os.path.splitext(metadata_fp)[0], str(getpass.getuser()))
        else:
            output_fp = '%s_user.tsv' % os.path.splitext(metadata_fp)[0]
    elif '.' not in output_fp or len(output_fp.split('.')[-1]) > 15:
        output_fp = '%s_clean_%s.tsv' % (output_fp, str(getpass.getuser()))
    metadata_pd = metadata_pd.fillna(str(nan_value_user))
    metadata_pd.to_csv(output_fp, index=False, sep='\t')
    return output_fp


def write_outputs(metadata_pd, metadata_fp, output_fp, nan_value, nan_value_user):

    clean_metadata_fps = []

    clean_metadata_fps.append(
        write_clean_metadata(
            metadata_pd,
            metadata_fp,
            output_fp
        )
    )
    if nan_value_user != nan_value:
        clean_metadata_fps.append(
            write_clean_metadata_user(
                metadata_pd,
                metadata_fp,
                nan_value_user,
                output_fp
            )
        )
    return clean_metadata_fps
