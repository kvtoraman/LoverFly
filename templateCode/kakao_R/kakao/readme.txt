[Available on Python 3]

usage: chatroom_analysis.py [-h] [-C {kr,en}] [-U USERNAME] chatlog

positional arguments:
  chatlog               folder path to KakaoTalk chat log text file

optional arguments:
  -h, --help            show this help message and exit
  -C {kr,en}, --client-lang {kr,en}
                        KakaoTalk client language
  -U USERNAME, --username USERNAME
                        set specific KakaoTalk user to 'user1'



Run example: python chatroom_analysis.py -U 한승현 ./data
(Example Data : GCT564 (3명)과 카카오톡 대화-1.txt)