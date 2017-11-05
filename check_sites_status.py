#! /usr/bin/env python

import time
import pycurl
from termcolor import colored
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

SITES = open("sites.txt").read().splitlines()
SITESa = []

def check_all():
	f = open("sites.txt")
	SITES = f.read().splitlines()
	now = datetime.datetime.now()
	for site in SITES:
		body = ""
		try:
			curl = pycurl.Curl()
			curl.setopt(pycurl.URL, 'http://'+site)
			curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36')
			curl.setopt(pycurl.FOLLOWLOCATION, 1)
			curl.setopt(pycurl.NOBODY, True)
			curl.setopt(pycurl.SSL_VERIFYPEER, 0)
			curl.perform()

			if curl.getinfo(pycurl.HTTP_CODE) >=400:
				body += site + '\n'
				body += "    status code: %s" % curl.getinfo(pycurl.HTTP_CODE) + '\n'
				body += 'Down since: ' + str(datetime.now()) + '\n\n'
				startTime = datetime.now()
				send_down(body, site)
				SITESa.append(site)
				#
				f.close()
				f = open("sites.txt", 'w')
				SITES.pop(SITES.index(site))
				f.write('\n'.join(SITES))
				f.close()
				time.sleep(5)
				f = open("sites.txt")
				SITES = f.read().splitlines()
				#
				body = ''
		except pycurl.error, error:
			errno, errstr = error
			body += site + '\n'
			body += str('Error: ') + str(errstr) + '\n'
			body += 'Down since: ' + str(datetime.now()) + '\n\n'
			startTime = datetime.now()
			send_down(body, site)
			SITESa.append(site)
			#
			f.close()
			f = open("sites.txt", 'w')
			SITES.pop(SITES.index(site))
			f.write('\n'.join(SITES))
			f.close()
			time.sleep(5)
			f = open("sites.txt")
			SITES = f.read().splitlines()
			#
			body = ''
			continue
	f.close()
	fl = open("log.txt", 'a')
	fl.write(now.strftime("%Y-%m-%d %H:%M") + ' Total Time Taken: ' + str(datetime.datetime.now() - now) + '\n')
	fl.close()
	

def check_again():
	while len(SITESa) >0:
		for site in SITESa:
			time.sleep(30)
			bodyA = ""
			try:
				curl = pycurl.Curl()
				curl.setopt(pycurl.URL, 'http://'+site)
				curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36')
				curl.setopt(pycurl.FOLLOWLOCATION, 1)
				curl.setopt(pycurl.NOBODY, True)
				curl.setopt(pycurl.SSL_VERIFYPEER, 0)
				curl.perform()

				if curl.getinfo(pycurl.HTTP_CODE) <400:
					bodyA += site + '\n'
					bodyA += "    status code: %s" % curl.getinfo(pycurl.HTTP_CODE) + '\n'
					bodyA += 'Up since: ' + str(datetime.now()) + '\n'
					send_up(bodyA, site)
					SITESa.pop(SITESa.index(site))
					#
					f2 = open("sites.txt")
					SITES = f2.read().splitlines()
					f2.close()
					f2 = open("sites.txt", 'w')
					SITES.append(site)
					f2.write('\n'.join(SITES))
					f2.close()
					#
			except pycurl.error, error:
				continue

def send_up(b, s):
	server = smtplib.SMTP('192.168.*.*', 25)
	fromaddr = "do-not-reply@*.com"
	toaddr = "*@*.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = s + ' is now Up'
	msg.attach(MIMEText(b, 'plain'))
	server.ehlo()
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)

def send_down(b, s):
	server = smtplib.SMTP('192.168.*.*', 25)
	fromaddr = "do-not-reply@*.com"
	toaddr = "*@*.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = s + ' is Down'
	msg.attach(MIMEText(b, 'plain'))
	server.ehlo()
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)

def main():
	check_all()
	check_again()

if __name__ == "__main__":
	main()
