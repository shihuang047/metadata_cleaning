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
import re


def make_regex_from_nan_value(nan_value):
    """
    Get the regex allowing finding persistent NaN values
    """
    if nan_value:
        if isinstance(nan_value, str):
            regex_nan = nan_value
        elif isinstance(nan_value, list):
            regex_nan = '|'.join([x[1:] for x in sorted(nan_value)])
            regex_nan = regex_nan.replace(
                'o data', 'o data|o_data'
            ).replace(
                'ot provided', 'ot provided|ot_provided'
            ).copy()
        else:
            regex_nan = 'nan'
    else:
        regex_nan = 'nan'
    return regex_nan


def set_column_dtypes(dtypes, column, float_to_string):
    """
    Fill the dtypes object with the temporary dtype inferred from the data
    """
    # add temporary inferred dtype of the column
    if not float_to_string[2]:
        #  if there is no non-float in the column
        # (note the column could be only np.nan, which are floats!)
        dtypes[column].append('float64')
    elif float_to_string[2]:
        # if there is at least one non-float
        if float_to_string[1] or float_to_string[0]:
            # but also a float --> flag to further check
            dtypes[column].append('check')
        else:
            # only non-floats
            dtypes[column].append('object')
    return dtypes


def get_dtypes_and_unks(md_pd, nan_value, sampleID_cols, length=25):
    """
    Get the native dtype and infer it too for each column of the passed metadata.
    Also get the the unknown factors that are ultimately considered "missing"
        metadata. Are considered as such: "short" string (<30 chars)
        containing none of ['/', '-', ':'] and no digit at all

    Parameters
    ----------
    md_pd : pd.DataFrame
        Metadata table in pandas (columns = variable, rows = observations).

    nan_value : str / np.nan
        Value to use for replacement for NaN / declared as such

    sampleID_cols : list
        Names of the columns containing the sample IDs

    length : int
        Length threshold for the factor - that could be a frequent
        unwanted factor (e.g. non, nan,...)

    Returns
    -------
    dtypes : dict
        keys    -> metadata columns
        values  -> 2-items lists
            [0] native dtype (from the pd.Series of columns)
            [1] inferred dtype ('object', 'float64' or 'check')

    potential_unks : dict
        keys    -> "NaN" metadata factor (e.g. "not provided")
        values  -> n-items lists
            [...] metadata columns where "NaN" factor is encountered

    nan_diversity: set
        all possible factors of all metadata variables that hit the
        regex used to identify potentially "NaN" / "missing" data

    """

    # get the regex allowing finding persistent NaN values
    regex_nan = make_regex_from_nan_value(nan_value)

    dtypes_inferred = {}
    potential_unks = {}
    nan_diversity = set()
    for column in md_pd.columns:
        native_dtype = str(md_pd[column].dtypes)  # get native dtype (may be "wrong")
        dtypes_inferred[column] = [native_dtype]
        float_to_string = [0, 0, 0, []]
        #  [0] - int  : contains a 'nan'
        #  [1] - int  : contains a 'float64'
        #  [2] - int  : contains a non-'float64'
        #  [3] - list : collect the unique non-'float64's
        if column in sampleID_cols:
            # force "#SampleID" or "sample_name" to not be a string
            dtypes_inferred[column].append('object')
            continue
        # look at content non "sample identifier" columns
        for V in md_pd[column].unique():
            v = str(V).lower()
            if re.search(regex_nan, v):
                if ':unspecified' not in v:
                    nan_diversity.add(V)
            if v == 'nan':
                float_to_string[0] += 1
            else:
                # check if column contains at least one float
                try:
                    float_V = float(V)
                    float_to_string[1] += 1
                except:
                    float_to_string[2] += 1
                    float_to_string[3].append(V)
                    if len(v) < length and '/' not in v and '-' not in v and not len(
                            [x for x in str(v) if x.isdigit()]):
                        potential_unks.setdefault(v, []).append(column)
        dtypes_inferred = set_column_dtypes(dtypes_inferred, column, float_to_string)
    return dtypes_inferred, potential_unks, nan_diversity


def get_certainly_NaNs(potential_unks, md_pd, freq=10):
    """
    Count the occurrences of the potential NaN (et al.)
    variables factors and return those that more than a
    given number of times.

    Parameters
    ----------
    potential_unks : dict
        all the factors that have the characetristics of a NaN.

    md_pd : pd.DataFrame
        original metadata table.

    freq : int
        minimun number of occurrences across the entire dataset
        to be considered a recurrent NaN and then to be staged
        for replacement.

    Returns
    -------
    certainly_NaNs : ps.Series
        final list of sufficiently occurrent factors that may be
        check by user and set on stage for replacement by commmon
        NaN-encoding value.
    """
    # encode the entire metadata as binary for each potential missing factor
    potential_unks_pd_L = []
    for col in md_pd.columns:
        potential_unks_pd_L.append(
            [1 if col in unk_samples else 0 for unk, unk_samples in sorted(potential_unks.items())])

    # make this binary data a dataframe
    potential_unks_pd = pd.DataFrame(potential_unks_pd_L,
                                     index=md_pd.columns.tolist(),
                                     columns=sorted(potential_unks.keys()))
    # nrows = potential_unks_pd.shape[0]
    sumCols = potential_unks_pd.sum(0)

    # Keep only the columns (i.e. the variables) that have at least 10 entries
    # all_unks_pd_common = all_unks_pd.loc[:, sumCols > (nrows*0.1)]
    certainly_NaNs = potential_unks_pd.loc[:, sumCols > freq].copy()
    return certainly_NaNs


def get_dtypes_final(dtypes_inferred, md_pd, nan_value, sampleID_cols):
    """
    Verify the dtypes of each column and apply
    it to some of the metadata columns.

    Parameters
    ----------
    dtypes_inferred : dict
        dtypes inferred from the metadata.
        e.g. {'sample_name': 'O', ...
              'age_years': 'Q'}

    md_pd : pd.DataFrame
        original metadata table.

    nan_value : str / np.nan
        Value to use for replacement for NaN / declared as such

    sampleID_cols : list
        Names of the columns containing the sample IDs

    Returns
    -------
    dtypes_inferred : dict
        inferred dtypes with the final dtype appended.

    dtypes_final : dict
        final dtypes verified for NaN columns that me current
        hybrids between 'nan' as "object" and float64.

    """
    dtypes_final = {}
    for col, checks in dtypes_inferred.items():
        if col in sampleID_cols:
            dtypes_inferred[col].append('object')
            dtypes_final[col] = 'O'

        # for the columns that might be numeric but
        # to which a string has been added during cleaning
        elif checks[-1] in ['check', 'object']:
            for v in md_pd[col].unique():
                # if str(v) == 'nan':
                # if the value is
                if str(v) == str(nan_value):
                    continue
                else:
                    try:
                        float_v = float(v)
                        continue
                    except:
                        dtypes_inferred[col].append('object')
                        dtypes_final[col] = 'O'
                        break
            else:
                dtypes_inferred[col].append('float64')
                dtypes_final[col] = 'Q'
        else:
            dtypes_inferred[col].append(checks[-1])
            dtypes_final[col] = 'Q'
    return dtypes_inferred, dtypes_final


def rectify_dtypes_in_md(md_pd, dtypes_final):
    """
    Set the dtypes of the columns based on the
    inference and checking steps.

    Parameters
    ----------
    md_pd : pd.DataFrame
        original metadata table

    dtypes_final : dict
        dtypes inferred from the metadata and verified
        e.g. {'sample_name': 'O',
              ...
              'age_years': 'Q'}

    Returns
    -------
    md_pd : pd.DataFrame
        final metadata table with updated dtypes
    """
    for col, dtype in dtypes_final.items():
        if col in md_pd.columns.tolist():
            if dtype == 'Q':
                md_pd[col] = md_pd[col].astype('float64')
            else:
                md_pd[col] = md_pd[col].astype('str')
        else:
            print('Warning: No dtype for "%s"' % col, '(set to "str")')
            md_pd[col] = md_pd[col].astype('str')
    return md_pd


def make_solve_dtypes_cleaning(md_pd, nan_value, sampleID_cols, show=None):
    """
    Run functions to understand and treat dtypes information.

    Parameters
    ----------
    md_pd : pd.DataFrame
        original metadata table.

    nan_value : str / np.nan
        Value to use for replacement for NaN / declared as such.

    sampleID_cols : list
        Names of the columns containing the sample IDs.

    Returns
    -------
    md_pd : pd.DataFrame
        dtypes-solved metadata table.

    """
    # starts by converting all the instances of the
    # replacement string to numpy NaN
    md_pd.replace(str(nan_value), np.nan, inplace=True)

    # get columns native and inferred dtypes
    dtypes_inferred, potential_unks, nan_diversity = get_dtypes_and_unks(md_pd, nan_value, sampleID_cols, 20)

    # get metadata factors that are short (length in the previous command) and frequent (freq here)
    certainly_NaNs = get_certainly_NaNs(potential_unks, md_pd, freq=10)
    if len(certainly_NaNs) and show:
        print('\nWarning: should not these '
              'be "%s" factors in the "nans" rule?:\n\t%s\n' % (
            nan_value, ', '.join(certainly_NaNs.columns.tolist())
        ))

    # get the final dtype by verifying the numeric column "without" the added nan_values
    dtypes_inferred, dtypes_final = get_dtypes_final(dtypes_inferred, md_pd, nan_value, sampleID_cols)

    # apply dtypes changes based on final dtypes
    md_pd = rectify_dtypes_in_md(md_pd, dtypes_final)

    md_pd.replace(str(nan_value), np.nan, inplace=True)
    return md_pd
