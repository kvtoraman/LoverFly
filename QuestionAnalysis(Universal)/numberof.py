#!/usr/bin/env python
#-*-coding:utf-8-*-

#######################################################################
# CTP472 Social Media and Culture
# Author: Jaram Park (jaram.park@kaist.ac.kr) & Team 1: Kamil, Insu Kim, 
#######################################################################

import re, sys, os
import codecs
from datetime import datetime, date, time

import copy

parameter = raw_input("Enter YSL/KSH date(e.g. 2017. 5. 16) userID words: ")
parameter = parameter.split()
name = parameter[0]
date = parameter[1]+" "+parameter[2]+" "+parameter[3]
user = parameter[4]
if str(type(user)) == "<class 'bytes'>":
	user = user.decode('ascii')
elif str(type(user)) == "<type 'unicode'>":
	user = str(user)
else:
	user = user.decode('euc-kr')
user = user.encode('utf-8')

newfile = True
if os.path.isfile('./numberresult/' + name + '_number' + '.txt'):
	newfile = False
res = open('./numberresult/' + name + '_number' + '.txt','a')

words = parameter[5:]
for i in range (len(words)):
	try:
		if str(type(words[i])) == "<class 'bytes'>":
			words[i] = words[i].decode('ascii')
		elif str(type(words[i])) == "<type 'unicode'>":
			words[i] = str(words[i])
		else:
			words[i] = words[i].decode('euc-kr')
		words[i] = words[i].encode('utf-8')
	except:
		print "can't encode " + words[i] + "\t" + str(type(words[i]))


msg_count = [0,0]
word_count = [0,0]
word_percent = [0,0]

file_cnt = 0

for fname in os.listdir('./numberdata/'+name):
	p = 0
	for line in open('./numberdata/'+name+'/'+fname):
		if not ":" in line:
			continue

		a = line.split('.')
		b = date.split('.')
		if p == 0 and a[0].strip() == b[0].strip() and int(a[1].strip()) >= int(b[1].strip()) and int(a[2].strip()) >= int(b[2].strip()):
			p = 1

		a = line.split(':')
		b = a[1].split(',')
		try:
			if b[1].strip() == user:
				msg_count[p] += 1
				for word in words:
					if word in a[2]:
						word_count[p] += 1
						break
		except:
			continue

word_percent[0] = "{0:.2f}".format(float(word_count[0])/float(msg_count[0])*100)
word_percent[1] = "{0:.2f}".format(float(word_count[1])/float(msg_count[1])*100)

if newfile:
	print >> res, "Total messages before: " + str(msg_count[0]) + ", after: " + str(msg_count[1])
	print >> res, "words\tbefore#\tafter#\tbefore%\tafter%"

w = ""
for word in words:
	try:
		w += word.decode('utf-8').encode('euc-kr')
	except:
		continue
	w += ","
if word_count[0] > 0 or word_count[1] > 0:
	print >> res, w[:-1] + "\t" + str(word_count[0]) + "\t" + str(word_count[1])+ "\t" + str(word_percent[0])  + "\t" + str(word_percent[1])
	print ""
	print word_count
	print msg_count
	print word_percent
else:
	print "no usage at all"

res.close()
