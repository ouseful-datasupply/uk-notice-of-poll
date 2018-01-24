# `uk-notice-of-poll`
Scraper tool for UK Notice of Poll PDFs.

Hacky tool in need of revision for scraping data out of UK election Notice of Poll PDFs.

This makes use of `pdftohtml` as supplied in the Linux [`poppler-utils`](https://launchpad.net/ubuntu/xenial/+package/poppler-utils) package.

It may be worth trying to migrate everything to use the Python [`pdfminer.six`](https://github.com/pdfminer/pdfminer.six) package or scrape everything more directly using the Python [`pdfquery`](https://github.com/jcushman/pdfquery) package.

In need of some maintenance to tidy things up...

## Installation

`pip install --upgrade git+https://github.com/ouseful-datasupply/uk-notice-of-poll.git`

Without dependencies:

`pip install --upgrade --no-deps git+https://github.com/ouseful-datasupply/uk-notice-of-poll.git`

## CLI

```
Usage: pollscrape [OPTIONS] [FILES]...

[FILES] Path to one or more Notice of Poll PDFs

Options:
  --dbname TEXT  SQLite database name
  --help         Show this message and exit.
```
