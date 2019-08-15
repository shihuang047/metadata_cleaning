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

import os

from _df_utils import (
    get_nan_value_and_sampleID_cols,
    read_input_metadata
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



def metadata_clean(yaml_rules_fp=None, do_dummy=True):
    """
    Main command running the tool.
    Needs setup using @click for the inputs...

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

    if not yaml_rules_fp:
        yaml_rules_fp = os.path.join(
            "tests", "cleaning_rules.yaml"
        )
    # Read the rules from the yaml fule
    rules = get_yaml_rules(yaml_rules_fp, show_raw=False)

    # but the final user version will be written too at the end if different from np.nan
    nan_value_user, sampleID_cols = get_nan_value_and_sampleID_cols(rules)

    # default NaN value will be used in the per_column rules
    nan_value = 'nan'

    if do_dummy:
        md_pd = build_dummy_dataset_for_lauriane_rules_testing()
    else:
        md_fp = os.path.join(
            "tests", "dummy.tsv"
            # "tests", "internal", "2019.07.17_danone_md_n3844_selection_draft.xlsx"
            # "tests", "internal", "meta_16S_3577s.tsv"
        )
        if 'xls' in os.path.splitext(md_fp)[1]:
            md_pd = read_input_metadata(md_fp, True, sampleID_cols)
        else:
            md_pd = read_input_metadata(md_fp, False, sampleID_cols)

    nan_decisions = {}
    for name_col in md_pd.columns:
        nan_decisions[name_col] = set()
        nan_decisions[name_col.lower()] = set()
        input_col = md_pd[name_col]
        # clean NaNs or Yes/No
        for rule in ['nans', 'booleans']:
            if rule in rules:
                output_col, nan_decisions = make_replacement_cleaning(input_col, name_col,
                                                                      nan_decisions, nan_value,
                                                                      rules, rule)
                md_pd[name_col] = output_col

    # correct sample ID
    if 'sample_id' in rules:
        md_pd = make_sampleID_cleaning(md_pd, rules['sample_id'])

    # correct time
    if 'time_format' in rules:
        md_pd = make_date_time_cleaning(md_pd, rules)

    # clean per_column
    if 'per_column' in rules:
        for name_col, ranges_or_reps in rules['per_column'].items():
            md_pd, nan_decisions = make_per_column_cleaning(md_pd, name_col,
                                                            ranges_or_reps,
                                                            nan_value,
                                                            nan_decisions)

    # clean combinations
    if 'combinations' in rules:
        for combination, conditions_decision in rules['combinations'].items():
            md_pd = make_combinations_cleaning(md_pd, combination,
                                                       conditions_decision, nan_decisions)

    # clean del_columns
    if 'del_columns' in rules:
        del_columns = [y.lower() for y in rules['del_columns']]
        md_pd = md_pd[[x for x in md_pd.columns if x.lower() not in del_columns]]

    # clean forbidden_characters
    if 'forbidden_characters' in rules:
        md_pd = make_forbidden_characters_cleaning(md_pd, rules['forbidden_characters'])

    # solve dtypes
    if 'solve_dtypes' in rules and rules['solve_dtypes']:
        md_pd = make_solve_dtypes_cleaning(md_pd, nan_value, sampleID_cols)

    print(md_pd)

if __name__ == "__main__":
    metadata_clean()

