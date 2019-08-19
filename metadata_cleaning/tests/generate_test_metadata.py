#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from os.path import join
import random
import pandas as pd


def generate_test_metadata(
    data,
    basename,
    rules_in,
    nrows
):
    """
    Create a metadata for unittest.
    User must hard-code edits.

    Parameters
    ----------
    data : dict
        Full dummy data frame content.

    basename : str
        Name of the current test data set,
        To be used as basename in:
        "tests/test_datasets/inputs/metadata/metadata_test_<basename>.tsv"
    """

    # Make the data frame for the test case
    if basename == 'full':
        # complete dummy data set
        data_pd = pd.DataFrame(data)
    elif basename == 'empty':
        # empty file
        data_pd = pd.DataFrame()
    elif basename == 'noSampleId':
        data_pd = pd.DataFrame(
            dict((x, y) for x, y in data.items() if x != 'sample_name')
        )
    elif 'XYSampleDtypes' in basename:
        data_pd = pd.DataFrame({'X': [1,2,3], 'Y': [1,2,3], 'Z': [1,2,3]})

    elif basename == 'allSamID':
        data_pd = pd.DataFrame(
            dict((x, y) for x, y in data.items() if x in rules_in)
        )
        print(data_pd)
        for samID in ['sample_id', '#SampleID', 'sample', '#SampleName', 'sam']:
            data_pd[samID] = data_pd['sample_name']

    elif basename == '':
        data_pd = pd.DataFrame({
            '': [],
        })

    data_pd = data_pd.iloc[:nrows,:]
    # print(data_pd)

    # Write the table in the file having the basename
    path = join("test_datasets", "input", "metadata", "metadata_test_%s.tsv" % basename)
    if data_pd.shape[0]:
        data_pd.to_csv(path, index=False, sep='\t')
    else:
        open(path, 'w').close()


if __name__ == "__main__":

    data = {'sample_name':
                [0, 1, 2, 3, 4, 5, 6, 6, 6, 7, 8, 9, 10],
            'bloom_fraction':
                [float(x) / 100 for x in range(-50, 210, 20)],
            'TF':
                [random.choice([True, False]) for x in range(13)],
            'COLLECTION_DATE':
                ['4/01/2015', '5/8/15', '03/25/2015', '03/05/2015',
                 '06/16/2015', '3/9/2015', '04/26/2015', '05/15/15',
                 '03/09/2015', '04/26/2015', '05/15/2015', '4/7/2015',
                 '04/16/15'],
            'COLLECTION_TIME':
                ['00:20:00', '22:00:00', '19:00:00', '11:00:00',
                 '9:45:00', '07:00:00', '9:30:00', '11:05:00',
                 '7:00:00', '9:30:00', '11:05:00', '15:30:00',
                 '13:15:00'],
            'COLLECTION_TIMESTAMP':
                ['04/01/15 00:20', '5/8/2015 22:00', '03/25/2015 19:00',
                 '03/05/2015 11:00', '06/16/2015 9:45', '3/09/2015 7:00',
                 '04/26/2015 09:30', '05/15/2015 11:05', '5/8/2015 22:00',
                 '3/25/15 19:00', '03/05/15 11:00', '04/07/15 15:30',
                 '04/16/2015 13:15'],
            'bmi':
                [x for x in range(10, 131, 10)],
            'to_na':
                [random.choice([0, 'Unspecified', 'not provided',
                                'Unspecified', 'not provided',
                                'Unspecified', 'not provided']) for x in range(13)],
            'sex':
                ['male'] * 13,
            'pregnant':
                [random.choice([True, False]) for x in range(13)],
            'latitude':
                ['HERE'] * 13,
            'longitude':
                ['THERE'] * 13,
            'AGE_CORR':
                [0, 1, 3, 4, 0, 1, 2, 3, 20, 20, 20, 20, 20],
            'weight_g':
                [10, 40, 10, 10, 10, 10, 10, 30, 50, 60, 100, 100, 100],
            'height_cm':
                [110, 10, 30, 400, 100, 30, 20, 30, 50, 60, 100, 100, 100],
            'alcohol_gin':
                ['Yes', 'No', 'No', 'No', 'No', 'Yes', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes', 'Yes'],
            'alcohol_chartreuse':
                ['No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'Yes', 'No', 'No', 'No', 'No'],
            'alcohol_consumption':
                ['Yes', 'No', 'No', 'No', 'No', 'Yes', 'Yes', 'No', 'No', 'Yes', 'No', 'No', 'No']
            }

    print(sorted(data.keys()))

    rules_in = [
#        'AGE_CORR',
 #       'COLLECTION_DATE',
  #      'COLLECTION_TIME',
   #     'COLLECTION_TIMESTAMP',
        'TF',
    #    'alcohol_chartreuse',
     #   'alcohol_consumption',
      #  'alcohol_gin',
        'bloom_fraction',
#        'bmi',
 #       'height_cm',
  #      'latitude',
   #     'longitude',
    #    'pregnant',
        'sample_name',
#        'sex',
        'to_na',
 #       'weight_g',
    ]


    basename = 'empty'
    basename = 'full'
    basename = 'noSampleId'
    basename = 'XYSampleDtypes'
    basename = 'allSamID'

    generate_test_metadata(
        data, basename, rules_in, 5
    )
