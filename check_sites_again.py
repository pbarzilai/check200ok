#! /usr/bin/env python

import time
import psycopg2
from config import config
import pycurl
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import filelock
import sys

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600 + (days * 24)
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds

def stop_if_already_running():
	lock = filelock.FileLock("lock.txt")
	lock.timeout = 2
	try:
		lock.acquire()
		check_again()
						
	except filelock.Timeout:
		print 'Script is already running.'
		pass
		
def check_again():
	while True:	
		try:
			params = config()
			conn_sql = psycopg2.connect(**params)
			cur = conn_sql.cursor()
			cur.execute('SELECT hostname FROM sites_full WHERE online = False')
			row = cur.fetchone()
			if row is None:
				break
			cur.execute('SELECT hostname FROM sites_full WHERE online = False')
			for hostname in cur:
				#print hostname
				time.sleep(1)
				bodyA = ""
				mUP = ' is now Up'
				try:
					hostname = str(''.join(hostname))
					#print hostname
					#sys.stdout.flush()
					curl = pycurl.Curl()
					curl.setopt(pycurl.URL, 'http://'+hostname)
					curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36')
					curl.setopt(pycurl.FOLLOWLOCATION, 1)
					curl.setopt(pycurl.CONNECTTIMEOUT, 20)
					curl.setopt(pycurl.NOBODY, True)
					curl.setopt(pycurl.SSL_VERIFYPEER, 0)
					curl.perform()

					if curl.getinfo(pycurl.HTTP_CODE) <400:
						query = "SELECT down_since FROM sites_full WHERE HOSTNAME = %s"
						data = (hostname,)
						cur.execute(query, data)
						data = cur.fetchone()
						downsince = data[0]
						bodyA += hostname + '\n'
						bodyA += "    status code: %s" % curl.getinfo(pycurl.HTTP_CODE) + '\n'
						a = datetime.datetime.now() - downsince
						hours, minutes, seconds = convert_timedelta(a)
						bodyA += 'Site was down for: ' + '{} hours, {} minutes, {} seconds.'.format(hours, minutes, seconds) + '\n'
						send_mail(bodyA, hostname, mUP)
						reset_down_since = None
						query = "UPDATE sites_full SET online = %s, down_since = %s WHERE HOSTNAME = %s"
						data = ('True', reset_down_since, hostname)
						cur.execute(query, data)
						conn_sql.commit()
				except pycurl.error, error:
					continue
			cur.close()
			conn_sql.close()
		except psycopg2.ProgrammingError:
			continue
		time.sleep(30)
					
	
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
	stop_if_already_running()
		
if __name__ == "__main__":
	main()
