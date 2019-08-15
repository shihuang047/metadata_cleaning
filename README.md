# metadata_cleaning
Clean is a metadata curation tool that applies rules form the user and passed as a yaml file

## Description

Metadata often need to be cleaned upfront in order to adress issues such as
* duplicated sample ids,
* incorrect factor spellings that create additional factors,
* inconsistencies between metadata (e.g. pregnant male, alcoholoic baby, ...),
* variable values for NaN
* ...

## Install

```
git clone https://github.com/FranckLejzerowicz/metadata_cleaning.git
cd metadata_cleaning
python3 setup.py install
```

## Usage

```
cd metadata_cleaning
./metadata_clean.py
```

For now, it's only based on a test dataset in

Options to come on command line, e.g.:
* --input-metadata
* --input-yaml
* --edit-ids
* ...

### Optional arguments

```
TODO (will be based on click)
```

## Inputs

There is a dummy file that's hard coded in the "__main__"  of metadata_clean.py (written in "metadata_cleaning/tests/dummy.tsv").
I will apply on extent files, e.g.:
* ``metadata_cleaning/tests/internal/2019.07.17_danone_md_n3844_selection_draft.xlsx`` : current metadata selection for the shotgun campaign of AIM1
* ``metadata_cleaning/tests/internal/meta_16S_3577s.tsv`` : metadata for the Danone fermentation project

### metadata

|    |   sample_name |   bloom_fraction | TF    | COLLECTION_DATE   | COLLECTION_TIME   | COLLECTION_TIMESTAMP   |   bmi | dummiest     | sex   | latitude   | longitude   | pregnant   |   AGE_CORR |   weight_g |   height_cm | alcohol_gin   | alcohol_chartreuse   | alcohol_consumption   |
|---:|--------------:|-----------------:|:------|:------------------|:------------------|:-----------------------|------:|:-------------|:------|:-----------|:------------|:-----------|-----------:|-----------:|------------:|:--------------|:---------------------|:----------------------|
|  0 |             0 |             -0.5 | True  | 4/01/2015         | 00:20:00          | 04/01/15 00:20         |    10 | 0            | male  | HERE       | THERE       | True       |          0 |         10 |         110 | Yes           | No                   | Yes                   |
|  1 |             1 |             -0.3 | True  | 5/8/15            | 22:00:00          | 5/8/2015 22:00         |    20 | not provided | male  | HERE       | THERE       | True       |          1 |         40 |          10 | No            | No                   | No                    |
|  2 |             2 |             -0.1 | True  | 03/25/2015        | 19:00:00          | 03/25/2015 19:00       |    30 | Unspecified  | male  | HERE       | THERE       | False      |          3 |         10 |          30 | No            | No                   | No                    |
|  3 |             3 |              0.1 | True  | 03/05/2015        | 11:00:00          | 03/05/2015 11:00       |    40 | not provided | male  | HERE       | THERE       | False      |          4 |         10 |         400 | No            | No                   | No                    |
|  4 |             4 |              0.3 | False | 06/16/2015        | 9:45:00           | 06/16/2015 9:45        |    50 | not provided | male  | HERE       | THERE       | False      |          0 |         10 |         100 | No            | No                   | No                    |
|  5 |             5 |              0.5 | True  | 3/9/2015          | 07:00:00          | 3/09/2015 7:00         |    60 | 0            | male  | HERE       | THERE       | False      |          1 |         10 |          30 | Yes           | No                   | Yes                   |
|  6 |             6 |              0.7 | True  | 04/26/2015        | 9:30:00           | 04/26/2015 09:30       |    70 | not provided | male  | HERE       | THERE       | False      |          2 |         10 |          20 | Yes           | No                   | Yes                   |
|  7 |             6 |              0.9 | False | 05/15/15          | 11:05:00          | 05/15/2015 11:05       |    80 | not provided | male  | HERE       | THERE       | False      |          3 |         30 |          30 | No            | No                   | No                    |
|  8 |             6 |              1.1 | True  | 03/09/2015        | 7:00:00           | 5/8/2015 22:00         |    90 | not provided | male  | HERE       | THERE       | False      |         20 |         50 |          50 | No            | Yes                  | No                    |
|  9 |             7 |              1.3 | False | 04/26/2015        | 9:30:00           | 3/25/15 19:00          |   100 | not provided | male  | HERE       | THERE       | True       |         20 |         60 |          60 | Yes           | No                   | Yes                   |
| 10 |             8 |              1.5 | True  | 05/15/2015        | 11:05:00          | 03/05/15 11:00         |   110 | 0            | male  | HERE       | THERE       | True       |         20 |        100 |         100 | No            | No                   | No                    |
| 11 |             9 |              1.7 | False | 4/7/2015          | 15:30:00          | 04/07/15 15:30         |   120 | 0            | male  | HERE       | THERE       | True       |         20 |        100 |         100 | Yes           | No                   | No                    |
| 12 |            10 |              1.9 | True  | 04/16/15          | 13:15:00          | 04/16/2015 13:15       |   130 | Unspecified  | male  | HERE       | THERE       | True       |         20 |        100 |         100 | Yes           | No                   | No                    |

### yaml rules

``metadata_cleaning/tests/cleaning_rules.yaml``
(these rules have been extracted from the Danone queries: ``metadata_cleaning/tests/iternal/Danone_md_colInfos_n3844_AC_LR_AC_FL.txt``)
```
# dict to tell which value to replace [applies to all columns]
booleans: {'False': 'No', 'True': 'Yes'}

# nested dict to tell which multiple conditions to assess and on which column to make a resulting edit [applies to the {<column>: }]
combinations:
  ? !!python/tuple [age, alcohol_consumption]
  : - !!python/tuple ['range(0,4)', true]
    - {alcohol_consumption: Missing}
  ? !!python/tuple [age, height]
  : - !!python/tuple ['range(0,4)', 'range(105,None)']
    - {height: Missing}
  ? !!python/tuple [age, weight]
  : - !!python/tuple ['range(0,4)', 'range(20,None)']
    - {weight: Missing}
  ? !!python/tuple [alcohol, alcohol_consumption]
  : - !!python/tuple [true, false]
    - {alcohol_consumption: 'Yes'}
  ? !!python/tuple [sex, pregnant]
  : - !!python/tuple [male, true]
    - {pregnant: .nan}

# list to tell which columns to remove
del_columns: [latitude, longitude]

# default value to use for replacement of violating checks [applies to all columns]
na_value: Missing

# dict to tell which "nan" value to replace [applies to all columns]
nans: {Unknown: Missing, Unspecified: Missing, no data: Missing, not provided: Missing}

# dict of lists to tell which conditions to check for violations [applies to the column:]
per_column:
  age: ['range(0,120)']
  bloom_fraction: ['range(0,1)']
  bmi: ['range(15,50)']
  country:
  - {Cote D'ivoire: "C\xF4te d'Ivoire", 'Iran, Islamic Republic of': Iran (Islamic
      Republic of), Libyan Arab Jamahiriya: Libya, Reunion: "R\xE9union", US: United
      States, USA: United States, United States of America: United States}
  height: ['range(48,210)']
  weight: ['range(2.5,200)']

# tells which are the sample ID columns and if needs to check they are unique and if not how to edit them
sample_id:
  check_sample_id_force: true
  check_sample_id_unique: true
  sample_id_cols: ['#SampleID', sample_name]

# tells which time column to re-foramt homogeneously and how
time_format:
  columns: [COLLECTION_TIMESTAMP, COLLECTION_DATE, COLLECTION_TIME]
  format: DD/MM/YYYY HH:MM
  ranges: range(2011,2019)
```

*This format can be written from a simpler user entry-point*

## Output

Cleaned metadata (according) to the rules:

|    |   sample_name |   bloom_fraction | TF    | COLLECTION_DATE   | COLLECTION_TIME   | COLLECTION_TIMESTAMP   |   bmi | dummiest     | sex   | latitude   | longitude   | pregnant   |   AGE_CORR |   weight_g |   height_cm | alcohol_gin   | alcohol_chartreuse   | alcohol_consumption   |
|---:|--------------:|-----------------:|:------|:------------------|:------------------|:-----------------------|------:|:-------------|:------|:-----------|:------------|:-----------|-----------:|-----------:|------------:|:--------------|:---------------------|:----------------------|
|  0 |             0 |             -0.5 | True  | 4/01/2015         | 00:20:00          | 04/01/15 00:20         |    10 | 0            | male  | HERE       | THERE       | True       |          0 |         10 |         110 | Yes           | No                   | Yes                   |
|  1 |             1 |             -0.3 | True  | 5/8/15            | 22:00:00          | 5/8/2015 22:00         |    20 | not provided | male  | HERE       | THERE       | True       |          1 |         40 |          10 | No            | No                   | No                    |
|  2 |             2 |             -0.1 | True  | 03/25/2015        | 19:00:00          | 03/25/2015 19:00       |    30 | Unspecified  | male  | HERE       | THERE       | False      |          3 |         10 |          30 | No            | No                   | No                    |
|  3 |             3 |              0.1 | True  | 03/05/2015        | 11:00:00          | 03/05/2015 11:00       |    40 | not provided | male  | HERE       | THERE       | False      |          4 |         10 |         400 | No            | No                   | No                    |
|  4 |             4 |              0.3 | False | 06/16/2015        | 9:45:00           | 06/16/2015 9:45        |    50 | not provided | male  | HERE       | THERE       | False      |          0 |         10 |         100 | No            | No                   | No                    |
|  5 |             5 |              0.5 | True  | 3/9/2015          | 07:00:00          | 3/09/2015 7:00         |    60 | 0            | male  | HERE       | THERE       | False      |          1 |         10 |          30 | Yes           | No                   | Yes                   |
|  6 |             6 |              0.7 | True  | 04/26/2015        | 9:30:00           | 04/26/2015 09:30       |    70 | not provided | male  | HERE       | THERE       | False      |          2 |         10 |          20 | Yes           | No                   | Yes                   |
|  7 |             6 |              0.9 | False | 05/15/15          | 11:05:00          | 05/15/2015 11:05       |    80 | not provided | male  | HERE       | THERE       | False      |          3 |         30 |          30 | No            | No                   | No                    |
|  8 |             6 |              1.1 | True  | 03/09/2015        | 7:00:00           | 5/8/2015 22:00         |    90 | not provided | male  | HERE       | THERE       | False      |         20 |         50 |          50 | No            | Yes                  | No                    |
|  9 |             7 |              1.3 | False | 04/26/2015        | 9:30:00           | 3/25/15 19:00          |   100 | not provided | male  | HERE       | THERE       | True       |         20 |         60 |          60 | Yes           | No                   | Yes                   |
| 10 |             8 |              1.5 | True  | 05/15/2015        | 11:05:00          | 03/05/15 11:00         |   110 | 0            | male  | HERE       | THERE       | True       |         20 |        100 |         100 | No            | No                   | No                    |
| 11 |             9 |              1.7 | False | 4/7/2015          | 15:30:00          | 04/07/15 15:30         |   120 | 0            | male  | HERE       | THERE       | True       |         20 |        100 |         100 | Yes           | No                   | No                    |
| 12 |            10 |              1.9 | True  | 04/16/15          | 13:15:00          | 04/16/2015 13:15       |   130 | Unspecified  | male  | HERE       | THERE       | True       |         20 |        100 |         100 | Yes           | No                   | No                    |

*Some systematic rules need to be defined*

Bug Reports:
-----------
contact ``flejzerowicz@ucsd.edu``
