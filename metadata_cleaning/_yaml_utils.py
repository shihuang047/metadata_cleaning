#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
import os
import yaml
import numpy as np


def validate_fp(yaml_rules_fp):
    """
    Does some basic validation on the passed file.
    """
    if not os.path.isfile(yaml_rules_fp):
        raise FileNotFoundError(
            "Yaml rules file '%s' do not exist." % yaml_rules_fp
        )


def validate_rules(yaml_rules_fp, rules):
    """
    Does some basic validation on the yaml rules.
    """
    if not isinstance(rules, dict):
        raise ValueError(
            "Rules from %s are not properly read" % yaml_rules_fp
        )
    if 'sample_id' not in rules:
        raise ValueError(
            "Mandatory 'sample_id' rule missing in '%s'" % yaml_rules_fp
        )
    elif 'sample_id_cols' not in rules['sample_id']:
        raise ValueError(
            "Mandatory 'sample_id_cols' rule missing in '%s'" % yaml_rules_fp
        )
    accepted_rules = {
        'booleans',
        'combinations',
        'del_columns',
        'forbidden_characters',
        'na_value',
        'nans',
        'per_column',
        'sample_id',
        'solve_dtypes',
        'time_format'
    }
    intersect_rules = set(list(rules.keys())) ^ accepted_rules
    if len(intersect_rules):
        print(
            "Warning: unrecognized rules (will not be treated):\n"
            "- %s" % '\n-'.join(list(intersect_rules))
        )


def get_nan_value_and_sample_id_cols(rules):
    """
    Get the default "NaN" values that will be used
    in the per_column rules.

    Parameters
    ----------
    rules : dict
        All rules in the following keys:
            ['booleans', 'combinations', 'nans',
            'per_column', 'sample_id', 'time_format']

    Returns
    -------
    nan_value : str / np.nan
        Value to use for replacement for NaN / declared as such
    """
    if 'na_value' in rules:
        nan_value = rules['na_value']
    else:
        nan_value = np.nan

    if 'sample_id' in rules:
        if 'sample_id_cols' in rules['sample_id']:
            return nan_value, rules['sample_id']['sample_id_cols']
    return nan_value, None


def get_yaml_rules(yaml_rules_fp, show=False):
    """
    Read rules from the yaml file.

    Parameters
    ----------
    yaml_rules_fp : str
        Path to the yaml file containing the cleaning rules.

    show : bool
        Whether to show the rules.

    Returns
    -------
    rules : dict
        Rules in dictionary form.
    """
    validate_fp(yaml_rules_fp)
    with open(yaml_rules_fp) as f:
        try:
            rules = yaml.load(f)
        except:
            raise (
                "Yaml rules file %s may not be in .yml format." % yaml_rules_fp
            )
    validate_rules(yaml_rules_fp, rules)
    if show:
        print('%s cleaning rules %s' % (('='*40), ('='*40)))
        for i,j in rules.items():
            print()
            print(i)
            print(j)
        print('\n%s' % ('='*100))
    return rules


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

    sample_id_cols : list
        Names of the columns containing the sample IDs
    """
    if not yaml_rules_fp:
        yaml_rules_fp = os.path.join(
            "tests", "test_datasets", "cleaning_rules.yaml"
        )
    # Read the rules from the yaml fule
    rules = get_yaml_rules(yaml_rules_fp, show)
    # but the final user version will be written too at the end if different from np.nan
    nan_value_user, sample_id_cols = get_nan_value_and_sample_id_cols(rules)
    # default NaN value will be used in the per_column rules
    nan_value = 'nan'
    return rules, nan_value, nan_value_user, sample_id_cols
