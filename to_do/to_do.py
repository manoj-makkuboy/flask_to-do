import os
import sys
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Response
import logging
import json


app = Flask(__name__)
app.config.from_object(__name__)  # loading config from this same file, to_do.py
 # Load default config and override config from an environment variable
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

@app.route('/sync', methods = ['GET'])
def show_entries():
	db = get_db()
	cur = db.execute('select task_id,item_content, is_done from entries order by task_id asc')
	entries = cur.fetchall()
	json_array = []
	for entry in entries:
		json_array.append([x for x in entry])
	print(Response, file=sys.stderr)
	return Response(json.dumps(json_array), mimetype='json/application') 
#	return Response('test response')	

@app.route('/add', methods = ['POST'])
def add_entry():
	recievedJSON = request.json
	db = get_db()
	db.execute('insert into entries (item_content, is_done) values (?, ?)', [recievedJSON[0], recievedJSON[1]])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))


@app.route('/done/<int:task_id>/<int:is_done>')
def update_status(task_id,is_done):
	db = get_db()
	logging.warning('task_id : ',task_id)	
	logging.warning('is_done : ',is_done)	

	if is_done == 0:
		is_done = 1
	else: 
		is_done = 0

	new_value = is_done

	db.execute('update entries set (is_done) = (?) where task_id=?',[new_value , task_id])

	db.commit()
	flash('update successful')
	return redirect(url_for('show_entries'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
	db = get_db()
	
	db.execute('delete from entries where task_id = ?',[task_id])
	db.commit()
	return redirect(url_for('show_entries'))
