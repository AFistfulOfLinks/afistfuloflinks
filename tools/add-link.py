#!/usr/bin/env python

import hashlib
from pathlib import Path
from tempfile import mkstemp

import click

from helpers import HugoContent


@click.command()
@click.option(
    '--post', '-p',
    help="Add URL to this post (YYYY-MM-DD.md or absolute path)"
)
@click.option(
    '--title', '-t',
    help="Title of article"
)
@click.option(
    '--author', '-a',
    help="Author of article"
)
@click.option(
    '--submitter.name', 'submitter_name',
    help="Submitter of article - name"
)
@click.option(
    '--submitter.url', 'submitter_url',
    help="Submitter of article - url"
)
@click.option(
    '--tags', '-T',
    help="Tags of article (comma-separated)"
)
@click.argument('url', nargs=1, required=False)
def main(post, title, author, submitter_name, submitter_url, tags, url):
    content_manager = HugoContent()
    new_metadata = {
        "source_url": url,
        "title": title,
        "author": author,
        "submitter.name": submitter_name,
        "submitter.url": submitter_url,
        "tags": tags,
    }

    for key, value in new_metadata.items():
        if value:
            continue
        default_value = None if key == 'source_url' else ''
        try:
            new_value = click.prompt(key, default=default_value, show_default=False)
            new_metadata[key] = new_value
        except click.Abort:
            print()
            break

    if new_metadata['submitter.name'] and new_metadata['submitter.url']:
        new_metadata['submitter'] = {
            'name': new_metadata['submitter.name'],
            'url': new_metadata['submitter.url'],
        }
    new_metadata.pop('submitter.name')
    new_metadata.pop('submitter.url')

    try:
        new_tags = [tag.strip() for tag in new_metadata['tags'].split(',')]
    except AttributeError:
        new_tags = []
    new_metadata['tags'] = new_tags

    url_hash = hashlib.sha256(new_metadata['source_url'].encode('UTF-8')).hexdigest()

    new_file = Path(__file__).joinpath(f"../../content/links/{url_hash}.md").resolve()
    if new_file.exists():
        _, new_file = mkstemp(suffix='.md', prefix='afollink-')
        new_file = Path(new_file)
        print(f"{url_hash}.md already exists")

    content_manager.set_metadata(new_file, new_metadata)
    print(f"Saved link as {new_file}")

    if post and url_hash == new_file.stem:
        post = Path(post)
        if not post.is_absolute():
            post = Path(__file__).joinpath(f"../../content/posts/{post}").resolve()
        post_metadata = content_manager.get_metadata(post)
        post_links = [link for link in post_metadata['links'] if link]
        post_links.append(url_hash)
        post_metadata['links'] = post_links
        content_manager.set_metadata(post, post_metadata)
        print(f"Added link to {post}")


if __name__ == "__main__":
    main()
