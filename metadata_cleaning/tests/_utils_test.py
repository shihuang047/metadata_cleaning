import random
import pandas as pd

def build_dummy_dataset_for_lauriane_rules_testing():
    dummy = pd.DataFrame({'sample_name': [0,1,2,3,4,5,6,6,6,7,8,9,10],
                          'bloom_fraction': [float(x)/100 for x in range(-50, 210, 20)],
                          'TF': [random.choice([True, False]) for x in range(13)],
                          'COLLECTION_DATE': ['4/01/2015', '5/8/15', '03/25/2015', '03/05/2015', '06/16/2015',
                                              '3/9/2015', '04/26/2015', '05/15/15', '03/09/2015', '04/26/2015',
                                              '05/15/2015', '4/7/2015', '04/16/15'],
                          'COLLECTION_TIME': ['00:20:00', '22:00:00', '19:00:00', '11:00:00','9:45:00', '07:00:00',
                                              '9:30:00', '11:05:00', '7:00:00', '9:30:00', '11:05:00', '15:30:00',
                                              '13:15:00'],
                          'COLLECTION_TIMESTAMP': ['04/01/15 00:20', '5/8/2015 22:00', '03/25/2015 19:00',
                                                   '03/05/2015 11:00', '06/16/2015 9:45', '3/09/2015 7:00',
                                                   '04/26/2015 09:30', '05/15/2015 11:05', '5/8/2015 22:00',
                                                   '3/25/15 19:00', '03/05/15 11:00', '04/07/15 15:30', '04/16/2015 '
                                                                                                        '13:15'],
                          'bmi': [x for x in range(10,131,10)],
                          'dummiest': [random.choice([0, 'Unspecified', 'not provided']) for x in range(-50, 210, 20)],
                          'sex': ['male']*13,
                          'pregnant': [random.choice([True, False]) for x in range(13)],
                          'latitude': ['HERE']*13,
                          'longitude': ['THERE']*13,
                          'AGE_CORR': [0,1,3,4,0,1,2,3,20,20,20,20,20],
                          'weight_g': [10,40,10,10,10,10,10,30,50,60,100,100,100],
                          'height_cm': [110,10,30,400,100,30,20,30,50,60,100,100,100],
                          'alcohol_gin': ['Yes','No','No','No','No','Yes','Yes','No','No','Yes','No','Yes','Yes'],
                          'alcohol_chartreuse': ['No','No','No','No','No','No','No','No','Yes','No','No','No','No'],
                          'alcohol_consumption': ['Yes','No','No','No','No','Yes','Yes','No','No','Yes','No','No',
                                                  'No']})
    return dummy
