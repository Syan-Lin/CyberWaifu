import warnings
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import datetime
import time
def brackets(answer):
    flag = 0
    if "（" in answer and "）" in answer:
        open_index = answer.index("（")
        close_index = answer.index("）")

        action = answer[int(open_index + 1):int(close_index)]
        answer = answer[:open_index] + answer[close_index + 1:]
        flag = 1

    elif "(" in answer and ")" in answer:
        open_index = answer.index("(")
        close_index = answer.index(")")

        action = answer[int(open_index + 1):int(close_index)]
        answer = answer[:open_index] + answer[close_index + 1:]
        flag = 1

    else:
        # print("The string does not have ().")
        flag = 0
        action = ""



    return flag, answer, action

def brackets_replace(answer):
    """
     这个函数实现文本中(动作)的提取与剔除

     Parameters:
     answer:回答的文本

     Returns:
     flag:判断文本中是否存在(动作)
     answer:剔除(动作)后的回答文本
     action:动作文本
     """
    flag, answer, action = brackets(answer)
    return flag, answer, action

def brackets_delete(answer):
    """
     这个函数实现文本中(动作)的提取与剔除

     Parameters:
     answer:回答的文本

     Returns:
     flag:判断文本中是否存在(动作)
     answer:剔除(动作)后的回答文本
     action:动作文本
     """
    while(True):
        flag, answer, action = brackets(answer)
        if flag == 0:
            break

    return answer

def send_sets(character,api):
    if character == 23:
        with open('linghua.txt', 'r', encoding='utf-8') as f:
            for item,line in enumerate(f):
                resp = api.send_message(line)
                print("sent set:",item)
                time.sleep(0.5)



    elif character == -1:
        with open('set_test.txt', 'r', encoding='utf-8') as f:
            for item,line in enumerate(f):
                resp = api.send_message(line)
                print("sent set:",item)
                time.sleep(0.5)
    elif character == 29:
        with open('shenzi.txt', 'r', encoding='utf-8') as f:
            for item,line in enumerate(f):
                resp = api.send_message(line)
                print("sent set:",item)
                time.sleep(0.5)
    print("sets successed!")

def send_sets_self(character,api):

    with open(character, 'r', encoding='utf-8') as f:
        for item,line in enumerate(f):
            resp = api.send_message(line)
            print("sent set:",item)
            time.sleep(0.5)
    print("sets successed!")

def playPromptVoice(voice):
    path = "promptVoice/" + voice
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    # 播放音频文件
    pygame.mixer.music.play()
    # 等待音频播放完成
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def sayHello():
    curr_time = datetime.datetime.now()
    hour = curr_time.hour
    if hour>0 and hour<=12:
        playPromptVoice("am.wav")
    elif hour>12 and hour<=18:
        playPromptVoice("pm.wav")
    else:
        playPromptVoice("nm.wav")

if __name__ == "__main__":
    # answer = "你好啊之(dfds)间的(打发十分)！"
    # print(brackets_replace(answer))
    # send_sets("linghua")
    # winsound.Beep(800, 400)

    # playPromptVoice("web.wav")
    # sayHello()
    pass


