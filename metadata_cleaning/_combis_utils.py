#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import re
import pandas as pd


def get_combinations_rule_details(combination, conditions):
    """
    Get the metadata columns that match the given combination.

    Parameters
    ----------
    combination : tuple
        Columns to check for decision,
        e.g. ('age', 'alcohol_consumption')

    conditions : tuple
        e.g. ('range(0,4)', True)
        e.g. ('range(0,4)', 'range(20,None)')
        e.g. ('alcohol', 'alcohol_consumption')

    Returns
    -------
    cur_rules : dict
        key    -> item in combination
        value  -> tuple of decision for the actual cleaning
        e.g. {'age': ('in', 0.0, 4.0),
              'alcohol_consumption': ('is', None, None)}

    """
    cur_rules = {}
    for cdx, condition in enumerate(conditions):
        in_out = 'in'
        column = combination[cdx]
        if condition in [True, False]:
            cur_rules[column] = ('is', condition, None)
        elif condition.startswith('range('):
            cur_range_xy = [float(x) if x != 'None' else None for x in re.split('\(|\)', condition)[1].split(',')]
            if cur_range_xy[0] == None:
                cur_rules[column] = ('<', cur_range_xy[1], None)
            elif cur_range_xy[1] == None:
                cur_rules[column] = ('>', cur_range_xy[0], None)
            else:
                cur_rules[column] = (in_out, cur_range_xy[0], cur_range_xy[1])
    return cur_rules


def get_columns_from_combination(md, combination):
    """
    Get the metadata columns that match the given combination.

    Parameters
    ----------
    md : pd.DataFrame
        Metadata with columns to clean.

    combination : tuple
        Columns to check for decision,
        e.g. ('age', 'alcohol_consumption')

    Returns
    -------
    columns_match : dict
        key    -> item in combination
        value  -> list of columns that match
    """

    columns_match = {}
    for combi in combination:
        for col in md.columns:
            if combi.lower() in col.lower():
                columns_match.setdefault(combi, []).append(col)

    return columns_match


def apply_combination_rule_check(row, cur_rules, columns_match, nan_decisions):
    """
    Check if the rule that is depending on >1 column applies.

    Parameters
    ----------
    row : pd.Series
        Row of the dataframe reduced to the usefule columns
        to check if the rule applies.

    cur_rules : dict
        Multi-columns rule that has been prepared in
        get_combinations_rule_details()
        e.g. {'age': ('<', 18, None),
              'alcohol_consumption': ('is', 'Yes', None)}
        (you should not drink if you are less than 18)

    columns_match : dict
        Columns of the original metadata that correspond
        to the current rule.

    nan_decisions : dict
        Dict to update with the encountered edits.

    Returns
    -------
    md : pd.DataFrame
        Metadata with cleaned columns.
    """
    rule_applies = 0
    # for each column used for the combination rule (col_rule)
    # and each rule that applies to this paticular column (cur_rule)
    for col_rule, cur_rule in cur_rules.items():
        # for each source metadata column
        for md_col in columns_match[col_rule]:
            # first go into the "type of comparison" condition
            # ... then into the actual comparison
            if cur_rule[0] == 'is':
                if cur_rule[1] and str(row[md_col]) in ['True', 'Yes', '1']:
                    break
                if not cur_rule[1] and str(row[md_col]) in ['False', 'No', '0']:
                    break
            elif cur_rule[0] == 'in':
                if row[md_col] in nan_decisions[md_col] or not str(row[md_col]).isdigit():
                    continue
                if row[md_col] >= cur_rule[1] and row[md_col] <= cur_rule[2]:
                    break
            elif cur_rule[0] == '>':
                if row[md_col] in nan_decisions[md_col] or not str(row[md_col]).isdigit():
                    continue
                if row[md_col] >= cur_rule[1]:
                    break
            elif cur_rule[0] == '<':
                if row[md_col] in nan_decisions[md_col] or not str(row[md_col]).isdigit():
                    continue
                if row[md_col] <= cur_rule[2]:
                    break
        else:
            # if the condition is never met then the
            # below "rule_applies" is not incremented
            continue
        rule_applies += 1
    # return if number of met rules equals the number of rules
    if rule_applies == len(cur_rules.keys()):
        return True
    return False


def make_combinations_cleaning(md, combination, conditions_decision, nan_decisions, nan_value):
    """
    Change column(s) based on the combination
    of factors in multiple columns.

    Parameters
    ----------
    md : pd.DataFrame
        Metadata with columns to clean.

    combination : tuple
        Columns to check for decision,
        e.g. ('age', 'alcohol_consumption')

    conditions_decision : list
        [0] tuple  : Index-wise values of the combinations items
        [1] dict   : Edits to apply if conditions satisfied.
        e.g. [('range(0,4)', True), {'alcohol_consumption': 'Missing'}]

    nan_value : str
        Value to use for replacement for NaN / declared as such.

    Returns
    -------
    md : pd.DataFrame
        Metadata with cleaned columns.
    """
    show = 0
    columns_match = get_columns_from_combination(md, combination)
    if len(columns_match) == len(combination):

        conditions, decision = conditions_decision
        # conditions -->  ('range(0,4)', True)
        # decision   -->  {'alcohol_consumption': 'Missing'}
        if isinstance(decision, dict):
            decision_key, decision_value = [(x, y) for x, y in decision.items()][0]
        else:
            decision_key, decision_value = decision, nan_value

        # get the column name and dataframe's column that may be edited
        decision_col = list(set([x for x in md.columns if decision_key.lower() in x.lower()]))[0]
        output_copy = md[decision_col].tolist()

        # parse the rules and prepare an encoding for the actual row-wise filterinf
        cur_rules = get_combinations_rule_details(combination, conditions)

        # get all the unique metadata columns that will serve for the rule
        all_columns_match = list(set([y for columns in columns_match.values() for y in columns]))

        for rdx, (r, row) in enumerate(md[all_columns_match].iterrows()):
            # check if the combinations of the columns contents match the rule from the yaml file
            rule_applies = apply_combination_rule_check(row, cur_rules,
                                                        columns_match,
                                                        nan_decisions)

            # if yes -> edit the current entry of the current decision column
            if rule_applies:
                output_copy[rdx] = decision_value

        # put the edited column as a replacement in the dataframe
        md[decision_col] = output_copy

    return md