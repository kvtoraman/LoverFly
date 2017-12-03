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

name = raw_input("Enter name of katalk user: ")
date = raw_input("Enter date (e.g. 2017-01-01: ")

hour_count = [[0 for i in range(24)],[0 for i in range(24)]]

file_cnt = 0

for fname in os.listdir('./24data/'+name):
	if ("hourly" in fname):
		period = 0
		file_cnt += 1
		firstline = True
		for line in open('./24data/'+name+'/'+fname):
			if firstline:
				firstline = False
				continue
			line = line.strip()
			line = line.split()
			a = line[0].split('-')
			b = date.split('-')
			if period == 0 and a[0].strip() == b[0].strip() and int(a[1].strip()) >= int(b[1].strip()) and int(a[2].strip()) >= int(b[2].strip()):
				period = 1
				print line
			hour_count[period][int(line[2])] += int(line[4])

print hour_count
print file_cnt

res = open('./24result/' + name + '_24hour.txt','w')
print >> res, "time\tcount"
print >> res, "Before"
for i in range(24):
	print >> res, str(i)+"\t"+str(hour_count[0][i])
print >> res, ""
print >> res, "After"
for i in range(24):
	print >> res, str(i)+"\t"+str(hour_count[1][i])

res.close()
