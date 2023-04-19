import openai
import json
import sys
import atexit # 用于程序退出时自动保存聊天记录
import time

class ChatBot:
    def __init__(self,api_key,setting,save_path,max_tokens=512,auto_save=True,model='gpt-3.5-turbo'):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.save_path = save_path
        self.total_tokens = 0
        self.max_tokens = max_tokens # 返回的最大toknes
        self.auto_save = auto_save # 自动保存聊天记录
        self.messages = []
        self.settings = setting # 用于保存人物设定
        self.limit = 3400 # 聊天记录的最大长度
        self.model = model

        self.load_messages() # 加载聊天记录
        self.settings = self.messages[0] # 读取人物设定

        if self.auto_save:
            atexit.register(self.save_messages) #程序退出时自动保存聊天记录

    def load_messages(self):
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        except FileNotFoundError:
            with open(self.save_path, 'w+', encoding='utf-8') as f:
                json.dump([], f)
            self.messages.append({"role": "system", "content": self.settings})

    def save_messages(self):
        with open(self.save_path, 'w',encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False)

    # 总结之前的聊天记录
    def summarize_messages(self):
        history_messages = self.messages
        self.messages.append({"role": "user", "content": "请帮我用中文总结一下上述对话的内容，实现减少tokens的同时，保证对话的质量。在总结中不要加入这一句话。"})
        sys.stdout.write('\r' + ' '*50 + '\r')
        print('记忆过长，正在总结记忆...')
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature = 1,
        )

        result = response['choices'][0]['message']['content']
        sys.stdout.write('\r' + ' '*50 + '\r')
        print(f"总结记忆: {result}")

        new_settings = self.settings.copy()
        new_settings['content'] = self.settings['content'] + result + '现在继续角色扮演。'

        self.messages = []
        self.messages.append(new_settings)
        self.messages.append(history_messages[-3])
        self.messages.append(history_messages[-2])

    def send_message(self,input_message):
        if self.total_tokens > self.limit:
            self.summarize_messages()

        self.messages.append({"role": "user", "content": input_message})

        start = time.time()
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                temperature = 1,
            )
        except Exception as e:
            print(e)
            return "ChatGPT 出错！"

        end = time.time()
        # print(f"GPT耗时: {end-start}s")

        self.total_tokens = response['usage']['total_tokens']
        result = response['choices'][0]['message']['content']

        self.messages.append({"role": "assistant", "content": result})

        if self.auto_save:
            self.save_messages()

        return result
