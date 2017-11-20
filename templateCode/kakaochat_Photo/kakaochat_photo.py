#!/usr/bin/env python
#coding: utf-8
import re, sys, os
import codecs
import time
from datetime import datetime, date, time


##### Regular expression patterns for finding nonverbal cue
nonverbal = re.compile(ur"\(.*?\)+|[ㅋㅎㅠㅜ!?~\.]+|http(s)?[:]//|[=<>]?(?<![A-Za-z0-9])[;:]{1}[\^'-]?[\\\/)(\]\[}{DPpboO|]+|[=<>]?(?<![A-Za-z0-9])[;:]{1}[\^'-]?[0X#]\s|[>\^ㅜㅠㅡ@][ㅁㅇ0oO\._\-]*[<\^ㅜㅠㅡ@];*|[T\-oOXx+=;][\._]+[T\-+oOXx=;];*|(?<!\w)TT\s|\s[ha]+\s|[Ll][Oo][Ll]", re.UNICODE)
Users = {'회원님':'user1'}
user_num = 2

dirName = '../../katalk_1to1'

folder_name = dirName.split('/')[-1]      ## For Linux (Mac)
#folder_name = dirName.split('\\\\')[-1]    ## For Windows
print 'Peer type: ',folder_name, 'Now analyzing'




f = codecs.open(folder_name+'_kakaochat_all_info_result.txt','w',encoding = 'utf-8')
f_each_emoticon = codecs.open(folder_name+'_kakaochat_emoticon.txt','w',encoding='utf-8')
f_each_url = codecs.open(folder_name+'_kakaochat_url.txt','w',encoding='utf-8')
f_each_photo = codecs.open(folder_name+'_kakaochat_photo.txt','w',encoding='utf-8')
Time = {}

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
					user = info[1].strip()
				except:
					continue
				if user not in Users:
					uid = 'user'+str(user_num)
					Users[user] = uid
					user_num+=1
				else:
					uid = Users[user]

			except Exception, e:
				continue
			
			day_list = time.split()
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
				date_time = time_info.strftime("%Y-%m-%d\t%H:%M\t%a")
					
			except Exception, e:
				print e, hour
				
	
			text = unicode(text, 'utf-8')
			photo_text = unicode('<사진>','utf-8')
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
					f_each_emoticon.write(date_time+'\t'+Users[user]+'\t'+str(len(text))+'\t'+str(wc)+'\t'+cue_char+'\n')
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
					f_each_url.write(date_time+'\t'+Users[user]+'\t'+str(len(text))+'\t'+str(wc)+'\t'+str(url_num)+'\t'+url+'\n')
					url_num+=1
				except Exception, e:
					break


			if date not in Time:
				Time[date] = {}
			if hour not in Time[date]:
				Time[date][hour] = {}
				
			if uid not in Time[date][hour]:
				Time[date][hour][uid] = {'num':1, 'byte':len(text),'wc':wc,'url':len(urls),'photo':0,'nonverbal':0}
			else:
				Time[date][hour][uid]['num']+=1
				Time[date][hour][uid]['byte']+=len(text)
				Time[date][hour][uid]['wc']+=wc
				Time[date][hour][uid]['url']+=len(urls)
				Time[date][hour][uid]['nonverbal']+=len(cue_str)

			if photo_text in text:
				Time[date][hour][uid]['photo']+=1
				f.write(time+'\t'+Users[user]+'\t'+'photo'+'\n')
				f_each_photo.write(date_time+'\t'+Users[user]+'\n')
			else:
				f.write(time+'\t'+Users[user]+'\t'+str(len(text))+'\t'+str(wc)+'\t'+str(len(cue_str))+'\t'+str(len(urls))+'\t'+'\t'.join(urls)+'\n')
for u in Users:
	print Users[u],u


f = open(folder_name+'_hourly_kakaochat_conversation_freq.txt','w')
f_daily = open(folder_name+'_daily_kakaochat_conversation_freq.txt','w')

for date in Time:
	daily_num = 0
	daily_byte = 0
	daily_wc = 0
	daily_user = {}
	daily_url = 0
	daily_photo = 0
	daily_nonverbal = 0
	for hour in Time[date]:
		hour_num = 0
		hour_byte = 0
		hour_wc = 0
		hour_url = 0
		hour_photo = 0
		hour_nonverbal = 0
		for uid in Time[date][hour]:
			if uid not in daily_user:
				daily_user[uid] = ''
			daily_byte +=Time[date][hour][uid]['byte']
			daily_wc +=Time[date][hour][uid]['wc']
			daily_num+=	Time[date][hour][uid]['num']
			daily_url+=Time[date][hour][uid]['url']
			daily_photo+=Time[date][hour][uid]['photo']
			daily_nonverbal+=Time[date][hour][uid]['nonverbal']
			hour_num += Time[date][hour][uid]['num']
			hour_byte += Time[date][hour][uid]['byte']
			hour_wc += Time[date][hour][uid]['wc']
			hour_url += Time[date][hour][uid]['url']
			hour_photo += Time[date][hour][uid]['photo']
			hour_nonverbal += Time[date][hour][uid]['nonverbal']
		
		f.write(date+'\t'+hour+'\t'+str(len(Time[date][hour]))+'\t'+str(hour_num)+'\t'+str(hour_byte)+'\t'+str(hour_wc)+'\t'+str(hour_nonverbal)+'\t'+str(hour_url)+'\t'+str(hour_photo)+'\n')
	f_daily.write(date+'\t'+str(len(daily_user))+'\t'+str(daily_num)+'\t'+str(daily_byte)+'\t'+str(daily_wc)+'\t'+str(daily_nonverbal)+'\t'+str(daily_url)+'\t'+str(daily_photo)+'\n')

