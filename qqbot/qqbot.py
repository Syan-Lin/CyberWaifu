from pycqBot.cqHttpApi import cqHttpApi, cqLog
from pycqBot.data import Message
from pycqBot.cqCode import image
from waifu.Waifu import Waifu

import os
import sys
import logging

def make_qq_bot(callback, waifu: Waifu):
    cqLog(level=logging.INFO, logPath='./qqbot/cqLogs')

    cqapi = cqHttpApi(download_path='./qqbot/download')

    def on_private_msg(message: Message):
        if 'CQ' in message.message and 'image' in message.message:
            return
        callback.set_sender(message.sender)
        sys.stdout = sys.__stdout__
        waifu.ask(message.message)

    bot = cqapi.create_bot(
        group_id_list=[
            # 需处理的 QQ 群信息 为空处理所有
            0 # 不处理群消息
        ],
        user_id_list=[
            # 需处理的 QQ 信息 为空处理所有
            475694569
        ]
    )

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
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    bot.start(go_cqhttp_path='./qqbot/')