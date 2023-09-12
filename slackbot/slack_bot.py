import random
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from presets.emoticon import Links
from waifu.Tools import divede_sentences
from waifu.Waifu import Waifu
import configparser

def make_slack_bot(callback, waifu: Waifu, send_text, send_voice, tts):
    config = configparser.ConfigParser()
    config.read('config.ini', 'utf-8')
    # 创建bot
    slack_app_token = config["Slack"]["SLACK_APP_TOKEN"]
    slack_bot_token = config["Slack"]["SLACK_BOT_TOKEN"]

    app = App(token=slack_bot_token)
    # 收到任何消息
    @app.message(".*")
    def message_handler(message, say):
        """
        用户输入的消息 ：message
        bot 返回消息：say
        """
        Message = message['text']
        try:
            print("用户输入：", Message)
            # 调用ask，获得回复reply
            reply = waifu.ask(Message)
            print("原本回复：", reply)

            # 调用分割bot回复的函数
            sentences = divede_sentences(reply)
            print("多端回复列表：", sentences)
            # 循环发送分割后的列表消息
            for st in sentences:
                # 跳过空格
                if st == '' or st == ' ':
                    continue
                # 如果回复模式为发送文本
                print('--------------')
                print("多端回复处理内容：", st)
                if send_text:
                    # 发送emoji
                    print("预计发送消息文本：", waifu.add_emoji(st))
                    say(waifu.add_emoji(st))

                # 如果回复模式为发送语音，跳过
                if send_voice:
                    pass
                # 回复延迟，让回复更人性化
                time.sleep(random.uniform(0.5, 1))

            # 将本次对话进行记忆存储。同时得到返回的图片表情包文件名称
            # bot回复完后有60%的概况在结尾添加表情包
            print("运行中")
            file_name = waifu.finish_ask(reply)

            print("本次发送的表情包ID为:", file_name)

            # 发送图片表情包
            if file_name != '':
                # 返回表情包对应的直链
                link = Links.linsk.get(file_name)
                blocks = [
                    {
                        "type": "divider"
                    },
                    {
                        "type": "image",
                        "image_url": "{}".format(link),
                        "alt_text": "None"
                    }

                ]
                # 图片发送
                say(blocks=blocks,
                    text="【图片消息】")
                # 富文本形式

            time.sleep(0.5)
            # 不清楚具体用处
            waifu.brain.think('/reset 请忘记之前的对话')
            # 拦截报错
        except Exception as e:
            print("Error in make_slack_bot ", e)

    # 运行bot
    SocketModeHandler(app,slack_app_token).start()
