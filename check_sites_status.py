#! /usr/bin/env python

import time
import psycopg2
from config import config
import pycurl
import datetime
import smtplib
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from multiprocessing import Pool

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600 + (days * 24)
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds
	
def select_urls():
	params = config()
	conn_sql = psycopg2.connect(**params)
	cur = conn_sql.cursor()
	query = "SELECT hostname FROM sites_full WHERE online = %s"
	data = ('true',)
	cur.execute(query, data)
	result_set = list(cur.fetchall())
	cur.close()
	conn_sql.close()
	return result_set

def curlhttp(hostname):
	body = ""
	mDOWN = ' is Down'
	try:
		hostname = str(''.join(hostname))
		#print hostname
		#sys.stdout.flush()
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, 'http://'+hostname)
		curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36')
		curl.setopt(pycurl.FOLLOWLOCATION, 1)
		curl.setopt(pycurl.NOBODY, True)
		curl.setopt(pycurl.SSL_VERIFYPEER, 0)
		curl.perform()

		if curl.getinfo(pycurl.HTTP_CODE) >=400:
			body += hostname + '\n'
			body += "    status code: %s" % curl.getinfo(pycurl.HTTP_CODE) + '\n'
			body += 'Down since: ' + str(datetime.datetime.now()) + '\n\n'
			startTime = str(datetime.datetime.now())
			send_mail(body, hostname, mDOWN)
			query = "UPDATE sites_full SET online = %s, down_since = %s where HOSTNAME = %s"
			data = ('False', startTime, hostname)
			params = config()
			conn_sql = psycopg2.connect(**params)
			cur = conn_sql.cursor()
			cur.execute(query, data)
			conn_sql.commit()
			cur.close()
			conn_sql.close()
	except pycurl.error, error:
		errno, errstr = error
		body += hostname + '\n'
		body += str('Error: ') + str(errstr) + '\n'
		body += 'Down since: ' + str(datetime.datetime.now()) + '\n\n'
		startTime = str(datetime.datetime.now())
		send_mail(body, hostname, mDOWN)
		query = "UPDATE sites_full SET online = %s, down_since = %s where HOSTNAME = %s"
		data = ('False', startTime, hostname)
		params = config()
		conn_sql = psycopg2.connect(**params)
		cur = conn_sql.cursor()
		cur.execute(query, data)
		conn_sql.commit()
		cur.close()
		conn_sql.close()
		pass
	return body

def send_mail(b, s, msgS):
	f = open("email_settings.txt")
	for line in f:
		fields = line.strip().split()
	server = smtplib.SMTP(fields[1], 25)
	fromaddr = fields[3]
	toaddr = fields[5]
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = s + msgS
	msg.attach(MIMEText(b, 'plain'))
	server.ehlo()
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)

if __name__ == '__main__':
	urls = select_urls()
	now = datetime.datetime.now()
	pool = Pool(8)
	results = pool.map(curlhttp, urls)
	pool.close() 
	pool.join()
	a = datetime.datetime.now() - now
	hours, minutes, seconds = convert_timedelta(a)
	print 'Total Time Taken: ' + '{} hours, {} minutes, {} seconds.'.format(hours, minutes, seconds)
	