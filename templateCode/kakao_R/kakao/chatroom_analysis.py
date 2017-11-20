#-*- coding: utf-8 -*-

# Revision: 6 (June 3th, 2017 3:10)
# Author: Claude Jin, Sanggyu Nam, Seunghyun Han (DiscoveryChannel)

# Logs
# Revision 1: user anonymization, dateline, firstline, message types(emoticon, photo, video, link)
# Revision 2: chatroomname, # of current participants, invitationline, multiple lines into one message
# Revision 3: Add support for chat log files exported in English and refactor the reader logic using classes.
# Revision 4: Replace calling open/close functions of file object to using a context block. This reduces the memory consumption so that it becomes possible to process large data.
# Revision 5: Add argument parsing and fix UTF-8 BOM issue.
# Revision 6: Add --username argument. It makes a specific user to be distinguished even after anonymization.

# references for regular expressionf
# http://regexr.com/
# http://devanix.tistory.com/296

from abc import ABCMeta, abstractmethod
from datetime import datetime, date, time, timedelta
from os import path
import io
import itertools
import re, sys, os
import glob
import csv
import json

class BaseChatLogReader(metaclass=ABCMeta):
    """Base reader for KakaoTalk chat log files."""

    @property
    @abstractmethod
    def chatroomnameGroup(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def chatroomnameIndividual(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def dynamicsline(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def dateline(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def firstline(self):
        raise NotImplementedError

    def fileobj(self, f):
        if not isinstance(f, (io.TextIOBase, str)):
            raise TypeError('f should be a text I/O stream or a file name')
        return (f if isinstance(f, io.TextIOBase)
                else open(f, 'r', encoding='utf-8-sig'))

    def readChatroomLog(self, filename, username):
        usercounter = 0
        dynamics = []
        dates = []
        messages = []
        participants = dict()
        msg = None

        if username is not 'Empty':
            usercounter += 1
            participants[username] = "user" + str(usercounter)

        with self.fileobj(filename) as f:
            first_line = next(f)

            m = self.chatroomnameGroup.match(first_line)
            if m:
                chatroomName = m.group("name")
                participantCnt = m.group("current")
            else:
                m = self.chatroomnameIndividual.match(first_line)
                chatroomName = m.group("name")
                participantCnt = 2

            lines = itertools.islice(f, 4, None)
            for line in lines:
                # Skip blank lines.
                if len(line) <= 1:
                    continue

                m = self.dynamicsline.match(line)
                if m:
                    dynamics.append(m.groupdict())
                    continue

                m = self.dateline.match(line)
                if m:
                    msg = None
                    dates.append(m.groupdict())
                    continue

                m = self.firstline.match(line)
                if m:
                    if msg is not None:
                        messages.append(msg)
                    msg = self.firstline.match(line).groupdict()

                    # Anonymize users.
                    if msg["participant"] in participants.keys():
                        msg["participant"] = participants[msg["participant"]]
                    else:
                        usercounter += 1
                        participants[msg["participant"]] = "user" + str(usercounter)
                        msg["participant"] = "user" + str(usercounter)
                    continue

                # Encountered a multi-line message.
                if msg is None:
                    print("Multi-line Error")
                    print(line)
                    print(dynamics)
                    exit(1)
                msg["message"] += " " + line

        return [dates, messages, participants, participantCnt, chatroomName, dynamics]


class KoreanChatLogReader(BaseChatLogReader):
    """Reader for KakaoTalk chat log files exported in Korean."""

    @property
    def chatroomnameGroup(self):
        return re.compile("^(?P<name>.*) \((?P<current>[0-9]*)명\)과 카카오톡 대화-1.txt$")

    @property
    def chatroomnameIndividual(self):
        return re.compile("^(?P<name>.*)님과 카카오톡 대화-1.txt$")

    @property
    def dynamicsline(self):
        return re.compile("^(?P<year>[0-9]{4})\. (?P<month>[0-9]{1,2})\. (?P<date>[0-9]{1,2})\. "
                          "(?P<meridiem>오전|오후) (?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2}): "
                          "(.*?)님이 (?:((?:(?:.*?)님(?:, )?(?:과 )?)+)을 초대했습니다|나갔습니다).$")

    @property
    def dateline(self):
        return re.compile("^(?P<year>[0-9]{4})년 (?P<month>[0-9]{1,2})월 (?P<date>[0-9]{1,2})일 (?P<day>.)요일$")

    @property
    def firstline(self):
        return re.compile("^(?P<year>[0-9]{4})\. (?P<month>[0-9]{1,2})\. (?P<date>[0-9]{1,2})\. (?P<meridiem>오전|오후) (?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2}), (?P<participant>.*?) : (?P<message>.*)")


class EnglishChatLogReader(BaseChatLogReader):
    """Reader for KakaoTalk chat log files exported in English."""

    @property
    def chatroomnameGroup(self):
        return re.compile("^KakaoTalk Chats with (?P<name>.*) \((?P<current>[0-9]*) people\)-1.txt$")

    @property
    def chatroomnameIndividual(self):
        return re.compile("^KakaoTalk Chats with (?P<name>.*)-1.txt$")

    @property
    def dynamicsline(self):
        return re.compile("^(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) "
                          "(?P<date>[0-9]{1,2}), (?P<year>[0-9]{4}), "
                          "(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2}) "
                          "(?P<meridiem>AM|PM): "
                          "(.*?) (?:invited ((?:(?:.*?)(?:, )?(?: and )?)+)|left this chatroom).$"
                          )

    @property
    def dateline(self):
        return re.compile("^(?P<day>.{3}).*day, "
                          "(?P<month>January|February|March|April|May|June|July|August|September|October|November|December) "
                          "(?P<date>\d{1,2}), (?P<year>\d{4})$")

    @property
    def firstline(self):
        return re.compile("^(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) "
                          "(?P<date>[0-9]{1,2}), (?P<year>[0-9]{4}), "
                          "(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2}) "
                          "(?P<meridiem>AM|PM), "
                          "(?P<participant>.*?) : (?P<message>.*)")


class Analyzer:
    """Analyzer for KakaoTalk chat log"""

    # message types
    emoticon = re.compile("^\((?:emoticon|이모티콘)\) $")
    photo = re.compile("^(사진|Photo)$")
    video = re.compile("^(동영상|Video)$")
    link = re.compile("^https?:\/\/.*")
    
    maxInterval = 24
    hour2Sec = 3600
    day2Hour = 24

    def __init__(self, lang, chatroomLogs, chatroomID):
        self.chatroomLogs = chatroomLogs
        self.lang = lang
        self.dates = self.chatroomLogs[0]
        self.messages = self.chatroomLogs[1]
        self.participants = self.chatroomLogs[2]
        self.participantCnt = self.chatroomLogs[3]
        self.chatroomName = self.chatroomLogs[4]
        self.dynamics = self.chatroomLogs[5]
        self.users = dict()
        
        self.chatroom = dict()
        self.chatroom["chatroomID"] = chatroomID
        self.chatroom["old"] = self.getOld(self.dates)
        self.chatroom["pop"] = int(self.participantCnt)
        self.chatroom["activePop"] = 0
        self.chatroom["M"] = 0.0
        self.chatroom["F"] = 0.0
        self.chatroom["avgCharLen"] = 0
        self.chatroom["dynamics"] = len(self.dynamics)
        self.chatroom["avgInterval"] = self.getIntervalTime()
        self.chatroom["avgReactTime"] = 0.0


        if len(self.participants) == 2:
            self.maxInterval = 24 # hour
        else:
            self.maxInterval = 8 # hour

        for key, user in zip(self.participants.keys(), self.participants.values()):
            self.users[user] = dict()
            self.users[user]["chatroomID"] = chatroomID
            self.users[user]["userID"] = user
            self.users[user]["avgSeqMsg"] = []
            self.users[user]["maxSeqMsg"] = 0
            self.users[user]["reactionTime"] = []
            self.users[user]["avgCharLen"] = []
            self.users[user]["msgShare"] = 0.0
            self.users[user]["msg"] = 0
            self.users[user]["normal"] = 0
            self.users[user]["photo"] = 0
            self.users[user]["video"] = 0
            self.users[user]["emoticon"] = 0
            self.users[user]["link"] = 0
            self.users[user]["activeness"] = 0

        self.chatroom["M"] = round(self.chatroom["M"] / len(self.participants.keys()), 4)
        self.chatroom["F"] = round(self.chatroom["F"] / len(self.participants.keys()), 4)

    # Return all metrics
    def getMetrics(self):
        days = 54   # You can set the number of days that you want to measure.

        self.getSequentialMsgs()
        self.getReactionTimes()
        self.getCharLen()
        self.getActiveParticipants(days, days)
        self.cntMsgType(days)

        return [self.chatroom, self.users]

    # Count the number of active participants for a specific period
    def getActiveParticipants(self, period, n): # period : days, # n : times of activity
        if self.lang == "kr":
            date = "2017-05-24 00:00"           # You must set the base date
            FMT = '%Y-%m-%d %H:%M'
        else :
            date = "2017-May-24 00:00"
            FMT = '%Y-%b-%d %H:%M'

        for msg in reversed(self.messages):
            interval = datetime.strptime(date, FMT) - datetime.strptime(self.convertTime(msg), FMT)

            if timedelta.total_seconds(interval) > period * self.hour2Sec * self.maxInterval:
                break
            self.users[msg["participant"]]["activeness"] += 1

        for user in self.users:
            value = self.users[user]["activeness"]
            if value >= n:
                self.users[user]["activeness"] = "A"
                self.chatroom["activePop"] += 1
            else :
                self.users[user]["activeness"] = "I"

    # Count the number of messages for a specific period
    def cntMsgType(self, period): 
        cntMsg = 0
        if self.lang == "kr":
            date = "2017-05-24 00:00"           # You must set the base date
            FMT = '%Y-%m-%d %H:%M'
        else :
            date = "2017-May-24 00:00"
            FMT = '%Y-%b-%d %H:%M'
        
        for msg in reversed(self.messages):
            interval = datetime.strptime(date, FMT) - datetime.strptime(self.convertTime(msg), FMT)

            if timedelta.total_seconds(interval) > period * self.hour2Sec * self.day2Hour:
                break
            cntMsg += 1
            self.users[msg["participant"]]["msg"] += 1
            if self.photo.match(msg["message"]):
                self.users[msg["participant"]]["photo"] += 1
            elif self.video.match(msg["message"]):
                self.users[msg["participant"]]["video"] += 1
            elif self.link.match(msg["message"]):
                self.users[msg["participant"]]["link"] += 1
            elif self.emoticon.match(msg["message"]):
                self.users[msg["participant"]]["emoticon"] += 1
            else:
                self.users[msg["participant"]]["normal"] += 1

        for user in self.users:
            self.users[user]["msgShare"] = round(self.users[user]["msg"] / cntMsg, 4)

    # Get interval from all pairs of users
    def getIntervalTime(self):
        intervals = []
        
        for prev_msg, msg in zip(self.messages, self.messages[1:]):
            interval = self.calculateInterval(prev_msg, msg)

            if timedelta.total_seconds(interval) < self.hour2Sec * self.maxInterval:
                intervals.append(interval)
        if len(intervals) > 1:
            avg_interval = timedelta.total_seconds(sum(intervals, timedelta()) / len(intervals))
        else:
            avg_interval = -1.0
        return avg_interval

    # Get some information about consecutive message from a user
    def getSequentialMsgs(self):
        cnt = 0
        user = ""
        for msg in self.messages:
            if cnt is 0 :
                cnt += 1
                user = msg["participant"]
            elif user == msg["participant"]:
                cnt += 1
            else :
                self.users[user]["avgSeqMsg"].append(cnt)
                cnt = 1
                user = msg["participant"]

        for user in self.users:
            value = self.users[user]["avgSeqMsg"]
            if len(value) > 0:
                self.users[user]["avgSeqMsg"] = round(sum(value)/len(value), 4)
                self.users[user]["maxSeqMsg"] = max(value)
            else:
                self.users[user]["avgSeqMsg"] = 0.0
                self.users[user]["maxSeqMsg"] = 0

    # Get some reaction information of a user from a latest message.
    def getReactionTimes(self):
        avgReactTime = 0
        for prev_msg, msg in zip(self.messages, self.messages[1:]):
            if prev_msg["participant"] == msg["participant"]:
                continue
            else:                
                interval = self.calculateInterval(prev_msg, msg)
                
                # Skip the interval > 1 day 
                if timedelta.total_seconds(interval) < self.hour2Sec * self.maxInterval:
                    self.users[msg["participant"]]["reactionTime"].append(interval)

        for user in self.users:
            value = self.users[user]["reactionTime"]
            if len(value) > 0:
                self.users[user]["reactionTime"] = timedelta.total_seconds(sum(value, timedelta()) / len(value))
            else:
                self.users[user]["reactionTime"] = -1
            avgReactTime += int(self.users[user]["reactionTime"])
        self.chatroom["avgReactTime"] = round(avgReactTime / float(len(self.users)), 4)

    # dynamics : Join / Exit
    def getDynamics(self):
        return len(self.dynamics)

    # Count characters from a specific user
    def getCharLen(self):
        avgCharLen = 0

        for msg in self.messages:
            self.users[msg["participant"]]["avgCharLen"].append(len(msg["message"]))
        for user in self.users:
            avgCharLen += sum(self.users[user]["avgCharLen"])
            if len(self.users[user]["avgCharLen"]) > 0:
                self.users[user]["avgCharLen"] = round(sum(self.users[user]["avgCharLen"]) / float(len(self.users[user]["avgCharLen"])), 4)
            else:
                self.users[user]["avgCharLen"] = 0.0            
        self.chatroom["avgCharLen"] = round(avgCharLen / float(len(self.messages)), 4)


    def calculateInterval(self, prev_msg, msg):
        prev_time = self.convertTime(prev_msg)
        time = self.convertTime(msg)
        if self.lang == "kr":   
            FMT = '%Y-%m-%d %H:%M'
        else:   
            FMT = '%Y-%b-%d %H:%M'
        return datetime.strptime(time, FMT) - datetime.strptime(prev_time, FMT)


    def convertTime(self, msg):
        hour = int(msg['hour'])
        if (msg['meridiem'] == "오후" or msg['meridiem'] == "PM") and hour is not 12:
            hour = (hour+12)%24
        elif (msg['meridiem'] == "오전" or msg['meridiem'] == "AM") and hour is 12:
            hour = 0
        return '{}-{}-{} {}:{}'.format(msg['year'], msg['month'], msg['date'], hour, msg['minute'])

    # Estimate age of specific room
    def getOld(self, datelist):
        firstDate = datelist[0]
        endDate = datelist[-1]
        firstDate = '{}-{}-{}'.format(firstDate['year'], firstDate['month'], firstDate['date'])
        endDate = '{}-{}-{}'.format(endDate['year'], endDate['month'], endDate['date'])

        if self.lang == "kr":   
            FMT = '%Y-%m-%d'
        else:   
            FMT = '%Y-%B-%d'
        return timedelta.total_seconds(datetime.strptime(endDate, FMT) - datetime.strptime(firstDate, FMT))
        

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('chatlog', help='put your directory path here')
    parser.add_argument('-C', '--client-lang',
                        choices=['kr', 'en'],
                        default='kr',
                        help='KakaoTalk client language')
    parser.add_argument('-U', '--username',
                        default='Empty',
                        help='set specific KakaoTalk user to \'user1\'')
    args = parser.parse_args()

    ReaderClass = {
        'kr': KoreanChatLogReader,
        'en': EnglishChatLogReader
    }

    prefix = ""
    cnt = 0
    exportCsvDict = dict()
    chatroomList = []
    userList = []
    f_chatroom = open(args.chatlog + "/chatroom.json", "w", encoding='utf-8')
    f_user = open(args.chatlog + "/user.json", "w", encoding='utf-8')


    for file in glob.glob(args.chatlog+"/*.txt"):
        cnt += 1
        print (file[len(args.chatlog)+1:])

        if file[len(args.chatlog)+1:len(args.chatlog)+10] == "KakaoTalk":
            args.client_lang = 'en'
        else:
            args.client_lang = 'kr'

        reader = ReaderClass[args.client_lang]()

        chatroomLogs = reader.readChatroomLog(file, args.username)
        exportCsvDict.update(chatroomLogs[2]) # update participants
        analyzer = Analyzer(args.client_lang, chatroomLogs, prefix + str(cnt))
        chatroom, users = analyzer.getMetrics()
        chatroomList.append(chatroom)
        for user in users:
            userList.append(users[user])

    json.dump(chatroomList, f_chatroom)
    json.dump(userList, f_user)
    f_chatroom.close()
    f_user.close()