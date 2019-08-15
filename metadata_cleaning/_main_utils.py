#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd


def make_replacement_cleaning(input_col, name_col, nan_decisions, rules, key=None):
    """
    Treat column by replacement.

    Parameters
    ----------
    input_col : pd.Series
        Column to clean.

    name_col : str
        Name of the passed column.

    nan_decisions : dict
        Dict to update with the encountered edits.

    rules : dict
        All rules in the following keys:
            ['booleans', 'combinations', 'nans',
            'per_column', 'sample_id', 'time_format']
        Or a replacement dict

    key : str
        Rule key, e.g. ['booleans', 'nans']
        Could be None if a replacement dict is directly
            passed in the rules dict

    Returns
    -------
    input_col : pd.Series
        Cleaned column.
    """

    def get_ouput_col_and_edits(name_col, input_col, replacement, nan_decisions):
        """Get the replaced column and update the decisions
        dict with the replacement values for the current column"""
        output_col = input_col.astype('str').replace(replacement)
        edits = [edit for edit in output_col if edit in list(replacement.values())]
        # always collect an edit value in the column (nan_decisions)
        nan_decisions[name_col].update(edits)
        return output_col, nan_decisions

    if 'sample_id' in rules and name_col in rules['sample_id']['sample_id_cols']:
        return input_col, nan_decisions

    input_col_dtype = str(input_col.dtype)
    if input_col_dtype == 'bool' and key == 'booleans':
        return get_ouput_col_and_edits(name_col, input_col, rules[key], nan_decisions)
    elif input_col_dtype != 'object':
        return input_col, nan_decisions
    else:
        if key:
            return get_ouput_col_and_edits(name_col, input_col, rules[key], nan_decisions)
        else:
            return get_ouput_col_and_edits(name_col, input_col, rules, nan_decisions)
    return input_col


def make_sampleID_cleaning(md, sample_rules):
    """
    Check and correct the sample identifiers.
    Print warnings if something wrong.

    Parameters
    ----------
    md : pd.DataFrame
        Dataframe with sample_id to clean.

    sample_rules : dict
        All rules in the keys "sample_id"

    Returns
    -------
    md : pd.DataFrame
        Dataframe with cleaned sample_ids.
    """
    for sample_col in sample_rules['sample_id_cols']:
        if not sample_col in md:
            continue
        input_col = md[sample_col].astype('str')
        if sample_rules['check_sample_id_unique']:
            if input_col.unique().size != input_col.size:
                print('Warning: duplicate sample names in "%s"' % sample_col)
                print(' (Duplication number: %s)' % sum(input_col.value_counts( ) >1))
                if sample_rules['check_sample_id_force']:
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


def make_date_time_cleaning(md, rules):
    """
    Edit the date/time information.

    Parameters
    ----------
    md : pd.DataFrame
        Dataframe with time columns to clean.

    rules : dict
        All rules in the following keys:
            ['booleans', 'combinations', 'nans',
            'per_column', 'sample_id', 'time_format']

    Returns
    -------
    md : pd.DataFrame
        Dataframe with cleaned time columns.
    """
    # for each time colums passed in the rules file
    for name_col in rules['time_format']['columns']:
        if name_col in md:
            input_col = md[name_col]
            # format using pandas function .to_datetime and eventually parse this formatting
            if name_col.lower() == 'collection_date':
                input_col_dt = pd.to_datetime(input_col, infer_datetime_format=True).astype('str')
                clean_time = ['/'.join(x.split('-')[::-1]) for x in input_col_dt]
            elif name_col.lower() == 'collection_time':
                clean_time = pd.to_datetime(input_col, format='%H:%M:%S').dt.time.astype('str')
            elif name_col.lower() == 'collection_timestamp':
                input_col_dt = pd.to_datetime(input_col, infer_datetime_format=True).astype('str')
                clean_time = ['%s %s' % ('/'.join(x.split()[0].split('-')[::-1]), x.split()[1]) for x in input_col_dt]
            md[name_col] = clean_time
    return md
