#!/usr/bin/env python

from pathlib import Path
import yaml


class DuplicateEditionError(Exception):
    pass


def parse_file_metadata(fileobj):
    with open(fileobj) as fh:
        front_matter = fh.read()
    begin = 3
    end = front_matter.index('---', begin)
    front_matter = front_matter[begin:end]
    metadata = yaml.safe_load(front_matter)
    return metadata


if __name__ == "__main__":
    editions = []
    for post in Path('content/posts/').glob('*.md'):
        metadata = parse_file_metadata(post)
        this_edition = (metadata['year'], metadata['edition'])
        if this_edition in editions:
            msg = (f"{post.name} contains duplicate edition id, "
                   f"year: {this_edition[0]}, edition: {this_edition[1]}")
            raise DuplicateEditionError(msg)
        editions.append(this_edition)
