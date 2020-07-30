#!/usr/bin/env python

import subprocess

from helpers import HugoContent


def main():
    page_content = HugoContent()
    claimed_links = [
        link
        for metadata in page_content.posts_with_metadata.values()
        for link in metadata['links']
    ]
    unclaimed_links = [
        link for link in page_content.links
        if link.stem not in claimed_links
    ]

    result = []

    for path in unclaimed_links:
        metadata = page_content.get_metadata(path)
        if 'submitter' in metadata:
            submitter = metadata['submitter']['name']
        else:
            process = subprocess.run(
                ['git', 'log', '-s', '-n1', '--format=%an', path.as_posix()],
                stdout=subprocess.PIPE
            )
            submitter = process.stdout.decode("UTF-8").strip()
            submitter = f"{submitter} (from git)"
        item = "{id}\nurl: {url}\ntitle: {title}\nsubmitter: {submitter}"
        item = item.format(
            id=path.stem, url=metadata['source_url'], title=metadata['title'],
            submitter=submitter
        )
        result.append(item)
    print("\n\n\n".join(result))


if __name__ == "__main__":
    main()
