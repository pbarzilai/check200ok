#! /usr/bin/env python

import psycopg2
from config import config
from flask import Flask, request
from flask_restful import Resource, Api
from flask import jsonify

app = Flask(__name__)
api = Api(app)

class Sites(Resource):
	def get(self):
		params = config()
		conn_sql = psycopg2.connect(**params)
		cur = conn_sql.cursor()
		query = "SELECT * FROM sites_full order by hostname asc"
		data = ('true',)
		cur.execute(query, data)
		r = [dict((cur.description[i][0], value) \
		for i, value in enumerate(row)) for row in cur.fetchall()]
		cur.close()
		conn_sql.close()
		return jsonify(r)

api.add_resource(Sites, '/sites') # Route_1

if __name__ == '__main__':
	app.run(port='5002')
	 
	 
	 
	
	