# A Fistful of Links

A Fistful of Links is a weekly newsletter about leadership, technology and books. This is main repository, containing Hugo website sources.

## Initial setup

This repository contains git submodules for theme and live website code. To pull them in, you need to pass `--recurse-submodules` flag during initial clone:

```
git clone --recurse-submodules git@github.com:AFistfulOfLinks/afistfuloflinks.git
```

You need [Hugo](https://gohugo.io/) to build website.

While not strictly necessary, this repository also contains Python tools for easier content authoring. To use them, you need [Python 3](https://www.python.org/) and some external modules. The easiest way is creating new virtual environment:

```
python3 -m venv ~/.virtualenvs/afistfuloflinks/
source ~/.virtualenvs/afistfuloflinks/bin/activate
pip install -r tools/requirements.txt
```

When working on theme, it's recommended to add upstream repository as new remote, to make it easy to pull in upstream changes to our fork:

```
cd themes/hugo-vitae-afol
git remote add upstream https://github.com/dataCobra/hugo-vitae.git
```

## Managing content

There are two types of content: posts (editions) and links. Posts are ordered collections of links. Posts are timestamped, while links are tagged.

### Adding new post

```
hugo new posts/YYYY-MM-DD.md
```

Example:

```
$ hugo new posts/2020-01-06.md
/home/afistfuloflinks/content/posts/2020-01-06.md created
```

You need to set `year` and `edition` variables in new post, and add 5 links. Links are identified by their file name without `.md` suffix. See `content/posts/2020-07-27.md` for example.

### Adding new link

Links file names must be SHA256 sum (hash) of link URL. `add-link.py` tool relieves you from remembering this detail - see **Tools** below.

```
$ echo -n 'https://afistfuloflinks.github.io/' |sha256sum
1150bcde7e13bc24b65dfa84a3b563a62c9e2ffc0cc844956c783b95adde9015  -
$ hugo new links/1150bcde7e13bc24b65dfa84a3b563a62c9e2ffc0cc844956c783b95adde9015.md
/home/afistfuloflinks/content/links/1150bcde7e13bc24b65dfa84a3b563a62c9e2ffc0cc844956c783b95adde9015.md created
```

Or as single command:
```
$ hugo new links/$(echo -n 'https://afistfuloflinks.github.io/' |sha256sum  | cut -d ' ' -f 1).md
```

All links must have `source_url`, `title`, `author` and `tags` variables set. `tags` contains list of strings.

`submitter` field is optional and must be set when link is submitted by person outside of newsletter editors. It's complex field containing name and website of submitter (historically, website was link to submitter page on intranet). If there is no submitter, field must be removed.

All links must contain excerpt (lead, sneak peek) from linked article below Hugo's front matter. You can use markdown formatting.

### Building website for testing

When building website, you probably want to pass `-F`, `--buildFuture` flag to `hugo` - otherwise, new edition will not be displayed.

```
hugo serve -F
```

## Tools

### lint

Checks content source for correctness. It's automatically run on Github for all new pull requests.

```
./tools/lint.py
```

You can pass `-r`, `--rules` option to run only specified checks. Argument to that option must be comma-separated list of checks. Use `--list-rules` to see available values.

### add-link

Adds new link, and optionally adds this link to specified post.

```
./tools/add-link.py
./tools/add-link.py 'https://afistfuloflinks.github.io/'
./tools/add-link.py --post 2020-01-06.md 'https://afistfuloflinks.github.io/'
./tools/add-link.py --title 'A Fistful of Links' --author 'Og Maciel, Mirek Długosz' --tags 'newsletter' 'https://afistfuloflinks.github.io/'
```

Field values can be passed in during command invocation. When not set, tool will ask for fields value. All fields except URL are optional - just press Enter to move to next field. You can also press Ctrl + D to skip all remaining fields. If submitter is to be added, both name and url must be specified.

`--post` value must be file name of existing post, or absolute path to existing file.

This tool manages only metadata (front matter). You still need to add link excerpt by editing the file.

### edition-num-for-date

Tells edition number for specified date. Support unlimited number of arguments.

```
./tools/edition-num-for-date.py 2020-01-06 2020-01-13
./tools/edition-num-for-date.py 01/06/2020 01.06.2020 01062020
./tools/edition-num-for-date.py content/posts/2020-01-06.md
./tools/edition-num-for-date.py -w content/posts/2020-01-06.md
```

Date segments can be delimited using `-`, `.`, `/` or nothing at all. When year is the last component, order of day and month is determined using system locale - if locale contains `_US`, it is assumed that month is specified first, and day second (`%m-%d-%Y`). Otherwise, day is assumed to be first (`%d-%m-%Y`).

Argument can be path to file, but that file must exist. Date will be read from file name.

Optional `-w`/`--write` flag can be used to automatically set post metadata to value calculated by tool. Obviously that applies only to arguments that are paths to files.

### unclaimed-links

Lists links that exist in source, but are not part of any post (edition).

```
./tools/unclaimed-links.py
```
