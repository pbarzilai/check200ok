#! /usr/bin/env python

import time
import psycopg2
from config import config
import requests
import datetime
import smtplib
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

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
	query = "SELECT hostname FROM sites_full WHERE online = %s AND check_status = %s ORDER BY hostname"
	data = ('true','true')
	cur.execute(query, data)
	result_set = list(cur.fetchall())
	cur.close()
	conn_sql.close()
	#return result_set
	curlhttp(result_set)

def curlhttp(hostname):
	#print hostname
	for site in hostname:
		try:
			#print site
			body = ""
			#mDOWN = ' is Down'
			mDOWN = ''
			#s = requests.session()
			#s.config['keep_alive'] = False
			headers = {}
			headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
			site = str(''.join(site))
			#resp = {}
			resp = requests.get('http://'+site, timeout=(2, 4), headers=headers)
			if resp.status_code >=400:
				body += site + '\n'
				body += "    status code: %s" % resp.status_code + '\n'
				body += 'Down since: ' + str(datetime.datetime.now()) + '\n\n'
				content = ""
				content = resp.text.encode('utf-8')
				startTime = str(datetime.datetime.now())
				send_mail(body, content, site, mDOWN)
				resp.close()
				#resp.text = ""
				query = "UPDATE sites_full SET online = %s, down_since = %s where HOSTNAME = %s"
				data = ('False', startTime, site)
				params = config()
				conn_sql = psycopg2.connect(**params)
				cur = conn_sql.cursor()
				cur.execute(query, data)
				conn_sql.commit()
				cur.close()
				conn_sql.close()
		except requests.exceptions.Timeout, error:
			body += site + '\n'
			body += str('Error: ') + str(error) + '\n'
			#body += 'Down since: ' + str(datetime.datetime.now()) + '\n\n'
			content = ""
			mERROR = " - Timeout ERROR"
			#content = resp.text.encode('utf-8')
			startTime = str(datetime.datetime.now())
			send_mail(body, content, site, mERROR)
			resp.close()
			#resp.text = ""
			#query = "UPDATE sites_full SET online = %s, down_since = %s where HOSTNAME = %s"
			#data = ('False', startTime, site)
			#params = config()
			#conn_sql = psycopg2.connect(**params)
			#cur = conn_sql.cursor()
			#cur.execute(query, data)
			#conn_sql.commit()
			#cur.close()
			#conn_sql.close()
			continue
		except requests.exceptions.ConnectionError, error2:
			continue
		except requests.exceptions.RequestException, error3:
			body += site + '\n'
			body += str('Error: ') + str(error3) + '\n'
			#body += 'Down since: ' + str(datetime.datetime.now()) + '\n\n'
			content = ""
			mERROR = " - Other ERROR"
			#content = resp.text.encode('utf-8')
			startTime = str(datetime.datetime.now())
			send_mail(body, content, site, mERROR)
			resp.close()
			#resp.text = ""
			#query = "UPDATE sites_full SET online = %s, down_since = %s where HOSTNAME = %s"
			#data = ('False', startTime, site)
			#params = config()
			#conn_sql = psycopg2.connect(**params)
			#cur = conn_sql.cursor()
			#cur.execute(query, data)
			#conn_sql.commit()
			#cur.close()
			#conn_sql.close()
			continue
		except ValueError:
			print site + ": " + "ValueError"
		resp.close()
		#return body

def send_mail(b, c, s, msgS):
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
	msg.attach(MIMEText(c, 'html'))
	server.ehlo()
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)

if __name__ == '__main__':
	now = datetime.datetime.now()
	urls = select_urls()
	a = datetime.datetime.now() - now
	hours, minutes, seconds = convert_timedelta(a)
	print 'Total Time Taken: ' + '{} hours, {} minutes, {} seconds.'.format(hours, minutes, seconds)
	
