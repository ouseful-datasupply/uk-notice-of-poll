from setuptools import setup

setup(
    name="notice-of-poll",
    version='0.0.1',
    packages=['notice_of_poll'],
    install_requires=[
        'Click',
        'requests',
        'lxml',
        'scraperwiki'
    ],
    entry_points='''
        [console_scripts]
        pollscrape=notice_of_poll.cli:pdfscrape
    ''',
)