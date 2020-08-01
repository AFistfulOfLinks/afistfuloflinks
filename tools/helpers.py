#!/usr/bin/env python

import io
from pathlib import Path

import yaml


class HugoContent():
    def __init__(self):
        self.links = self.__get_content_paths("links")
        self.posts = self.__get_content_paths("posts")
        self._content = {}

    def __get_content_paths(self, directory: str):
        dir_path = Path(__file__).joinpath(f"../../content/{directory}/").resolve()
        return list(dir_path.glob("*.md"))

    def get_metadata(self, path: Path):
        key = path.as_posix()
        try:
            return self._content[key]
        except KeyError:
            metadata, _ = self._parse_file(path)
            self._content[key] = metadata
            return metadata

    def set_metadata(self, path: Path, new_metadata):
        _, content = self._parse_file(path)

        front_matter = io.StringIO()
        yaml.safe_dump(
            new_metadata, front_matter, indent=4, sort_keys=False,
            allow_unicode=True
        )
        front_matter.seek(0)
        front_matter = front_matter.read()

        with open(path, 'w') as fh:
            fh.write('---\n')
            fh.write(front_matter)
            fh.write('---\n')
            if content:
                fh.write(content)

    @property
    def links_with_metadata(self):
        return {path: self.get_metadata(path)
                for path in self.links}

    @property
    def posts_with_metadata(self):
        return {path: self.get_metadata(path)
                for path in self.posts}

    def _parse_file(self, fileobj):
        try:
            with open(fileobj) as fh:
                file_content = fh.read()
                file_content.index('---')
        except (FileNotFoundError, ValueError):
            return {}, ''

        front_matter_begin = 3
        front_matter_end = file_content.index('---', front_matter_begin)

        front_matter = file_content[front_matter_begin:front_matter_end]
        metadata = yaml.safe_load(front_matter)

        content = file_content[front_matter_end + front_matter_begin:]
        return metadata, content.strip()
