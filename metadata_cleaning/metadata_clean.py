#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Clean is a metadata curation tool that applies rules form the user and
# passed as a yaml file.
#
# It will as a standalone tool and part of the metadata QIIME 2 plugin.
#
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os, sys

from metadata_cleaning._df_utils import (
    write_outputs
)

from metadata_cleaning._main_utils import (
    make_replacement_cleaning,
    make_sample_id_cleaning,
    make_date_time_cleaning,
    make_forbidden_characters_cleaning,
)

from metadata_cleaning._dtypes_utils import (
    make_solve_dtypes_cleaning
)

from metadata_cleaning._perColumn_utils import (
    make_per_column_cleaning
)

from metadata_cleaning._combis_utils import (
    make_combinations_cleaning
)


def metadata_clean(
        rules,
        no_booleans,
        no_combinations,
        no_del_columns,
        no_forbidden_characters,
        no_nans,
        no_per_column,
        no_solve_dtypes,
        no_time_format,
        nan_value,
        nan_value_user,
        sample_id_cols,
        metadata_pd,
        metadata_fp,
        output_fp=None,
        show=True
):
    """
    Main command running the cleaning.

    Parameters
    ----------
    rules : dict
        All rules in the following keys:
            ['booleans', 'combinations', 'nans', 'del_columns', 'forbidden_characters', 'na_value',
             'solve_dtypes', 'per_column', 'sample_id', 'time_format'] (or more to come...)

    no_booleans : bool
        Boolean to not replace the True/False ("booleans" rules).

    no_combinations : bool
        Boolean to not check the conditions of combinations ("combinations" rules).

    no_del_columns : bool
        Boolean to not delete the given columns ("del_columns" rule).

    no_forbidden_characters : bool
        Boolean to not replace the given forbidden characters ("forbidden_characters" rules).

    no_nans : bool
        Boolean to not clean the values of "nans" ("nans" rules).

    no_per_column : bool
        Boolean to not apply the per-column rules ("per_column" rules).

    no_solve_dtypes : bool
        Boolean to not check the dtypes of the columns ("solve_dtypes" rule).

    no_time_format : bool
        Boolean to not clean the formatting of the time/date ("time_format" rule).

    nan_value : str
        Value to use for replacement for NaN / declared as such.

    nan_value_user : str
        Value to use for replacement for NaN declared by user.

    sample_id_cols : list
        Names of the columns containing the sample IDs

    metadata_pd : pd.DataFrame
        Metadata table.

    metadata_fp : str
        Input file path

    output_fp : str
        Output file path

    show : bool
        Activate verbose.

    Returns
    -------
    metadata_pd : pd.DataFrame
        final metadata table with updated dtypes
    """

    nan_decisions = {}
    for name_col in metadata_pd.columns:
        nan_decisions[name_col] = set()
        nan_decisions[name_col.lower()] = set()
        input_col = metadata_pd[name_col]
        # clean NaNs or Yes/No
        for rule in ['nans', 'booleans']:
            if rule in rules:
                if rule == 'booleans' and no_booleans:
                    continue
                if rule == 'nans' and no_nans:
                    continue
                output_col, nan_decisions = make_replacement_cleaning(
                    input_col,
                    name_col,
                    sample_id_cols,
                    nan_decisions,
                    nan_value,
                    rules,
                    rule
                )
                metadata_pd[name_col] = output_col

    # correct sample ID
    if 'sample_id' not in rules:
        if show:
            print('"sample_id" cleaning...')
        print('Error: "sample_id" in a mandatory rule')
        return 1

    metadata_pd = make_sample_id_cleaning(
        metadata_pd,
        sample_id_cols,
        rules['sample_id'],
        show
    )

    # correct time
    if 'time_format' in rules and not no_time_format:
        if show:
            print('"time_format" cleaning...')
        metadata_pd = make_date_time_cleaning(metadata_pd, rules)

    # clean per_column
    if 'per_column' in rules and not no_per_column:
        if show:
            print('"per_column" cleaning...')
        for name_col, ranges_or_reps in rules['per_column'].items():
            metadata_pd, nan_decisions = make_per_column_cleaning(
                metadata_pd,
                name_col,
                sample_id_cols,
                ranges_or_reps,
                nan_value,
                nan_decisions
            )

    # clean combinations
    if 'combinations' in rules and not no_combinations:
        if show:
            print('"combinations" cleaning...')
        for combination, conditions_decision in rules['combinations'].items():
            metadata_pd = make_combinations_cleaning(
                metadata_pd,
                combination,
                conditions_decision,
                nan_decisions,
                nan_value
            )

    # clean del_columns
    if 'del_columns' in rules and not no_del_columns:
        if show:
            print('"del_columns" cleaning...')
        del_columns = [y.lower() for y in rules['del_columns']]
        metadata_pd = metadata_pd[[x for x in metadata_pd.columns if x.lower() not in del_columns]]

    # clean forbidden_characters
    if 'forbidden_characters' in rules and not no_forbidden_characters:
        if show:
            print('"forbidden_characters" cleaning...')
        metadata_pd = make_forbidden_characters_cleaning(
            metadata_pd, sample_id_cols, rules['forbidden_characters']
        )

    # solve dtypes
    if 'solve_dtypes' in rules and rules['solve_dtypes'] and not no_solve_dtypes:
        if show:
            print('"solve_dtypes" cleaning...')
        metadata_pd = make_solve_dtypes_cleaning(
            metadata_pd,
            nan_value,
            sample_id_cols,
            show
        )

    # write outputs
    exit_code = write_outputs(
        metadata_pd,
        metadata_fp,
        output_fp,
        nan_value,
        nan_value_user
    )

    if exit_code != 0:
        raise ValueError("No metadata cleaning output.")



