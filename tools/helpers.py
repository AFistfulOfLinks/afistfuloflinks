#!/usr/bin/env python

import datetime
import io
import locale
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

    def get_data(self, path: Path):
        key = path.as_posix()
        try:
            return self._content[key]
        except KeyError:
            metadata, content = self._parse_file(path)
            data = {"metadata": metadata, "content": content}
            self._content[key] = data
            return data

    def get_metadata(self, path: Path):
        return self.get_data(path)['metadata']

    def get_content(self, path: Path):
        return self.get_data(path)['content']

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


class EditionNumber():
    _locale_strptime_format = None

    @classmethod
    def _get_locale_strptime_format(cls):
        if cls._locale_strptime_format is not None:
            return cls._locale_strptime_format

        locales = locale.getlocale(locale.LC_TIME)
        if locales[0] is None:
            locales = locale.getdefaultlocale()

        locale_strptime_format = '%d-%m-%Y'
        try:
            if locales[0].endswith('_US'):
                locale_strptime_format = '%m-%d-%Y'
        except AttributeError:
            pass

        cls._locale_strptime_format = locale_strptime_format
        return locale_strptime_format

    @classmethod
    def _parse_date_string(cls, date_string):
        delimiters = ['-', '.', '/', '']
        locale_strptime_format = cls._get_locale_strptime_format()
        for date_format in ("%Y-%m-%d", locale_strptime_format):
            for delimiter in delimiters:
                strptime_format = date_format.replace('-', delimiter)
                try:
                    date_obj = datetime.datetime.strptime(date_string, strptime_format)
                    return date_obj
                except ValueError:
                    pass

        raise ValueError(f"Could not figure out format of {date_string}")

    @classmethod
    def from_date(cls, date_string):
        date_obj = cls._parse_date_string(date_string)
        edition_number = int(date_obj.strftime("%W"))
        if edition_number == 0:
            previous_year = datetime.datetime(date_obj.year - 1, 12, 31)
            edition_number = int(previous_year.strftime("%W"))
        return edition_number

    @classmethod
    def from_path(cls, path):
        date_string = path.stem
        return cls.from_date(date_string)
