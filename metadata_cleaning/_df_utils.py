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
import getpass

from metadata_cleaning.tests._utils_test import build_dummy_dataset


def validate_fp(fp):
    """
    Does some basic validation on the passed file.
    """
    if not os.path.isfile(fp):
        raise FileNotFoundError(
            "'%s' do not exist." % fp
        )


def validate_pd(metadata_fp, metadata_pd):
    """
    Does some basic validation on the DataFrame.
    # inspired from https://github.com/biocore/qurro/
       Checks not empty.
    """
    if metadata_pd.shape[0] < 2:
        raise ValueError(
            "May only have one row in the metadata file {}.".format(metadata_fp)
        )
    if metadata_pd.shape[1] < 2:
        raise ValueError(
            "May only have one column in the metadata file {}.".format(metadata_fp)
        )


def parse_metadata_file(sample_id_cols, metadata_fp=None, do_dummy=False):
    """
    Read the metadata input file.

    Parameters
    ----------
    sample_id_cols : list
        Names of the columns containing the sample IDs

    metadata_fp : str
        File path for the metadata file
        if either excel of tab-separated format.

    do_dummy : bool
        Tells whether to jsut run things
        on the dummy dataset.

    Returns
    -------
    metadata_pd : pd.DataFrame
        Metadata data frame.
    """
    if do_dummy:
        metadata_fp = None
        metadata_pd = build_dummy_dataset()
    else:
        if not metadata_fp:
            metadata_fp = os.path.join(
                "tests", "test_datasets", "dummy.tsv"
            )
        validate_fp(metadata_fp)
        if 'xls' in os.path.splitext(metadata_fp)[1]:
            metadata_pd = read_input_metadata(metadata_fp, True, sample_id_cols)
        else:
            metadata_pd = read_input_metadata(metadata_fp, False, sample_id_cols)
        validate_pd(metadata_fp, metadata_pd)
    return metadata_pd


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
        as_str_d = dict((x, 'str') for x in as_str)
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
    metadata_pd : pd.DataFrame
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
        output_fp = '%s_clean.tsv' % os.path.splitext(metadata_fp)[0]
    elif '.' not in output_fp or len(output_fp.split('.')[-1])>15:
        output_fp = '%s_clean.tsv' % output_fp
    metadata_pd.to_csv(output_fp, index=False, sep='\t')
    return output_fp


def write_clean_metadata_user(metadata_pd, metadata_fp, output_fp, nan_value_user):
    """
    Write clean metadata file with user-specified NaN encoding

    Parameters
    ----------
    metadata_pd : pd.DataFrame
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
            output_fp = '%s_clean_%s.tsv' % (os.path.splitext(metadata_fp)[0], str(getpass.getuser()))
        else:
            output_fp = '%s_clean_user.tsv' % os.path.splitext(metadata_fp)[0]
    elif '.' not in output_fp or len(output_fp.split('.')[-1]) > 15:
        output_fp = '%s_clean_%s.tsv' % (output_fp, str(getpass.getuser()))
    metadata_out_pd = metadata_pd.fillna(str(nan_value_user)).copy()
    metadata_out_pd.to_csv(output_fp, index=False, sep='\t')
    return output_fp


def write_outputs(metadata_pd, metadata_fp, output_fp, nan_value, nan_value_user):

    clean_metadata_fps = list()

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
                output_fp,
                nan_value_user
            )
        )
    if clean_metadata_fps:
        print("\nOutput(s) of metadata_cleaning:")
        print('\n'.join(clean_metadata_fps))
        return 0

    return 1
