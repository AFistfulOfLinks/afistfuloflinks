#!/usr/bin/env python

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
            metadata = self._parse_file_metadata(path)
            self._content[key] = metadata
            return metadata

    @property
    def links_with_metadata(self):
        return {path: self.get_metadata(path)
                for path in self.links}

    @property
    def posts_with_metadata(self):
        return {path: self.get_metadata(path)
                for path in self.posts}

    def _parse_file_metadata(self, fileobj):
        with open(fileobj) as fh:
            front_matter = fh.read()
        begin = 3
        end = front_matter.index('---', begin)
        front_matter = front_matter[begin:end]
        metadata = yaml.safe_load(front_matter)
        return metadata
