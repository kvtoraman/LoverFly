#!/usr/bin/env python
#coding: utf-8
import re, sys, os
import codecs
import time
from datetime import datetime, date, time


##### Regular expression patterns for finding nonverbal cue
nonverbal = re.compile(ur"\(.*?\)+|[ㅋㅎㅠㅜ!?~\.]+|http(s)?[:]//|[=<>]?(?<![A-Za-z0-9])[;:]{1}[\^'-]?[\\\/)(\]\[}{DPpboO|]+|[=<>]?(?<![A-Za-z0-9])[;:]{1}[\^'-]?[0X#]\s|[>\^ㅜㅠㅡ@][ㅁㅇ0oO\._\-]*[<\^ㅜㅠㅡ@];*|[T\-oOXx+=;][\._]+[T\-+oOXx=;];*|(?<!\w)TT\s|\s[ha]+\s|[Ll][Oo][Ll]", re.UNICODE)
Users = {}
user_num = 1

dirName = '../../katalk_1to1'

folder_name = dirName.split('/')[-1]      ## For Linux (Mac)
#folder_name = dirName.split('\\\\')[-1]    ## For Windows
print 'Peer type: ',folder_name, 'Now analyzing'



f = codecs.open(folder_name+'_kakaochat_url_info_result.txt','w',encoding = 'utf-8')
f_each_emoticon = codecs.open(folder_name+'_kakaochat_info.txt','w',encoding='utf-8')
Time = {}
previous_line = ''
previous_text = ''
CP = False

CP_info = []

for fname in os.listdir(dirName):
	print 'Now analyzing: ', fname
	
	for line in open(dirName+'/'+fname):  ## For Linux (Mac)
#	for line in open(dirName+'\\\\'+fname): ## For Windows
		line = line.strip()

		if ':' in line:
			if ',' not in line:
				continue
			talk = line.split(':')	
			try:
				text = ''.join(talk[2:])
				wc = len(text.split())
				if wc==0: 
					continue
				info = (talk[0]+':'+talk[1]).split(',')
				time = info[0]
				try:
					user = info[1]
				except:
					continue
				uid = 'user'+str(user_num)
				if user not in Users:
					Users[user] = uid
					user_num+=1

			except Exception, e:
				continue
			
			day_list = time.split()
			previous_line = line	
			year = day_list[0][0:4]
			month = day_list[1].split('월')[0]
			day = day_list[2].split('일')[0]
		
			try:
				hour = 	day_list[4].split(':')[0]
				minute = day_list[4].split(':')[1]

				if '오후' in time:
					if hour!='12':
						hour =  str(int(hour)+12)
				else:
					if hour=='12':
						hour = '0'

			except Exception, e:
				print e
				continue

			try:
				time_info = datetime(int(year),int(month),int(day),int(hour),int(minute))
				time = time_info.strftime("%Y-%m-%d %H:%M")
				date = time_info.strftime("%Y-%m-%d\t%a")
					
			except Exception, e:
				print e, hour
				
	
			text = unicode(text, 'utf-8')
			urls = []
			text_list  = []
			cues = re.finditer(nonverbal, text)
			cue_str = []
			emo_num =1 
			while True:
				cue_char =''
				try:
					cue_char = cues.next().group(0)
					cue_str.append(cue_char)
					emo_num+=1
				except Exception, e:
					break
			if 'http' in text:
				text_list = text.split()
			for i in range(0,len(text_list)):
				if 'http' in text_list[i]:
					urls.append(text_list[i])
						
			url_num =1 
			for url in urls:
				try:
					f_each_emoticon.write(time+'\t'+Users[user]+'\t'+str(len(line))+'\t'+str(wc)+'\t'+str(url_num)+'\t'+url+'\n')
					url_num+=1
				except Exception, e:
					break
			f.write(time+'\t'+Users[user]+'\t'+str(len(line))+'\t'+str(wc)+'\t'+str(len(cue_str))+'\t'+str(len(urls))+'\t'+'\t'.join(urls)+'\n')


			if date not in Time:
				Time[date] = {}
			if hour not in Time[date]:
				Time[date][hour] = {}
				
			if uid not in Time[date][hour]:
				Time[date][hour][uid] = {'num':1, 'byte':len(line),'wc':wc,'url':len(urls),'CP_info':[]}
			else:
				Time[date][hour][uid]['num']+=1
				Time[date][hour][uid]['byte']+=len(line)
				Time[date][hour][uid]['wc']+=wc
				Time[date][hour][uid]['url']+=len(urls)
				
			
for u in Users:
	print u, Users[u]


f = open(folder_name+'_hourly_kakaochat_conversation_freq.txt','w')
f_daily = open(folder_name+'_daily_kakaochat_conversation_freq.txt','w')

for date in Time:
	daily_num = 0
	daily_byte = 0
	daily_wc = 0
	daily_user = {}
	daily_url = 0
	for hour in Time[date]:
		hour_num = 0
		hour_byte = 0
		hour_wc = 0
		hour_url = 0
		for uid in Time[date][hour]:
			if uid not in daily_user:
				daily_user[uid] = ''
			daily_byte +=Time[date][hour][uid]['byte']
			daily_wc +=Time[date][hour][uid]['wc']
			daily_num+=	Time[date][hour][uid]['num']
			daily_url+=Time[date][hour][uid]['url']
			hour_num += Time[date][hour][uid]['num']
			hour_byte += Time[date][hour][uid]['byte']
			hour_wc += Time[date][hour][uid]['wc']
			hour_url += Time[date][hour][uid]['url']
		
		f.write(date+'\t'+hour+'\t'+str(len(Time[date][hour]))+'\t'+str(hour_num)+'\t'+str(hour_byte)+'\t'+str(hour_wc)+'\t'+str(hour_url)+'\n')
	f_daily.write(date+'\t'+str(len(daily_user))+'\t'+str(daily_num)+'\t'+str(daily_byte)+'\t'+str(daily_wc)+'\t'+str(daily_url)+'\n')

