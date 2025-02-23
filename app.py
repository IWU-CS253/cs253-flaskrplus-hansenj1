# -*- coding: utf-8 -*-
"""
    Flaskr plus
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def show_entries():
    """Displays all entries from the database or filters them by category."""
    db = get_db()

    #get list of categories, repeats are a no no
    cur = db.execute('select distinct category from entries')
    categories = cur.fetchall()

    #if a category is selected, filter by that category
    selected_category = request.args.get('category')
    if selected_category:
        cur = db.execute(
            'select id, title, text, category from entries where category = ? order by id desc',  #make sure id is selected
            [selected_category]
        )
        entries = cur.fetchall()
    else:
        #otherwise, show all
        cur = db.execute('select id, title, text, category from entries order by id desc')
        entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, categories=categories, selected_category=selected_category)

@app.route('/add', methods=['POST'])
def add_entry():
    """Adds a new post to the database with a user-defined category."""
    db = get_db()
    db.execute(
        'insert into entries (title, text, category) values (?, ?, ?)',  #modified to show category
        [request.form['title'], request.form['text'], request.form['category']]
    )
    db.commit()
    flash('New entry was successfully posted!')
    return redirect(url_for('show_entries'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    """Deletes the post with the given id from the database."""
    db = get_db()
    db.execute('delete from entries where id = (?)', [id])
    db.commit()
    flash('The post was successfully deleted.')
    return redirect(url_for('show_entries'))
