# metadata_cleaning
Clean is a metadata curation tool that applies rules form the user and passed as a yaml file

## Description

Metadata often need to be cleaned upfront in order to adress issues such as
* duplicated sample ids,
* incorrect factor spellings that create additional factors,
* inconsistencies between metadata (e.g. pregnant male, alcoholic baby, ...),
* variable values for NaN
* ...

## Install

```
git clone https://github.com/FranckLejzerowicz/metadata_cleaning.git
cd metadata_cleaning
python3 setup.py install
```

## Input / Output

*Look at the dummy input / output metadata table examples below, and the yaml example too (encoding the cleaning
 rules from the Danone team)*

## Inputs

#### Metadata
It works well on the Danone files, e.g.:
* Current metadata selection for the shotgun campaign of AIM1: `metadata_cleaning/tests/internal/2019.07
.17_danone_md_n3844_selection_draft.xlsx`
* Metadata for the Danone fermentation project: `metadata_cleaning/tests/internal/meta_16S_3577s.tsv`
* There is a dummy file that's hard coded in the "__main__"  of `metadata_clean.py` (and also written in
 `metadata_cleaning/tests/dummy.tsv`).

#### Yaml rules

The way to generate this file could be done in several ways:

* Use the yaml rules maker (**TO DO**: develop a helper tool based on `raw_input`)
* Direct writing in yaml: see example below
* Python dictionary-based:
    * Write the rules as a dictionary, e.g.
        ```
        full_yaml_d = {
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
            ],
        
            'forbidden_characters': {
                '(': '_',
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
                'weight': [
                    'range(2.5,200)'
                ]
            },
        
            'combinations': {
                ('sex', 'pregnant'): [
                    ('male', True), {'pregnant': 'NaN'}
                ]
            }
        }
        
        
        ```
    * Run this on the dictionary:
        ```
        import yaml
        print(yaml.dump(full_yaml_d))
        ```  
    * Copy / paste the result in a file that is passed to ``metadata_cleaning.py``

*Some systematic rules need to be defined*

*This format can be written from a simpler user entry-point*

``metadata_cleaning/tests/cleaning_rules.yaml``
(these rules have been extracted from the Danone queries: ``metadata_cleaning/tests/iternal/Danone_md_colInfos_n3844_AC_LR_AC_FL.txt``)


Most directives are given in the yaml rules file, but arguments passed to command line could override (see below).

**Attention**: for the rules "combinations", the order imports: a column might have to be cleaned based on another
 column that has already been cleaned! 

## Outputs

For now, two versions of the cleaned metadata are written:
* One output file with all the missing data factors encoded as np.nan (i.e. NaN interpreted as
 numeric in tools like pandas or R). This file will have a ```_clean.tsv``` extension instead of the original
  extension of your input file name.
* One output file the missing data factors encoded as specified in the "na_value" of the yaml. This file will have
 a ```_clean_<username>.tsv``` extension instead of the original extension of your input file name.
 
## Usage

```
cd metadata_cleaning
./metadata_clean.py
```

### Optional arguments

```
TODO
```

Command line to come (based on click), e.g.:
* --input-metadata
* --input-yaml
* --edit-ids
* --na_value
* ...


## Examples

### Input metadata

|    |   sample_name |   bloom_fraction | TF    | COLLECTION_DATE   | COLLECTION_TIME   | COLLECTION_TIMESTAMP   |   bmi | dummiest     | sex   | latitude   | longitude   | pregnant   |   AGE_CORR |   weight_g |   height_cm | alcohol_gin   | alcohol_chartreuse   | alcohol_consumption   |
|---:|--------------:|-----------------:|:------|:------------------|:------------------|:-----------------------|------:|:-------------|:------|:-----------|:------------|:-----------|-----------:|-----------:|------------:|:--------------|:---------------------|:----------------------|
|  0 |             0 |             -0.5 | True  | 4/01/2015         | 00:20:00          | 04/01/15 00:20         |    10 | Unspecified  | male  | HERE       | THERE       | True       |          0 |         10 |         110 | Yes           | No                   | Yes                   |
|  1 |             1 |             -0.3 | False | 5/8/15            | 22:00:00          | 5/8/2015 22:00         |    20 | Unspecified  | male  | HERE       | THERE       | True       |          1 |         40 |          10 | No            | No                   | No                    |
|  2 |             2 |             -0.1 | False | 03/25/2015        | 19:00:00          | 03/25/2015 19:00       |    30 | 0            | male  | HERE       | THERE       | False      |          3 |         10 |          30 | No            | No                   | No                    |
|  3 |             3 |              0.1 | True  | 03/05/2015        | 11:00:00          | 03/05/2015 11:00       |    40 | Unspecified  | male  | HERE       | THERE       | True       |          4 |         10 |         400 | No            | No                   | No                    |
|  4 |             4 |              0.3 | True  | 06/16/2015        | 9:45:00           | 06/16/2015 9:45        |    50 | Unspecified  | male  | HERE       | THERE       | False      |          0 |         10 |         100 | No            | No                   | No                    |
|  5 |             5 |              0.5 | False | 3/9/2015          | 07:00:00          | 3/09/2015 7:00         |    60 | Unspecified  | male  | HERE       | THERE       | True       |          1 |         10 |          30 | Yes           | No                   | Yes                   |
|  6 |             6 |              0.7 | True  | 04/26/2015        | 9:30:00           | 04/26/2015 09:30       |    70 | not provided | male  | HERE       | THERE       | True       |          2 |         10 |          20 | Yes           | No                   | Yes                   |
|  7 |             6 |              0.9 | False | 05/15/15          | 11:05:00          | 05/15/2015 11:05       |    80 | Unspecified  | male  | HERE       | THERE       | True       |          3 |         30 |          30 | No            | No                   | No                    |
|  8 |             6 |              1.1 | True  | 03/09/2015        | 7:00:00           | 5/8/2015 22:00         |    90 | Unspecified  | male  | HERE       | THERE       | True       |         20 |         50 |          50 | No            | Yes                  | No                    |
|  9 |             7 |              1.3 | False | 04/26/2015        | 9:30:00           | 3/25/15 19:00          |   100 | not provided | male  | HERE       | THERE       | True       |         20 |         60 |          60 | Yes           | No                   | Yes                   |
| 10 |             8 |              1.5 | True  | 05/15/2015        | 11:05:00          | 03/05/15 11:00         |   110 | 0            | male  | HERE       | THERE       | True       |         20 |        100 |         100 | No            | No                   | No                    |
| 11 |             9 |              1.7 | True  | 4/7/2015          | 15:30:00          | 04/07/15 15:30         |   120 | not provided | male  | HERE       | THERE       | True       |         20 |        100 |         100 | Yes           | No                   | No                    |
| 12 |            10 |              1.9 | False | 04/16/15          | 13:15:00          | 04/16/2015 13:15       |   130 | Unspecified  | male  | HERE       | THERE       | True       |         20 |        100 |         100 | Yes           | No                   | No                    |
​
### yaml rules

Note: Explanations are indicated in commented line: 

```
## dict to tell which value to replace [applies to all columns]
## (the lowercase cases will be taken into account)
booleans: {'False': 'No', 'True': 'Yes'}

# nested dict to tell which multiple conditions to assess
# and on which column to make a resulting edit [applies to the {<column>: }]
## NOTE1: THE ORDER MAY MATTER!
## NOTE2: FOR THE "range(x,y)", THE DATA MUST BE:
##            e.g. range(0,4)      means 0 >= data >= 4
##            e.g. range(105,None) means data >= 105
##            e.g. range(None,4)   means data <= 4
combinations:

    # --> START OF ONE COMBINATION RULE <--
                   # the columns here 
  ? !!python/tuple [age, alcohol_consumption]
                     # the rules on the above column (apply in same order) 
  : - !!python/tuple ['range(0,4)', true]
    # column to edit with the value of na_value (see rule "na_value")
    - alcohol_consumption
    # --> END OF ONE COMBINATION RULE <--

  ? !!python/tuple [age, height]
  : - !!python/tuple ['range(0,4)', 'range(105,None)']
    - height
  ? !!python/tuple [age, weight]
  : - !!python/tuple ['range(0,4)', 'range(20,None)']
    - weight
  ? !!python/tuple [alcohol, alcohol_consumption]
  : - !!python/tuple [true, false]
    # when a dictionary structure:
    #    key   -> column to edit
    #    value -> with what value to make the edit 
  - {alcohol_consumption: 'Yes'}
  ? !!python/tuple [sex, pregnant]
  : - !!python/tuple [male, true]
    - {pregnant: NaN}

## list to tell which columns to remove
del_columns: [latitude, longitude]

## character to replace in every column
forbidden_characters: {' ': _, '%': _, (: _, ): _, ',': _, /: _}

## default value to use for replacement of violating checks [applies to all columns]
na_value: Missing

## list to tell which value to replace with "na_value" [applies to all columns]
nans: [Not provided, Not_provided, not provided, not_provided, Unknown, unknown, Unspecified,
  unspecified, no data, no_data]

## dict of lists to tell which conditions to check for violations [applies to the column:]
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

## tells which are the sample ID columns
## and if needs to check they are unique and if not how to edit them
sample_id:
  check_sample_id_force: true
  check_sample_id_unique: true
  sample_id_cols: ['#SampleID', sample_name]

## tells whether to solve the dtypes
## NOTE: THIS WILL NO NECESSARILY HOLD IF "na_value" in not np.nan
##       HOWEVER, IT WILL IN THE FIRST OUTPUT (i.e. "_clean.tsv")  
solve_dtypes: true

## tells which time column to re-foramt homogeneously and how
time_format:
  columns: [COLLECTION_TIMESTAMP, COLLECTION_DATE, COLLECTION_TIME]
  format: DD/MM/YYYY HH:MM
  ranges: range(2011,2019)
```

### Output metadata

Cleaned metadata (according) to the rules:


|    |   sample_name |   bloom_fraction | TF   | COLLECTION_DATE   | COLLECTION_TIME   | COLLECTION_TIMESTAMP   |   bmi |   dummiest | sex   | pregnant   |   AGE_CORR |   weight_g |   height_cm | alcohol_gin   | alcohol_chartreuse   | alcohol_consumption   |
|---:|--------------:|-----------------:|:-----|:------------------|:------------------|:-----------------------|------:|-----------:|:------|:-----------|-----------:|-----------:|------------:|:--------------|:---------------------|:----------------------|
|  0 |           0   |            nan   | Yes  | 01/04/2015        | 00:20:00          | 01/04/2015 00:20:00    |   nan |        nan | male  | NaN        |          0 |         10 |         nan | Yes           | No                   | nan                   |
|  1 |           1   |            nan   | No   | 08/05/2015        | 22:00:00          | 08/05/2015 22:00:00    |    20 |        nan | male  | NaN        |          1 |        nan |         nan | No            | No                   | No                    |
|  2 |           2   |            nan   | No   | 25/03/2015        | 19:00:00          | 25/03/2015 19:00:00    |    30 |          0 | male  | No         |          3 |         10 |         nan | No            | No                   | No                    |
|  3 |           3   |              0.1 | Yes  | 05/03/2015        | 11:00:00          | 05/03/2015 11:00:00    |    40 |        nan | male  | NaN        |          4 |         10 |         nan | No            | No                   | No                    |
|  4 |           4   |              0.3 | Yes  | 16/06/2015        | 09:45:00          | 16/06/2015 09:45:00    |    50 |        nan | male  | No         |          0 |         10 |         100 | No            | No                   | No                    |
|  5 |           5   |              0.5 | No   | 09/03/2015        | 07:00:00          | 09/03/2015 07:00:00    |   nan |        nan | male  | NaN        |          1 |         10 |         nan | Yes           | No                   | nan                   |
|  6 |           6.1 |              0.7 | Yes  | 26/04/2015        | 09:30:00          | 26/04/2015 09:30:00    |   nan |        nan | male  | NaN        |          2 |         10 |         nan | Yes           | No                   | nan                   |
|  7 |           6.2 |              0.9 | No   | 15/05/2015        | 11:05:00          | 15/05/2015 11:05:00    |   nan |        nan | male  | NaN        |          3 |        nan |         nan | No            | No                   | No                    |
|  8 |           6.3 |            nan   | Yes  | 09/03/2015        | 07:00:00          | 08/05/2015 22:00:00    |   nan |        nan | male  | NaN        |         20 |         50 |          50 | No            | Yes                  | Yes                   |
|  9 |           7   |            nan   | No   | 26/04/2015        | 09:30:00          | 25/03/2015 19:00:00    |   nan |        nan | male  | NaN        |         20 |         60 |          60 | Yes           | No                   | Yes                   |
| 10 |           8   |            nan   | Yes  | 15/05/2015        | 11:05:00          | 05/03/2015 11:00:00    |   nan |          0 | male  | NaN        |         20 |        100 |         100 | No            | No                   | No                    |
| 11 |           9   |            nan   | Yes  | 07/04/2015        | 15:30:00          | 07/04/2015 15:30:00    |   nan |        nan | male  | NaN        |         20 |        100 |         100 | Yes           | No                   | Yes                   |
| 12 |          10   |            nan   | No   | 16/04/2015        | 13:15:00          | 16/04/2015 13:15:00    |   nan |        nan | male  | NaN        |         20 |        100 |         100 | Yes           | No                   | Yes                   |


Bug Reports:
-----------
contact ``flejzerowicz@ucsd.edu``
