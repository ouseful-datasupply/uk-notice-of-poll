import notice_of_poll.pdf_scraper as nop
import click

@click.command()
@click.option('--dbname', default='nop_data.db',  help='SQLite database name')
@click.argument('files', nargs=-1, type=click.Path())
def pdfscrape(dbname,files):
    click.echo('Using SQLite3 database: {}'.format(dbname))
    for fn in files:
        nop.get_nop_data(fn, dbname)