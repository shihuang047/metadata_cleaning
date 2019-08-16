#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import yaml


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
    with open(yaml_rules_fp) as f:
        rules = yaml.load(f)

    if show:
        print('%s cleaning rules %s' % (('='*40), ('='*40)))
        for i,j in rules.items():
            print()
            print(i)
            print(j)
        print('\n%s' % ('='*100))
    return rules