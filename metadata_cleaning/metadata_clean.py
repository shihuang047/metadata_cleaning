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

from _df_utils import (
    get_nan_value_and_sampleID_cols,
    read_input_metadata,
    write_outputs
)

from _main_utils import (
    make_replacement_cleaning,
    make_sampleID_cleaning,
    make_date_time_cleaning,
    make_forbidden_characters_cleaning,
)

from _dtypes_utils import (
    make_solve_dtypes_cleaning
)

from _perColumn_utils import (
    make_per_column_cleaning
)

from _yaml_utils import (
    get_yaml_rules
)

from _combis_utils import (
    make_combinations_cleaning
)

from tests._utils_test import (
    build_dummy_dataset_for_lauriane_rules_testing
)

#
# TO BE ADDED: INFER THE RESULTING DTYPES
# EVEN AFTER ADDITION OF E.G. "Missing" IN
# A NUMERIC COLUMN
#
#from clean._dtypes_utils import (
#    get_dtypes_and_unks,
#    get_certainly_NaNs,
#    get_dtypes_final,
#    rectify_dtypes_in_md
#)


def parse_yaml_file(yaml_rules_fp=None, show=False):
    """
    Main command running the tool.
    Needs setup using @click for the inputs.

    Parameters
    ----------
    yaml_rules_fp : str
        File path for the rules in yaml format.

    show : bool
        Activate verbose.

    Returns
    -------
    rules : dict
        All rules in the following keys:
            ['booleans', 'combinations', 'nans', 'del_columns', 'forbidden_characters', 'na_value',
             'solve_dtypes', 'per_column', 'sample_id', 'time_format'] (or more to come...)

    nan_value : str
        Value to use for replacement for NaN / declared as such.

    nan_value_user : str
        Value to use for replacement for NaN declared by user.

    sampleID_cols : list
        Names of the columns containing the sample IDs
    """
    if not yaml_rules_fp:
        yaml_rules_fp = os.path.join(
            "tests", "cleaning_rules.yaml"
        )
    # Read the rules from the yaml fule
    rules = get_yaml_rules(yaml_rules_fp, show_rules)
    # but the final user version will be written too at the end if different from np.nan
    nan_value_user, sampleID_cols = get_nan_value_and_sampleID_cols(rules)
    # default NaN value will be used in the per_column rules
    nan_value = 'nan'
    return rules, nan_value, nan_value_user, sampleID_cols


def parse_metadata_files(metadata_fp=None, do_dummy=False):
    """
    Main command running the tool.
    Needs setup using @click for the inputs.

    Parameters
    ----------
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
        metadata_pd = build_dummy_dataset_for_lauriane_rules_testing()
    else:
        if not metadata_fp:
            metadata_fp = os.path.join(
                "tests", "dummy.tsv"
                # "tests", "internal", "2019.07.17_danone_md_n3844_selection_draft.xlsx"
                # "tests", "internal", "meta_16S_3577s.tsv"
            )
        else:
            metadata_pd = metadata_fp
        if 'xls' in os.path.splitext(metadata_fp)[1]:
            metadata_pd = read_input_metadata(metadata_fp, True, sampleID_cols)
        else:
            metadata_pd = read_input_metadata(metadata_fp, False, sampleID_cols)
    return metadata_pd


def metadata_clean(
        rules,
        nan_value,
        nan_value_user,
        sampleID_cols,
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

    nan_value : str
        Value to use for replacement for NaN / declared as such.

    nan_value_user : str
        Value to use for replacement for NaN declared by user.

    sampleID_cols : list
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
                output_col, nan_decisions = make_replacement_cleaning(input_col, name_col,
                                                                      nan_decisions,
                                                                      nan_value,
                                                                      rules, rule)
                metadata_pd[name_col] = output_col

    # correct sample ID
    if 'sample_id' not in rules:
        print('Error: "sample_id" in a mandatory rule')
        sys.exit(1)
    metadata_pd = make_sampleID_cleaning(metadata_pd, rules['sample_id'], show)

    # correct time
    if 'time_format' in rules:
        metadata_pd = make_date_time_cleaning(metadata_pd, rules)

    # clean per_column
    if 'per_column' in rules:
        for name_col, ranges_or_reps in rules['per_column'].items():
            metadata_pd, nan_decisions = make_per_column_cleaning(metadata_pd, name_col,
                                                            ranges_or_reps,
                                                            nan_value,
                                                            nan_decisions)

    # clean combinations
    if 'combinations' in rules:
        for combination, conditions_decision in rules['combinations'].items():
            metadata_pd = make_combinations_cleaning(
                metadata_pd,
                combination,
                conditions_decision,
                nan_decisions,
                nan_value
            )

    # clean del_columns
    if 'del_columns' in rules:
        del_columns = [y.lower() for y in rules['del_columns']]
        metadata_pd = metadata_pd[[x for x in metadata_pd.columns if x.lower() not in del_columns]]

    # clean forbidden_characters
    if 'forbidden_characters' in rules:
        metadata_pd = make_forbidden_characters_cleaning(
            metadata_pd,
            rules['forbidden_characters']
        )

    # solve dtypes
    if 'solve_dtypes' in rules and rules['solve_dtypes']:
        metadata_pd = make_solve_dtypes_cleaning(
            metadata_pd,
            nan_value,
            sampleID_cols,
            show
        )

    # write outputs
    clean_metadata_fps = write_outputs(
        metadata_pd,
        metadata_fp,
        output_fp,
        nan_value,
        nan_value_user
    )

    return clean_metadata_fps


