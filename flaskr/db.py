#flask tutorial, Define and Access the Database, https://flask.palletsprojects.com/en/3.0.x/tutorial/database/
import sqlite3

import click
from flask import current_app, g

import csv

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

#create: flaskr/schema.sql

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    csv_file = 'tcc_ceds_music.csv'

    # Insert data into the 'song' table
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            columns = ', '.join(['number', 'artist_name', 'track_name', 'release_date', 'genre', 'lyrics'])
            values = ', '.join(['?' for _ in row])
            query = f"INSERT INTO song ({columns}) VALUES ({values});"
            db.execute(query, tuple(row.values()))

    db.commit()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
# flask tutorial, end of Define and Access the Database