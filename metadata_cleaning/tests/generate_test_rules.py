#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from os.path import join
import yaml
import json
import codecs


def generate_test_yaml(
    data,
    basename,
    rules_in,
    rules_sub
):
    """
    Create a metadata for unittest.
    User must hard-code edits.

    Parameters
    ----------
    data : dict
        Full dummy rules content.

    basename : str
        Name of the current test data set,
        To be used as basename in:
        "tests/test_datasets/inputs/rules/rules_test_<basename>.yaml"

    rules_in : list
        List of rule keys to keep.

    rules_sub : dict
        Content of the rules.
    """

    data_yaml = {}

    # Make the data frame for the test case
    if basename == 'full':
        # complete dummy rules
        data_yaml = dict(data)

    elif basename == 'empty':
        # empty file
        data_yaml = ''

    elif basename in ['']:
        data_yaml = dict((x, rules_sub[x]) for x, y in data.items())

    elif basename in ['oneSamNA']:
        data_yaml = dict((x, rules_sub[x]) for x, y in data.items() if x in rules_in)

    elif basename in ['noNa_value']:
        data_yaml = dict((x, y) for x, y in data.items() if x in rules_in)

    elif basename in ['noSampleId']:
        data_yaml = dict((x, y) for x, y in data.items() if x in rules_in)

    # Write the table in the file having the basename
    path_yaml = join("test_datasets", "input", "rules", "rules_test_%s.yaml" % basename)
    path_dict = path_yaml.replace('.yaml', '.dict')
    if data_yaml:
        file = codecs.open(path_dict, "w", "utf-8")
        file.write(str(data_yaml))
        file.close()
        with open(path_yaml, "w") as o:
            o.write(yaml.dump(data_yaml))
    else:
        open(path_yaml, 'w').close()
        open(path_dict, 'w').close()
    print(path_yaml)
    print(path_dict)


if __name__ == "__main__":

    data = {
        'sample_id': {
            'sample_id_cols': [
                '#SampleID', 'sample_name'
            ],
            'check_sample_id_unique': True,
            'check_sample_id_force': True
        },

        'nans': [
            'Not provided', 'Not_provided',
            'not provided', 'not_provided',
            'Unknown', 'unknown',
            'Unspecified', 'unspecified',
            'no data', 'no_data'
        ],

        'na_value': 'Missing',

        'solve_dtypes': True,

        'del_columns': [
            'latitude',
            'longitude'
        ],

        'forbidden_characters': {
            '(': '_',
            '%': '_',
            ',': '_',
            '/': '_',
            ')': '_',
            ' ': '_'
        },

        'booleans': {
            'False': 'No',
            'True': 'Yes'
        },

        'time_format': {
            'format': 'DD/MM/YYYY HH:MM',
            'columns': [
                'COLLECTION_TIMESTAMP',
                'COLLECTION_DATE',
                'COLLECTION_TIME'
            ],
            'ranges': 'range(2011,2019)'
        },

        'per_column': {
            'age': [
                'range(0,120)'
            ],
            'bloom_fraction': [
                'range(0,1)'
            ],
            'country': [
                {
                    "Cote D'ivoire": "Côte d'Ivoire",
                    'Iran, Islamic Republic of': 'Iran (Islamic Republic of)',
                    'Libyan Arab Jamahiriya': 'Libya',
                    'Reunion': 'Réunion',
                    'USA': 'United States',
                    'United States of America': 'United States',
                    'US': 'United States'
                }
            ],
            'bmi': [
                'range(15,50)'
            ],
            'height': [
                'range(48,210)'
            ],
            'weight': [
                'range(2.5,200)'
            ]
        },

        'combinations': {
            ('age', 'alcohol_consumption'): [
                ('range(0,4)', True), 'alcohol_consumption'
            ],
            ('alcohol', 'alcohol_consumption'): [
                (True, False), {'alcohol_consumption': 'Yes'}
            ],
            ('age', 'height'): [
                ('range(0,4)', 'range(105,None)'), 'height'
            ],
            ('age', 'weight'): [
                ('range(0,4)', 'range(20,None)'), 'weight'
            ],
            ('sex', 'pregnant'): [
                ('male', True), {'pregnant': 'NaN'}
            ]
        }
    }

    rules_in = [
#        'booleans',
 #       'combinations',
  #      'del_columns',
   #     'forbidden_characters',
    #    'na_value',
        'nans',
     #   'per_column',
        'sample_id',
        'solve_dtypes',
       # 'time_format',
    ]

    rules_sub = {'sample_id': {'sample_id_cols': ['sample_name'],
                               'check_sample_id_unique': True,
                               'check_sample_id_force': True},
                 'nans': ['Not provided', 'Not_provided', 'not provided', 'not_provided',
                          'Unknown', 'unknown', 'Unspecified', 'unspecified', 'no data', 'no_data'],
                 'na_value': 'NA',
                 'solve_dtypes': True,
                 'del_columns': ['latitude', 'longitude'],
                 'forbidden_characters': {'(': '_', '%': '_', ',': '_', '/': '_', ')': '_', ' ': '_'},
                 'booleans': {'False': 'No', 'True': 'Yes'},
                 'time_format': {'format': 'DD/MM/YYYY HH:MM',
                                 'columns': ['COLLECTION_TIMESTAMP', 'COLLECTION_DATE', 'COLLECTION_TIME'],
                                 'ranges': 'range(2011,2019)'},
                 'per_column': {'age': ['range(0,120)'],
                                'bloom_fraction': ['range(0,1)'],
                                'country': [{"Cote D'ivoire": "Côte d'Ivoire",
                                             'Iran, Islamic Republic of': 'Iran (Islamic Republic of)',
                                             'Libyan Arab Jamahiriya': 'Libya',
                                             'Reunion': 'Réunion',
                                             'USA': 'United States',
                                             'United States of America': 'United States',
                                             'US': 'United States'
                                             }],
                                'bmi': ['range(15,50)'],
                                'height': ['range(48,210)'],
                                'weight': ['range(2.5,200)']},
                 'combinations': {('age', 'alcohol_consumption'): [('range(0,4)', True), 'alcohol_consumption'],
                                  ('alcohol', 'alcohol_consumption'): [(True, False), {'alcohol_consumption': 'Yes'}],
                                  ('age', 'height'): [('range(0,4)', 'range(105,None)'), 'height'],
                                  ('age', 'weight'): [('range(0,4)', 'range(20,None)'), 'weight'],
                                  ('sex', 'pregnant'): [('male', True), {'pregnant': 'NaN'}]}
                 }

    basename = 'empty'
    basename = 'noSampleId'
    basename = 'full'
    basename = 'oneSamNA'
    basename = 'noNa_value'

    generate_test_yaml(
        data,
        basename,
        rules_in,
        rules_sub
    )
