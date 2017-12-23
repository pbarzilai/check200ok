#! /usr/bin/env python

import sys
import psycopg2
from config import config
from flask import Flask, jsonify, request, json

app = Flask(__name__)

@app.route('/offline_sites')
def get():
	params = config()
	conn_sql = psycopg2.connect(**params)
	cur = conn_sql.cursor()
	cur.execute("SELECT hostname, online FROM sites_full where online <> 'true' or online IS NULL order by hostname asc")
	r = [dict((cur.description[i][0], value) \
	for i, value in enumerate(row)) for row in cur.fetchall()]
	cur.close()
	conn_sql.close()
	return jsonify(r)
	
@app.route('/add_new_site', methods=['POST'])
def add_site():
	userinput = request.get_json()
	new_site = userinput.get("hostname")
	params = config()
	conn_sql = psycopg2.connect(**params)
	cur = conn_sql.cursor()
	query = "SELECT hostname FROM sites_full where hostname = %s"
	data = (new_site,)
	cur.execute(query, data)
	if cur.rowcount <> 0:
		return "Site already exists in Database"
	else:
		query = "insert into sites_full (hostname) values (%s)"
		data = (new_site,)
		cur.execute(query, data)
		conn_sql.commit()
		return "Site added successfully"
	cur.close()
	conn_sql.close()
		

if __name__ == '__main__':
	app.run(port='5002')
	
	 
	 
	 
	
	