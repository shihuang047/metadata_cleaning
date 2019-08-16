#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import click
import argparse


from metadata_cleaning.metadata_clean import (
    parse_yaml_file,
    parse_metadata_files,
    metadata_clean,
)

from metadata_cleaning import __version__


@click.command()
@click.option(
#parser.add_argument(
    "-r",
    "-r-yaml-file",
    required=True,
    help="Rules file in yaml format."
)
@click.option(
#parser.add_argument(
    "-m",
    "--m-metadata-file",
    required=True,
    help="Metadata file"
)
@click.option(
#parser.add_argument(
    "-o",
    "--o-metadata-file",
    required=False,
    default=None,
    help=(
        "Output Metadata file name (Default: '*_clean.tsv'). " \
        "If 'na_value' from the yaml of option '-na' is not 'nan' " \
        "(i.e. the numpy's NaN), then another ouput file " \
        "will be generated, with '<previous_output>_<username>.tsv')"
    ),
)
@click.option(
#parser.add_argument(
    "-na",
    "--nan-value",
    required=False,
    default=None,
    help=(
        "Value to be use to replace the missing or violating entries. "
        "Violations are detected based on the rules of the yaml file."
    ),
)
@click.option(
#parser.add_argument(
    "-s",
    "--sample-id",
    required=False,
    multiple=True,
    default=None,
    help=(
        "List of columns names containing samples IDs. "
        "(or any other column(s) which may contain numeric "
        "and should not be interpreted as number."
    ),
)
@click.option(
    "-boo",
    "-no-booleans",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not replace the True/False ('booleans' rules)"
    ),
)
@click.option(
    "-com",
    "-no-combinations",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not check the conditions of combinations ('combinations' rules)"
    ),
)
@click.option(
    "-del",
    "-no-del-columns",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not delete the given columns ('del_columns' rule)"
    ),
)
@click.option(
    "-for",
    "-no-forbidden-characters",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not replace the given forbidden characters ('forbidden_characters' rules)"
    ),
)
@click.option(
    "-nan",
    "-no-nans",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not clean the values of 'nans' ('nans' rules)"
    ),
)
@click.option(
    "-per",
    "-no-per-column",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not apply the per-column rules ('per_column' rules)"
    ),
)
@click.option(
    "-sol",
    "-no-solve-dtypes",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not check the dtypes of the columns ('solve_dtypes' rule)"
    ),
)
@click.option(
    "-tim",
    "-no-time-format",
    required=False,
    is_flag=True,
    default=False,
    help=(
        "[YAML] Do not clean the formatting of the time/date ('time_format' rule)"
    ),
)
@click.option(
#parser.add_argument(
    "-v",
    "--verbose",
    required=False,
    is_flag=True,
    help=(
        "Show the rules and other info about encountered issue "
        "while cleaning."
    ),
)
@click.version_option(__version__, prog_name="metadata_clean")

def run_cleaning(
    r_yaml_file,
    m_metadata_file,
    nan_value,
    o_metadata_file,
    sample_id,
    verbose
):
    """
    Perform the cleaning of metadata on command line.
    """
    print(sample_id)
    rules, na_value, nan_value_usr, sampleID_cols = parse_yaml_file(
        r_yaml_file,
        verbose
    )

    # override sample IDs columns
    if sample_id:
        sampleID_cols = sample_id

    # override default NaN
    if nan_value:
        nan_value_user = nan_value

    metadata_pd = parse_metadata_files(
        sampleID_cols,
        m_metadata_file,
        False # do not do dummy by default
    )

    clean_metadata_fps = metadata_clean(
        rules,
        nan_value,
        nan_value_user,
        sampleID_cols,
        metadata_pd,
        m_metadata_file,
        o_metadata_file,
        verbose
    )

    print("Output(s) of metadata_cleaning:")
    print('\n'.join(clean_metadata_fps))

if __name__ == "__main__":
    run_cleaning()
