from pycqBot.cqHttpApi import cqHttpApi, cqLog
from pycqBot.data import Message
from waifu.Waifu import Waifu
import logging
import json

def load_config():
    with open(f'./qqbot/bot.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['group_id_list'], data['user_id_list']


def make_qq_bot(callback, waifu: Waifu):
    cqLog(level=logging.INFO, logPath='./qqbot/cqLogs')

    cqapi = cqHttpApi(download_path='./qqbot/download')

    def on_private_msg(message: Message):
        if 'CQ' in message.message:
            return
        callback.set_sender(message.sender)
        waifu.ask(message.message)

    group, user = load_config()

    bot = cqapi.create_bot(
        group_id_list=group,
        user_id_list=user
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
    bot.start(go_cqhttp_path='./qqbot/')