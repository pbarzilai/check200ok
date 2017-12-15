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
	try:
		params = config()
		conn_sql = psycopg2.connect(**params)
		cur = conn_sql.cursor()
		query = "SELECT hostname FROM sites_full_test WHERE online = %s"
		data = ('true',)
		cur.execute(query, data)
		for hostname in cur:
			now = datetime.datetime.now()
			body = ""
			mDOWN = ' is Down'
			try:
				hostname = str(''.join(hostname))
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
					query = "UPDATE sites_full_test SET online = %s, down_since = %s where HOSTNAME = %s"
					data = ('False', startTime, hostname)
					conn_sql = psycopg2.connect(**params)
					cur = conn_sql.cursor()
					cur.execute(query, data)
					conn_sql.commit()
					cur.close()
					conn_sql.close()
					time.sleep(5)
					body = ''
			#except (psycopg2.ProgrammingError, IndexError, pycurl.error, error) as e:
			except pycurl.error, error:
				errno, errstr = error
				body += hostname + '\n'
				body += str('Error: ') + str(errstr) + '\n'
				body += 'Down since: ' + str(datetime.datetime.now()) + '\n\n'
				startTime = str(datetime.datetime.now())
				send_mail(body, hostname, mDOWN)
				query = "UPDATE sites_full_test SET online = %s, down_since = %s where HOSTNAME = %s"
				data = ('False', startTime, hostname)
				conn_sql = psycopg2.connect(**params)
				cur = conn_sql.cursor()
				cur.execute(query, data)
				conn_sql.commit()
				cur.close()
				conn_sql.close()
				time.sleep(5)
				body = ''
				continue
		cur.close()
		conn_sql.close()
		#f = open("log.txt", 'a')
		#f.write(now.strftime("%Y-%m-%d %H:%M") + ' Total Time Taken: ' + str(datetime.datetime.now() - now) + '\n')
		#f.close()
	except (psycopg2.ProgrammingError, IndexError, pycurl.error) as e:
		#print e
		pass
	
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

def main():
	check_all()

if __name__ == "__main__":
	main()
