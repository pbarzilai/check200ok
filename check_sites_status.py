#! /usr/bin/env python

import time
import psycopg2
from config import config
import pycurl
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def check_all():
	params = config()
	conn_sql = psycopg2.connect(**params)
	cur = conn_sql.cursor()
	cur.execute('SELECT hostname FROM sites_full order by id')
	#cur.execute('SELECT hostname FROM sites_full where id = 26')
	for hostname in cur:
		now = datetime.datetime.now()
		body = ""
		try:
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
				startTime = datetime.datetime.now()
				#send_mail(body, hostname, ' is Down')
				query = "UPDATE sites_full SET online = B'0' WHERE HOSTNAME = %s"
				data = (hostname)
				cur.execute(query, data)
				conn_sql.commit()
				time.sleep(5)
				body = ''
		except pycurl.error, error:
			errno, errstr = error
			body += hostname + '\n'
			body += str('Error: ') + str(errstr) + '\n'
			body += 'Down since: ' + str(datetime.datetime.now()) + '\n\n'
			startTime = datetime.datetime.now()
			#send_mail(body, hostname, ' is Down')
			query = "UPDATE sites_full SET online = B'0' WHERE HOSTNAME = %s"
			data = (hostname)
			cur.execute(query, data)
			conn_sql.commit()
			time.sleep(5)
			body = ''
			continue
	cur.close()
	conn_sql.close()
	#f = open("log.txt", 'a')
	#f.write(now.strftime("%Y-%m-%d %H:%M") + ' Total Time Taken: ' + str(datetime.datetime.now() - now) + '\n')
	#f.close()
	

def check_again():
	params = config()
	conn_sql = psycopg2.connect(**params)
	cur = conn_sql.cursor()
	cur.execute('SELECT hostname FROM sites_full ORDER BY id WHERE online = 0')
	if cur >0:
		for hostname in cur:
			time.sleep(30)
			bodyA = ""
			try:
				curl = pycurl.Curl()
				curl.setopt(pycurl.URL, 'http://'+hostname)
				curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36')
				curl.setopt(pycurl.FOLLOWLOCATION, 1)
				curl.setopt(pycurl.NOBODY, True)
				curl.setopt(pycurl.SSL_VERIFYPEER, 0)
				curl.perform()

				if curl.getinfo(pycurl.HTTP_CODE) <400:
					bodyA += hostname + '\n'
					bodyA += "    status code: %s" % curl.getinfo(pycurl.HTTP_CODE) + '\n'
					bodyA += 'Up since: ' + str(datetime.datetime.now()) + '\n'
					send_mail(bodyA, hostname, ' is now Up')
					query = "UPDATE sites_full SET online = B'1' WHERE HOSTNAME = %s"
					data = (hostname)
					cur.execute(query, data)
					conn_sql.commit()
			except pycurl.error, error:
				continue
			cur.execute('SELECT hostname FROM sites_full ORDER BY id WHERE online = 0')
			if cur >0:
				continue
			else:
				break
	#else:
		#return
	cur.close()
	conn_sql.close()

def send_mail(b, s, msgS):
	server = smtplib.SMTP('192.168.*.*', 25)
	fromaddr = "*@*.com"
	toaddr = "*@*.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = s + msgS
	msg.attach(MIMEText(b, 'plain'))
	server.ehlo()
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)

def main():
	check_all()
	check_again()
	

if __name__ == "__main__":
	main()
