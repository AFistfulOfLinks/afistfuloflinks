#!/usr/bin/env python

import hashlib

import click

from helpers import HugoContent


class RuleCheckFailedError(Exception):
    pass


class Rule():
    description = "Not provided by rule"

    def __init__(self, context: HugoContent):
        self.context = context

    def execute(self):
        pass

    def fail(self, msg):
        raise RuleCheckFailedError(msg)


class LinksNumber(Rule):
    description = "Are there 5 links in edition?"

    def execute(self):
        for path in self.context.posts:
            metadata = self.context.get_metadata(path)
            if 'links' not in metadata:
                self.fail(f"{path.name} is missing links metadata")
            links_number = len(metadata['links'])
            if links_number != 5:
                self.fail(f"{path.name} has wrong number of links")


class LinksAreUnique(Rule):
    description = "Are all links in edition unique?"

    def execute(self):
        for path in self.context.posts:
            metadata = self.context.get_metadata(path)
            if 'links' not in metadata:
                self.fail(f"{path.name} is missing links metadata")

            if len(metadata['links']) != len(set(metadata['links'])):
                self.fail(f"Duplicate links found in {path.name}")


class LinksExist(Rule):
    description = "Do all links actually exist in content directory?"

    def execute(self):
        links = [path.stem for path in self.context.links]
        for path in self.context.posts:
            metadata = self.context.get_metadata(path)
            if 'links' not in metadata:
                self.fail(f"{path.name} is missing links metadata")

            for post_link in metadata['links']:
                if post_link not in links:
                    msg = (
                        f"{path.name} contains link {post_link} "
                        f"that doesn't exist in links database"
                    )
                    self.fail(msg)


class EditionIdSet(Rule):
    description = "Are 'year' and 'edition' metadata set?"

    def execute(self):
        for path in self.context.posts:
            metadata = self.context.get_metadata(path)
            has_edition = metadata.get('edition')
            has_year = metadata.get('year')
            if not all([has_edition, has_year]):
                msg = f"{path.name} is missing 'year' and/or 'edition' metadata"
                self.fail(msg)


class NoDuplicateEditions(Rule):
    description = "Are 'year'/'edition' metadata values unique in all posts?"

    def execute(self):
        editions = {}
        for path, metadata in self.context.posts_with_metadata.items():
            this_edition = (metadata['year'], metadata['edition'])
            if this_edition in editions:
                msg = f"{path.name} contains the same edition id as {editions[this_edition].name}"
                self.fail(msg)
            editions[this_edition] = path


class RequiredLinksMetadata(Rule):
    description = "Do all links contain all required metadata?"

    def execute(self):
        for path in self.context.links:
            fields = ['source_url', 'title', 'author']

            link_metadata = self.context.get_metadata(path)

            if 'submitter' in link_metadata:
                for key in ['name', 'url']:
                    master_key = f'submitter.{key}'
                    link_metadata[master_key] = link_metadata['submitter'].get(key)
                    fields.append(master_key)

            for field in fields:
                try:
                    value = link_metadata.get(field).strip()
                except AttributeError:
                    value = ''
                if not value:
                    msg = f"{path.name} is missing '{field}'"
                    self.fail(msg)

            if 'tags' not in link_metadata:
                msg = f"{path.name} is missing 'tags'"
                self.fail(msg)

            tags = [tag for tag in link_metadata['tags'] if tag.strip()]
            if not tags:
                msg = f"{path.name} doesn't have valid tags"
                self.fail(msg)


class LinksFilename(Rule):
    description = "Are file names for link generated correctly?"

    def execute(self):
        for path in self.context.links:
            link_metadata = self.context.get_metadata(path)
            actual_hash = path.stem
            expected_hash = hashlib.sha256(link_metadata['source_url'].encode('UTF-8')).hexdigest()
            if expected_hash != actual_hash:
                msg = f"{path.name} should be named {expected_hash}.md"
                self.fail(msg)


class LinksHaveExcerpt(Rule):
    description = "Do all links contain excerpt?"

    def execute(self):
        for path in self.context.links:
            if not self.context.get_content(path):
                msg = f"{path.name} is missing excerpt"
                self.fail(msg)


@click.command()
@click.option(
    '--rules', '-r', 'rules_to_run',
    help="Comma-separated list of rules to run; see --list-rules"
)
@click.option(
    '--list-rules', is_flag=True,
    help="List available rules"
)
def main(rules_to_run, list_rules):
    if list_rules:
        availabe_rules = [
            f" - {cls.__name__} - {cls.description}"
            for cls in Rule.__subclasses__()
        ]
        availabe_rules = "\n".join(availabe_rules)
        click.echo(f"Available rules:\n{availabe_rules}")
        raise SystemExit(0)

    context = HugoContent()
    rules = []
    all_rule_names = []
    for cls in Rule.__subclasses__():
        rule = cls(context)
        rules.append(rule)
        all_rule_names.append(type(rule).__name__)

    if rules_to_run:
        rules_to_run = [
            name.strip() for name in rules_to_run.split(",")
        ]
    else:
        rules_to_run = all_rule_names

    exit_code = 0
    for rule in rules:
        rule_name = type(rule).__name__
        if rule_name not in rules_to_run:
            continue

        try:
            rule.execute()
        except RuleCheckFailedError as exp:
            click.echo(f"{rule_name} failed with message:\n{exp}\n")
            exit_code += 1
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
