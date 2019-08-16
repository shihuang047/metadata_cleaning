# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
import click
from metadata_cleaning.metadata_clean import (
    parse_yaml_file,
    parse_metadata_files,
    metadata_cleaner
)
from metadata_cleaning import __version__

@click.command()
@click.option(
    "-r",
    "-r-yaml-file",
    required=True,
    help="Rules file in yaml format."
)
@click.option(
    "-m",
    "--m-metadata-file",
    required=True,
    help="Metadata file"
)
@click.option(
    "-o",
    "--o-metadata-file",
    required=False,
    help="Output Metadata file name (Default: '*_clean.tsv'). " \
         "If 'na_value' from the yaml of option '-na' is not 'nan' " \
         "(i.e. the numpy's NaN), then another ouput file " \
         "will be generated, with '<previous_output>_<username>.tsv')"
)
@click.option(
    "-na",
    "--nan-value",
    required=False,
    help=(
        "Value to be use to replace the missing or violating entries. "
        "Violations are detected based on the rules of the yaml file."
    ),
)
@click.option(
    "-s",
    "--sample-id",
    required=False,
    multiple=True,
    help=(
        "List of columns names containing samples IDs. "
        "(or any other column(s) which may contain numeric "
        "and should not be interpreted as number."
    ),
)
@click.option(
    "-v",
    "--verbose",
    required=False,
    default=True,
    help="Show the rules and other info about encountered issue "
         "while cleaning."
)
@click.version_option(__version__, prog_name="metadata_clean")

def run_cleaning(
    r_yaml_file: str,
    m_metadata_file: str,
    nan_value: str,
    o_metadata_file: str,
    sample_id: list,
    verbose: bool
):
    """
    Perform the cleaning of metadata on command line.
    """
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
        m_metadata_file,
        False # do not do dummy by default
    )

    clean_metadata_fps = metadata_cleaner(
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
