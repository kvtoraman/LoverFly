#!/usr/bin/env python
#coding: utf-8

#######################################################################
# CTP472 Social Media and Culture
# Author: Jaram Park (jaram.park@kaist.ac.kr)
#######################################################################

import re, sys, os
import codecs
from datetime import datetime, date, time

import copy


Users = {}
user_num = 1


dirName = './data'   ######### Modify the address where you put your data
result_dirName ='./result'
result_dirName = result_dirName + '/'

Daily = {}
Hour = {}
WeekDay = {}
Time = {}

ConvDuration = []

last_message_time = datetime.now()
print last_message_time
time_diff=''

##Modifications
response_rate=''
previous_text=''
r_rate = open(result_dirName+'r_rate.txt','w')

t_idff  = open(result_dirName+'time_diff.txt','w')
for fname in os.listdir(dirName):
        print 'Now analyzing: ', fname  ## input files
        
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
                                except:
                                        continue
                                if user not in Users: #save speaker (it could be a peer or yourself)
                                        uid = 'user'+str(user_num)
                                        Users[user] = uid
                                        user_num+=1
                        except Exception, e:
                                continue
                        
                        day_list = time.split()
                        year = day_list[0][0:4]
                        month = day_list[1].split('.')[0]
                        day = day_list[2].split('.')[0]
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

                        
                        #print('previous_text: '+previous_text)
                        #print('text: '+text)
                        
                        #if('??' in text):
                        #        print('common')
                        #        print(text)
                        current_user = uid
                        if previous_user=='': ## first line
                                previous_user = current_user
                                previous_text=text
               
                        if current_user == previous_user:
                                last_message_time = time_info
                                previous_text=text
                                previous_user = current_user
                                #if('??' in text):
                                #        print('current_user == previous_user')
                                #        print(text)
                
                                
                        else:
                                #if('??' in text):
                                #        print('else')
                                #        print(text)
                                time_diff = time_info - last_message_time
                                last_message_time = time_info
                                
                                print >> t_idff, time_diff
                                #print(previous_text.find('??'))
                                if('?' in previous_text):
                                        print >> r_rate, current_user, date+'\t'+hour+'\t'+str(len(Time[date][hour]))+" Question:"+previous_text+" Answer:"+text,time_diff
                                previous_text = text
                                previous_user = current_user
                elif line=='':
                        current_user  = ''
                        previous_user = ''

        

f = open(result_dirName+'hourly_katalk_conversation_freq.txt','w')
f_daily = open(result_dirName+'daily_katalk_conversation_freq.txt','w')
for date in Time:
        daily_num = 0
        daily_user = {}
        for hour in Time[date]:
                total_num = 0
                for uid in Time[date][hour]:
                        if uid not in daily_user:
                                daily_user[uid] = ''
                        daily_num+=     Time[date][hour][uid]['num']
                        total_num += Time[date][hour][uid]['num']
                
                print >> f, date+'\t'+hour+'\t'+str(len(Time[date][hour]))+'\t'+str(total_num)
        print >> f_daily, date+'\t'+str(len(daily_user))+'\t'+str(daily_num)

f.close()
f_daily.close()
t_idff.close()

r_rate.close()
