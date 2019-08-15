#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd


def fill_col_nans(cur_nans, column, NANs):
    """
    Fetch the freshly identified dtypes of each column
    and apply it to the main metadata.

    Parameters
    ----------
    dtypes_final : dict
        dtypes inferred from the metadata and verified
        e.g. {'sample_name': 'O',
              ...
              'age_years': 'Q'}

    md_pd : pd.DataFrame
        original metadata table

    Returns
    -------
    md_pd : pd.DataFrame
        final metadata table with updated dtypes
    """
    for nan in sorted(cur_nans):
        NANs.setdefault(nan, []).append(column)
    return NANs

def check_nan(md, column):
    """
    Get the count of nan.

    Parameters
    ----------
    dtypes_final : dict
        dtypes inferred from the metadata and verified
        e.g. {'sample_name': 'O',
              ...
              'age_years': 'Q'}

    md_pd : pd.DataFrame
        original metadata table

    Returns
    -------
    md_pd : pd.DataFrame
        final metadata table with updated dtypes
    """
    col_content = md[column]
    # col_size = col_content.size
    col_null = col_content.isnull()
    non_nan_idx = col_content[col_null==False].index
    # col_null_num = col_null.sum()
    cur_nans = set([str(x) for x in col_content[col_null]])
    col_non_null_counts = col_content[col_null==False].value_counts()
    return cur_nans, non_nan_idx