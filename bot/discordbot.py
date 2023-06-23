from waifu.Waifu import Waifu
from waifu.Tools import divede_sentences
import logging
import time
import discord

# 禁用discord.py的运行时警告

def discordbot(botkey, waifu: Waifu):
    # This example requires the 'message_content' intent.
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents,proxy='http://127.0.0.1:7890')

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message):
        if message.author != client.user and not message in ['',' ']: 
            print('收到信息: ',message.content)
            reply = waifu.ask(message.content)
            sentences = reply.split(';;')
            for st in sentences:
                time.sleep(2)
                if st == '' or st == ' ':
                    continue
                await message.channel.send(st)
                logging.info(f'发送信息: {st}')
            waifu.finish_ask(reply)
            time.sleep(2)
            waifu.brain.think('/reset 请忘记之前的对话')

    client.run(botkey)

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
