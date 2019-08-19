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
import numpy as np
import pytest
import glob

from pandas.util.testing import (
    assert_frame_equal,
    assert_series_equal
)

from metadata_cleaning._main_utils import (
    get_output_col_and_edits,
    make_replacement_cleaning,
    make_date_time_cleaning,
    make_forbidden_characters_cleaning,
    make_sample_id_cleaning
)


def get_output_col_and_edits():
    col_in = pd.Series(['A', 'B', 'b', 'C', 'D'])
    col_out = pd.Series(['A', np.nan, np.nan, np.nan, 'D'])
    # for replacements as dict
    assert (col_out, {'col': ['B', 'b', 'C']}) == get_output_col_and_edits(
        'col', col_in, np.nan, {'b': np.nan, 'c': np.nan}, {}
    )
    assert (col_out, {'col': ['B', 'b', 'C']}) == get_output_col_and_edits(
        'col', col_in, np.nan, ['b', 'c'], {}
    )


def test_make_replacement_cleaning():
    col_in = pd.Series(['A', 'B', 'b', 'C', 'D'])
    # return unchanged
    assert (col_in, {}) == make_replacement_cleaning(
        col_in, 'skip_col', ['skip_col'], {},
        np.nan, {}, 'nevermind')
    col_out_ref = pd.Series(['A', np.nan, np.nan, np.nan, 'D'])
    col_out_tst, nan_dec = make_replacement_cleaning(
        col_in, 'col', ['skip_col'], {'col': set()},
        np.nan, {'key': {'b': np.nan, 'c': np.nan}}, 'key')
    assert {'col': {np.nan}} == nan_dec
    assert_series_equal(col_out_ref, col_out_tst)

    col_out_ref = pd.Series(['A', np.nan, np.nan, np.nan, 'D'])
    col_out_tst, nan_dec = make_replacement_cleaning(
        col_in, 'col', ['skip_col'], {'col': set()},
        np.nan, {'b': np.nan, 'c': np.nan})
    print(nan_dec)
    assert {'col': {np.nan}} == nan_dec
    assert_series_equal(col_out_ref, col_out_tst)

    col_out_ref = pd.Series(['No', 'No', 'Yes'])
    for i in [[False, False, True], ['False', 'False', 'True']]:
        col_in = pd.Series(i)
        nan_dec_ref = {'col': {'Yes', 'No'}}
        col_out_tst, nan_dec_tst = make_replacement_cleaning(
            col_in, 'col', [], {'col': set()}, np.nan,
            {'key': {'False': 'No', 'True': 'Yes'}}, 'key')
    assert nan_dec_ref == nan_dec_tst
    assert_series_equal(col_out_ref, col_out_tst)

    col_out_ref = pd.Series(['No', 'No', 'Yes'])
    for i in [[False, False, True], ['False', 'False', 'True']]:
        col_in = pd.Series(i)
        nan_dec_ref = {'col': {'Yes', 'No'}}
        col_out_tst, nan_dec_tst = make_replacement_cleaning(
            col_in, 'col', [], {'col': set()}, np.nan,
            {'False': 'No', 'True': 'Yes'})
    assert nan_dec_ref == nan_dec_tst
    assert_series_equal(col_out_ref, col_out_tst)

    for i, j in [([1, 1, 0], 'int'),
                 ([1., 1., 0.], 'float64'),
                 ([1., 1., np.nan], 'float64')]:
        col_in = pd.Series(i, dtype=j)
        nan_dec_ref = {'col': set()}
        col_out_tst, nan_dec_tst = make_replacement_cleaning(
            col_in, 'col', [],  {'col': set()}, 'nevermind',
            {'key': {'what': 'ever'}}, 'key'
        )
    assert nan_dec_ref == nan_dec_tst
    assert_series_equal(col_in, col_out_tst)



def xtest_make_sample_id_cleaning():
    make_sample_id_cleaning(md, sample_id_cols, sample_rules, show=False)
    """
    Check and correct the sample identifiers.
    Print warnings if something wrong.

    Parameters
    ----------
    md : pd.DataFrame
        Dataframe with sample_id to clean.

    sample_id_cols : list
        Names of the columns containing the sample IDs

    sample_rules : dict
        All rules in the keys "sample_id"

    show : bool
        Verbosity

    Returns
    -------
    md : pd.DataFrame
        Dataframe with cleaned sample_ids.
    """
    for sample_col in sample_id_cols:
        if sample_col not in md.columns:
            continue
        input_col = md[sample_col].astype('str')
        if 'check_sample_id_unique' in sample_rules and sample_rules['check_sample_id_unique']:
            if input_col.unique().size != input_col.size:
                if show:
                    print('Warning: duplicate sample names in "%s"' % sample_col)
                    print(' (Duplication number: %s)\n' % sum(input_col.value_counts() > 1))
                if 'check_sample_id_force' in sample_rules and sample_rules['check_sample_id_force']:
                    replicated = dict(input_col.value_counts())
                    new_ids = []
                    new_ids_d = {}
                    for i in input_col:
                        if replicated[i] > 1:
                            if i not in new_ids_d:
                                new_ids_d[i] = 1
                            new_ids.append('%s.%s' % (i, new_ids_d[i]))
                            new_ids_d[i] += 1
                        else:
                            new_ids.append(i)
                    input_col = pd.Series(new_ids)
        md[sample_col] = input_col
    return md


def xtest_make_date_time_cleaning():
    md_in = pd.DataFrame({})
    md_pd = make_date_time_cleaning(md, rules)
    assert_frame_equal(md_in, md_out)


def xtest_make_forbidden_characters_cleaning():
    md_in = pd.DataFrame({})
    forbidden_rules = {}
    md_out = make_forbidden_characters_cleaning(md_in,
                                                ['sample_name'],
                                                forbidden_rules)
    assert_frame_equal(md_in, md_out)
