#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd


def get_output_col_and_edits(name_col, input_col, nan_value, replacement, nan_decisions):
    """
    Get the replaced column and update the decisions
    dict with the replacement values for the current column.

    Parameters
    ----------
    name_col : str
        Name of the passed column.

    input_col : pd.Series
        Column to clean.

    nan_value : str
        Value to use for replacement for NaN / declared as such

    nan_decisions : dict
        Dict to update with the encountered edits.

    replacement : dict or list
        Dict of replacements to execute.
        Or list of factor to replace by np.nan

    nan_decisions : dict
        Dict to update with the encountered edits.

    Returns
    -------
    output_col : pd.Series
        Cleaned column.

    nan_decisions : dict
        Updated dict of the encountered edits.
    """
    if isinstance(replacement, dict):
        replacement_aug = dict(replacement)
        for k, v in replacement.items():
            replacement_aug[k.lower()] = v
            replacement_aug[k.upper()] = v
    else:
        replacement_aug = dict((x, nan_value) for x in replacement)
    output_col = input_col.astype('str').replace(replacement_aug)
    edits = [edit for edit in output_col if edit in list(replacement_aug.values())]
    # always collect an edit value in the column (nan_decisions)
    nan_decisions[name_col].update(edits)
    return output_col, nan_decisions


def make_replacement_cleaning(input_col, name_col, sample_id_cols,
                              nan_decisions, nan_value, rules, key=None):
    """
    Treat column by replacement.

    Parameters
    ----------
    input_col : pd.Series
        Column to clean.

    name_col : str
        Name of the passed column.

    sample_id_cols : list
        Names of the columns containing the sample IDs

    nan_value : str
        Value to use for replacement for NaN / declared as such

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

    # if 'sample_id' in rules and name_col in rules['sample_id']['sample_id_cols']:
    if name_col in sample_id_cols:
        return input_col, nan_decisions

    input_col_dtype = str(input_col.dtype)
    if input_col_dtype == 'bool' and key == 'booleans':
        return get_output_col_and_edits(name_col, input_col, nan_value, rules[key], nan_decisions)
    elif input_col_dtype != 'object':
        return input_col, nan_decisions
    else:
        if key:
            return get_output_col_and_edits(name_col, input_col, nan_value, rules[key], nan_decisions)
        else:
            return get_output_col_and_edits(name_col, input_col, nan_value, rules, nan_decisions)


def make_sample_id_cleaning(md, sample_id_cols, sample_rules, show=False):
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


def make_date_time_cleaning(md, rules):
    """
    Edit the date/time information.

    Parameters
    ----------
    md : pd.DataFrame
        DataFrame with time columns to clean.

    rules : dict
        All rules in the following keys:
            ['booleans', 'combinations', 'nans',
            'per_column', 'sample_id', 'time_format']

    Returns
    -------
    md : pd.DataFrame
        Data frame with cleaned time columns.
    """

    # for each time column passed in the rules file
    if 'columns' in rules['time_format']:
        for name_col in rules['time_format']['columns']:
            if name_col in md:
                input_col = md[name_col].copy()
                # format using pandas function .to_datetime and eventually parse this formatting
                if name_col.lower() == 'collection_date':
                    input_col_dt = pd.to_datetime(input_col, infer_datetime_format=True).astype('str').copy()
                    clean_time = ['/'.join(x.split('-')[::-1]) for x in input_col_dt]
                elif name_col.lower() == 'collection_time':
                    clean_time = pd.to_datetime(input_col, format='%H:%M:%S').dt.time.astype('str').copy()
                elif name_col.lower() == 'collection_timestamp':
                    input_col_dt = pd.to_datetime(input_col, infer_datetime_format=True).astype('str').copy()
                    clean_time = ['%s %s' % ('/'.join(x.split()[0].split('-')[::-1]), x.split()[1]) for x in input_col_dt]
                else:
                    continue
                md[name_col] = clean_time
    return md


def make_forbidden_characters_cleaning(md_pd, sample_id_cols, forbidden_rules):
    """
    Replace the characters in columns that contain characters.

    Parameters
    ----------
    md_pd : pd.DataFrame
        Original metadata table.

    sample_id_cols : list
        Names of the columns containing the sample IDs

    forbidden_rules : dict
        Replacement values.
        keys  -> e.g. '('
        value -> e.g. '_'

    Returns
    -------
    md_pd : pd.DataFrame
        Clean metadata table.

    """
    if not isinstance(forbidden_rules, dict):
        print('Warning: object in "forbidden_characters" must be a dict')
        print(' -> no forbidden_characters cleaning...\n')
        return md_pd

    md_dp_copy = md_pd.copy()
    for col in md_pd.columns:
        if col in sample_id_cols:
            continue
        if str(md_pd[col].dtype) == 'object':
            cur_col = md_dp_copy[col]
            for k,v in forbidden_rules.items():
                cur_col = cur_col.replace(k,v)
            md_dp_copy[col] = cur_col
    return md_dp_copy


