#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from os.path import join
import numpy as np
import pytest
import yaml
import ast

from yaml.scanner import ScannerError

from metadata_cleaning._yaml_utils import (
    validate_fp,
    get_yaml_rules,
    validate_rules,
    get_nan_value_and_sample_id_cols,
    parse_yaml_file
)


def test_validate_fp():
    # test the presence of the file
    missing_fp = join("test_datasets", "input", "metadata", "metadata_test_NOFILE.tsv")
    with pytest.raises(FileNotFoundError):
        validate_fp(missing_fp)
    metadata = join("test_datasets", "input", "metadata", "dummy.tsv")
    assert metadata == validate_fp(metadata)
    rules = join("test_datasets", "input", "rules", "cleaning_rules.yaml")
    assert rules == validate_fp(rules)


def test_validate_rules():

    with pytest.raises(ValueError) as e:
        validate_rules('file', 'string')
    assert 'are not properly read' in str(e.value)

    with pytest.raises(ValueError) as e:
        validate_rules('file', {'not_sample_id': 1})
    assert "Mandatory 'sample_id' rule missing in" in str(e.value)

    with pytest.raises(ValueError) as e:
        validate_rules('file', {'sample_id': {'not_sample_id_cols': 1}})
    assert "Mandatory 'sample_id_cols' rule missing in" in str(e.value)

    rules_fp = join("test_datasets", "input", "rules", "rules_test_noSampleId.yaml")
    rules = yaml.load(open(rules_fp, encoding='utf8'), Loader=yaml.CLoader)
    with pytest.raises(ValueError) as e:
        validate_rules(rules_fp, rules)
    assert "Mandatory 'sample_id' rule missing in" in str(e.value)


def get_dict_from_yaml(rules_yaml):
    rules_dict = rules_yaml.replace('.yaml', '.dict')
    with open(rules_dict, 'rt', encoding='utf8') as f:
        s = f.read()
        rules = ast.literal_eval(s)
    return rules


def test_get_yaml_rules():
    def assert_in_e_info(e, *should_be_in):
        s_val = str(e.value)
        for thing in should_be_in:
            assert thing in s_val
    # give a non-yaml file
    rules_fp = join("test_datasets", "input", "rules", "cleaning_rules.txt")
    with pytest.raises(ScannerError) as e:
        get_yaml_rules(rules_fp)
    assert str(e.value) == "Yaml rules file may not be in .yml format"

    for rules_fp_base in ["rules_test_full.yaml",
                          "rules_test_noSampleId.yaml"]:
        rules_yaml = join("test_datasets", "input", "rules", rules_fp_base)
        rules = get_dict_from_yaml(rules_yaml)
        assert rules == get_yaml_rules(rules_yaml)


def test_get_nan_value_and_sample_id_cols():
    assert 'NaN' == get_nan_value_and_sample_id_cols(
        {'na_value': 'NaN'}
    )
    assert np.isnan(get_nan_value_and_sample_id_cols({}))


def test_parse_yaml_file():

    rules_fp = join("test_datasets", "input", "rules", "cleaning_rules.yaml")
    rules = get_dict_from_yaml(rules_fp)
    assert (rules, 'nan', 'Missing', [
        '#SampleID', 'sample_name'
    ]) == parse_yaml_file(rules_fp, False)

    rules_fp = join("test_datasets", "input", "rules", "rules_test_oneSamNA.yaml")
    rules = get_dict_from_yaml(rules_fp)
    assert (rules, 'nan', 'NA', ['sample_name']) == parse_yaml_file(rules_fp, False)