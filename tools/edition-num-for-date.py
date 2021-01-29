#!/usr/bin/env python

from pathlib import Path

import click

from helpers import EditionNumber
from helpers import HugoContent


def set_edition_number_for_file(path, edition_number, context):
    metadata = context.get_metadata(path)
    edition_in_metadata = metadata['edition']
    if edition_in_metadata == edition_number:
        return
    metadata['edition'] = edition_number
    context.set_metadata(path, metadata)


@click.command()
@click.option(
    '--write/--no-write', '-w',
    default=False,
    help="Set calculated edition number in file metadata"
)
@click.argument('dates', nargs=-1)
def main(write, dates):
    if write:
        content_manager = HugoContent()

    for date in dates:
        p = Path(date).resolve()
        if p.exists():
            edition_number = EditionNumber.from_path(p)
            if write:
                set_edition_number_for_file(p, edition_number, content_manager)
        else:
            edition_number = EditionNumber.from_date(date)
        print(f"{date} is edition number: {edition_number}")


if __name__ == "__main__":
    main()
