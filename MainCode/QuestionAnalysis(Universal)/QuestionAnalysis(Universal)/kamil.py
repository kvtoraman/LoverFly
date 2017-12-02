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

#reload(sys)
#sys.setdefaultencoding('utf-8')

Users = {}
user_num = 1


dirName = './data'   ######### Modify the address where you put your data
result_dirName ='./result'
result_dirName = result_dirName + '/'



last_message_time = datetime.now()
print last_message_time
time_diff=''

##Modifications

def strip_one(s):
    if s.endswith(" ") : s = s[:-1] #마지막이 " "임을 검사
    if s.startswith(" ") : s = s[1:] #첫번째가 " "임을 검사
    return s

#code to detect format
IPHONE = 1
ANDROID = 0
FORMAT = -1
month_splitter = '월'
day_splitter = '일'
print("Enter the name of kakaotalk ID you trying to analyze")
protagonist = raw_input()
inverseUsers = {}

#protagonist = protagonist.decode('ascii').encode('utf-8')
#protagonist = protagonist.decode('euc-kr')



if str(type(protagonist)) == "<class 'bytes'>":
    # only possible in Python 3
    protagonist = protagonist.decode('ascii')  # or  s = str(s)[2:-1]
elif str(type(protagonist)) == "<type 'unicode'>":
    # only possible in Python 2
    protagonist = str(protagonist)
else:
    protagonist = protagonist.decode('euc-kr')



protagonist = protagonist.encode('utf-8')


protagonist.strip()
def find_format(day_list):
        global FORMAT
        global  month_splitter
        global day_splitter

        if day_list[0][-1] == '.':
                FORMAT = IPHONE
                month_splitter = '.'
                day_splitter = '.'
                #result_dirName ='./result(iphone)'
        else:
                FORMAT = ANDROID
                month_splitter = '월'
                day_splitter = '일'
                #result_dirName ='./result(android)'





for fname in os.listdir(dirName):
	Daily = {}
	Hour = {}
	WeekDay = {}
	Time = {}
	response_rate=''
	previous_text=''

	ConvDuration = []

        
	
	r_rate = open(result_dirName + fname[:-4] + '_r_rate.txt','w')
		

	print 'Now analyzing: ', fname  ## input files
	FORMAT = -1
	user_found = 0
	previous_user = ''
	#print headers
	print >> r_rate, "user\tdata\tday\thour\ttime_diff"
	                        
	for line in open(dirName+'/'+fname):
	        line = line.strip()
	        
	        if ':' in line: 
	                talk = line.split(':')  
	                try:
	                        text = talk[2]
	                        
	                        info = (talk[0]+':'+talk[1]).split(',') # split information into time and speaker
	                        time = info[0]
	                        try:
	                                user = info[1]
	                                #user.strip()
	                        except:
	                                continue
	                        if user not in Users: #save speaker (it could be a peer or yourself)
	                                uid = 'user'+str(user_num)
	                                Users[user] = uid
	                                user_num+=1
	                                #inverseUsers[uid]=strip_one(user)
	                                #user=user.encode('utf-8')
	                                
	                                inverseUsers[uid]=user.strip()
	                except Exception, e:
	                        continue
	                
	                day_list = time.split()
	                if(FORMAT == -1):
	                        find_format(day_list)
	                year = day_list[0][0:4]
	                month = day_list[1].split(month_splitter)[0]
	                day = day_list[2].split(day_splitter)[0]
	                uid = Users[user]       
	                try:
	                        hour =  day_list[4].split(':')[0]
	                        minute = day_list[4].split(':')[1]

	                        if '오후' in time:
	                                if hour=='12':
	                                        continue
	                                hour =  str(int(hour)+12)
	                        else:
	                                if hour=='12':
	                                        hour = '0'
	                                day_time = hour

	                        if len(hour) < 2:
	                        	hour = "0" + hour
	                        day_time = hour+':'+minute
	                except Exception, e:
	                        print e
	                        continue
	                
	                try:
	                        time_info = datetime(int(year),int(month),int(day),int(hour),int(minute))
	                        time = time_info.strftime("%Y-%m-%d %H:%M") ## time information including hour and minute
	                        date = time_info.strftime("%Y-%m-%d\t%a") ## date information including weekday
	                                
	                except Exception, e:
	                        print e, hour
	                        time_info = 0


	                if date not in Time:
	                        Time[date] = {}
	                if hour not in Time[date]:
	                        Time[date][hour] = {}
	                                
	                if uid not in Time[date][hour]:
	                        Time[date][hour][uid] = {'num':1}
	                else:
	                        Time[date][hour][uid]['num']+=1

	                ####################################################
	                # calc duration of one conversation unit
	                ####################################################

	                current_user = uid
	                if previous_user=='': ## first line
	                        previous_user = current_user
	                        previous_text=text
	       
	                if current_user == previous_user:
	                        last_message_time = time_info
	                        previous_text=text
	                        previous_user = current_user
	                        
	                else:
	                        time_diff = time_info - last_message_time
	                        last_message_time = time_info
	                        
	                        
	                        

	                        if('?' in previous_text and inverseUsers[current_user] == protagonist):
	                        #if('?' in previous_text):
	                                #print >> r_rate, current_user, date+'\t'+hour+'\t'+str(len(Time[date][hour]))+" Question:"+previous_text+" Answer:"+text,'\t'+'response time: ',time_diff
	                                user_found = 1    
	                                print >> r_rate, current_user +'\t'+ str(date)+'\t'+ str(hour) + '\t' + str(time_diff)
	                        previous_text = text
	                        previous_user = current_user
	        elif line=='':
	                current_user  = ''
	                previous_user = ''

    	
	if(user_found):
		print "User found :",protagonist 
	else:
		print "User NOT found:", protagonist

	f = open(result_dirName + fname[:-4] + '_hourly_katalk_conversation_freq.txt','w')
	f_daily = open(result_dirName + fname[:-4] + '_daily_katalk_conversation_freq.txt','w')
	
	print >> f_daily, "date\tday\tusers#\tmessages#\tpercentage(%)"
	print >> f, "date\tday\thour\tusers#\tmessages#\tpercentage(%)"

	
	for _key in sorted(Time.keys()):
	        date = _key
	        daily_total_chat = 0
	       
	        daily_user = {}
	        daily_user_chat = 0
	        daily_total_chat = 0
	        
	        
	        for hour in sorted(Time[date].keys()):
	                hourly_user_chat = 0
	                hourly_total_chat = 0
	                hourly_user = {}
	                for uid in Time[date][hour]:
	                 
	                        if uid not in daily_user:
	                                hourly_user[uid] = ''
	                                daily_user[uid]=''
	                        if(inverseUsers[uid]==protagonist):
	                                daily_user_chat+=     Time[date][hour][uid]['num']
	                                hourly_user_chat += Time[date][hour][uid]['num']
	                                
	                        hourly_total_chat +=Time[date][hour][uid]['num']
	                        daily_total_chat += Time[date][hour][uid]['num']
	                        
	                
	                print >> f, date+'\t'+hour+'\t'+str(len(hourly_user))+'\t'+str(hourly_user_chat)+'\t'+str(hourly_user_chat/hourly_total_chat*100)
	        print >> f_daily, date+'\t'+str(len(daily_user))+str(daily_user_chat)+'\t'+str(daily_user_chat/daily_total_chat*100)



	f.close()
	f_daily.close()
	r_rate.close()
