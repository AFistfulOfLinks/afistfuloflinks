#!/usr/bin/env python

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
        item = "{id}\nurl: {url}\ntitle: {title}"
        item = item.format(
            id=path.stem, url=metadata['source_url'], title=metadata['title']
        )
        result.append(item)
    print("\n\n\n".join(result))


if __name__ == "__main__":
    main()
