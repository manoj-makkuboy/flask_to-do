import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import logging

app = Flask(__name__)
app.config.from_object(__name__)  # loading config from this same file, to_do.py
app.config.update(dict(
	DATABASE = os.path.join(app.root_path, 'to_do.db'),
	SECRET_KEY = 'development key',
	USERNAME = 'admin',
	PASSWORD = 'default'
))
app.config.from_envvar('TODO_SETTINGS', silent = True)

def get_db():
	"""Opens a new db connection is if its not present in the current application context"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()


def connect_db():
	"""connects to the specific database"""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv


def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode = 'r') as f:
		db.cursor().executescript(f.read())
	db.commit()


@app.cli.command('initdb')
def initdb_command():
	""" Initializes the database."""
	init_db()
	print('Initialized the database.')

@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select item_content, is_done from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries = entries)

@app.route('/add', methods = ['POST'])
def add_entry():
	db = get_db()
	db.execute('insert into entries (item_content, is_done) values (?, ?)', [request.form['item_content'], request.form['is_done']])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))


@app.route('/update_is_done', methods = ['POST'])
def update_status():
	db = get_db()
	id_from_form = request.form['id_of_entry']
	new_value = int(request.form['checkbox'])
	
	logging.warning("the request is :", request.form['checkbox'])
	db.execute('update entries set (is_done) = (?) where item_content=?',[new_value , id_from_form])
	db.commit()
	flash('update successful')
	return redirect(url_for('show_entries'))
