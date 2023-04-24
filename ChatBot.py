import openai
import json
from TokenCount import count
from Embedding import Embedding
from termcolor import colored
import os

TOP_N = 10

class ChatBot:
    def __init__(self, api_key, prompt, save_path, file_name, model='gpt-3.5-turbo'):
        openai.api_key = api_key
        self.prompt    = prompt
        self.save_path = save_path + file_name + '.json'
        self.memory    = []
        self.library   = []
        self.model     = model
        self.embedding = Embedding(api_key, save_path + file_name + '.csv', model)

        self.load_memory()


    def ask(self, text):
        while count(self.memory) + count([{'role': 'user', 'content': text}]) >= 2560:
            self.cut_memory()

        send_memory = self.memory.copy()
        self.memory.append({'role': 'user', 'content': text})
        self.library.append({'role': 'user', 'content': text})

        # Add embedding
        strings, relatives = self.embedding.get_relative_text(text, TOP_N)
        temp = []
        for string in strings:
            temp.append({'role': 'user', 'content': string})
        while count(temp) >= 1236:
            temp.pop()
        text += '\n[System Memory: This is your system memory, and your answer should be based on system memory. You cannot mention memories unrelated to the problem. You should judge the degree of correlation between the problem and memory and only select relevant memories as additional contextual information to introduce\n' + str(strings[0:len(temp)]) + ']'

        send_memory.append({'role': 'user', 'content': text})

        try:
            response = openai.ChatCompletion.create(
                model       = self.model,
                messages    = send_memory,
                temperature = 1,
            )
        except Exception as e:
            return 'ChatGPT 出错！(' + str(e) + ')'

        result = response['choices'][0]['message']['content']
        self.memory.append({'role': 'assistant', 'content': result})
        self.library.append({'role': 'assistant', 'content': result})

        # print('receive: ' + str(result))

        self.save()

        return result


    def load_memory(self):
        try:
            # 加载最近的二十条记忆
            with open(self.save_path, 'r', encoding='utf-8') as f:
                self.library = json.load(f)
                self.memory = []
                self.memory.append(self.library[0])
                length = min(20, len(self.library) - 1)
                self.memory.extend([self.library[i] for i in range(-length, 0)])
        except FileNotFoundError:
            self.memory.append({'role': 'system', 'content': self.prompt})
            self.library.append({'role': 'system', 'content': self.prompt})
            self.save()


    def cal_emb_from_file(self, path):
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                library = f.read()
                self.embedding.make_embedding_from_library(library)
                print(colored('成功导入记忆数据库!', 'green'),)
        except FileNotFoundError:
            return


    def cut_memory(self):
        user_text = self.memory[1]['content']
        bot_text = self.memory[2]['content']

        self.embedding.make_embeddings(user_text, bot_text)
        del self.memory[1:3]


    def save(self):
        with open(self.save_path, 'w',encoding='utf-8') as f:
            json.dump(self.library, f, ensure_ascii=False)