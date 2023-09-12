import json
import logging
import os
import time

from pycqBot.cqCode import image, record
from pycqBot.cqHttpApi import cqHttpApi, cqLog
from pycqBot.data import Message

from waifu.Tools import divede_sentences
from waifu.Waifu import Waifu


def load_config():
    """"
    读取使用者id
    """
    with open(f'./qqbot/bot.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['user_id_list']


# 包含qq bot的回复方法，分割句子方法，发送语音或文本方法，，发表情，颜文字方法，储存记忆方法，调用方法。
# 但个文件实现了qq bot的回复功能，传入的是默认设置的参数

def make_qq_bot(callback, waifu: Waifu, send_text, send_voice, tts):
    """
    log 记录
    """
    cqLog(level=logging.INFO, logPath='./qqbot/cqLogs')

    """
    文件下载
    """
    cqapi = cqHttpApi(download_path='./qqbot/download')

    """
    处理私聊消息
    """

    def on_private_msg(message: Message):
        if 'CQ' in message.message:
            return
        callback.set_sender(message.sender)
        try:
            # 发送消息
            waifu.ask(message.message)
        except Exception as e:
            # 记录报错
            logging.error(e)

    def on_private_msg_nonstream(message: Message):
        if 'CQ' in message.message:
            return
        try:
            # 发送消息
            reply = waifu.ask(message.message)
            # 调用分割bot回复的函数
            sentences = divede_sentences(reply)
            # 循环发送分割后的列表消息
            for st in sentences:
                time.sleep(0.5)
                # 跳过空格
                if st == '' or st == ' ':
                    continue
                # 如果回复模式为发送文本
                if send_text:
                    # 发送消息，调用修改源文本为插入小表情的函数
                    message.sender.send_message(waifu.add_emoji(st))
                    # 打印日志
                    logging.info(f'发送信息: {st}')
                # 如果回复模式为发送语音
                # pass
                if send_voice:
                    emotion = waifu.analyze_emotion(st)
                    tts.speak(st, emotion)
                    file_path = './output.wav'
                    abs_path = os.path.abspath(file_path)
                    mtime = os.path.getmtime(file_path)
                    local_time = time.localtime(mtime)
                    time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    message.sender.send_message("%s" % record(file='file:///' + abs_path))
                    logging.info(f'发送语音({emotion} {time_str}): {st}')
            # 避免风控？
            time.sleep(0.5)
            # 将本次对话进行记忆存储
            file_name = waifu.finish_ask(reply)
            # 如果有颜文字，就进行特殊处理
            if not file_name == '':
                file_path = './presets/emoticon/' + file_name
                abs_path = os.path.abspath(file_path)
                message.sender.send_message("%s" % image(file='file:///' + abs_path))
            time.sleep(0.5)
            # 不清楚具体用处
            # waifu.brain.think('/reset 请忘记之前的对话')
        # 拦截报错
        except Exception as e:
            logging.error(e)

    # 获得使用者id列表
    user = load_config()

    # cq函数
    bot = cqapi.create_bot(
        group_id_list=[0],
        user_id_list=user
    )
    # cq函数 slack 只需要处理单个回复数据的函数即可
    if callback is None:
        bot.on_private_msg = on_private_msg_nonstream
    else:
        bot.on_private_msg = on_private_msg

    # TODO: 指令功能
    # def echo(commandData, message: Message):
    #     # 回复消息
    #     message.sender.send_message(" ".join(commandData))
    # 设置指令为 echo
    # bot.command(echo, "echo", {
    #     # echo 帮助
    #     "help": [
    #         "#echo - 输出文本"
    #     ],
    #     "type": "all"
    # })
    # 运行qq
    bot.start(go_cqhttp_path='./qqbot/')
