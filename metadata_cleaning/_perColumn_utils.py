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

from metadata_cleaning._main_utils import make_replacement_cleaning


def missing_decision(cur_range_xy, entry_float):
    """
    Get the bool to tell whether the conditons
    are met for cleaning.

    Parameters
    ----------
    cur_range_xy : tuple
        Min and max values of a range.
        Could be just the min: e.g. (0, None)
              or just the max: e.g. (None, 1)

    entry_float : float
        Value to check in range.

    Returns
    -------
    bool
        Whether the value is not in the range.
    """
    # check whether the current value is oustide the given range
    if cur_range_xy[0] == None and entry_float > cur_range_xy[1]:
        return True
    elif cur_range_xy[1] == None and entry_float < cur_range_xy[0]:
        return True
    elif entry_float > cur_range_xy[1] or entry_float < cur_range_xy[0]:
        return True
    else:
        return False


def make_per_column_cleaning(md, name_col, ranges_or_reps, nan_value, nan_decisions):
    """
    Exectute the edit on the passed column based on either
        (i)  a dictionary of replacements
            (by running make_replacement_cleaning())
        (ii) checking the values inside/outside a given range of values

    Parameters
    ----------
    md : pd.DataFrame
        Metadata with columns to clean.

    name_col : str
        Name of the passed column.

    ranges_or_reps : dict
        All rules for the current columns placeholder,
            e.g. {'age': ['range(0,120)'], ...}
            (could apply to age, age_cat, age_corrected)

    nan_value : str
        Value to use for replacement for NaN / declared as such

    nan_decisions : dict
        Dict to update with the encountered edits.

    Returns
    -------
    md : pd.DataFrame
        Metadata with cleaned columns.
    """
    # get the columns that match the given column name
    ## => TO BE SET TO PERFECT MATCH --> discussion
    cols_to_edit = [x for x in md.columns if name_col.lower() in x.lower()]
    for col_to_edit in cols_to_edit:
        output_copy = md[col_to_edit].copy()
        #  for eahc actual rule to apply on the column content
        for range_or_rep in ranges_or_reps:

            # could be simple factors replacement rule
            if isinstance(range_or_rep, dict):
                # always collect an edit value in the column (nan_decisions)
                output_copy, nan_decisions = make_replacement_cleaning(output_copy, name_col,
                                                                       nan_decisions, nan_value,
                                                                       range_or_rep, None)
            # could be more complicated range check rule
            elif range_or_rep.startswith('range('):
                new_col = []
                # get the range
                cur_range_xy = [float(x) if x else None for x in
                                re.split('\(|\)', range_or_rep)[1].split(',')]
                # for each entry that can be compared to a numeric range
                for entry in output_copy:
                    try:
                        entry_float = float(entry)
                        # check if in/out range
                        edit_or_not = missing_decision(cur_range_xy, entry_float)
                        if edit_or_not:
                            new_col.append(nan_value)
                            # always collect an edit value in the column (nan_decisions)
                            nan_decisions[col_to_edit].add(nan_value)
                        else:
                            new_col.append(entry)
                    except:
                        new_col.append(entry)
                # get the edited column as a pandas Series
                output_copy = pd.Series(new_col)
        # put back the edited column
        md[col_to_edit] = output_copy
    return md, nan_decisions