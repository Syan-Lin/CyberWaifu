import json
import os
import waifu.Thoughts
from waifu.Tools import make_message, message_period_to_now, divede_sentences
from waifu.llm.Brain import Brain
from langchain.schema import messages_from_dict, messages_to_dict
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ChatMessageHistory
import logging,time


class Waifu():
    '''CyberWaifu'''

    def __init__(self,
                 brain: Brain,
                 prompt: str,
                 name: str,
                 username: str):
        self.brain = brain
        self.name = name
        self.username = username
        self.charactor_prompt = SystemMessage(content=f'{prompt}\nYour name is "{name}". Do not response with "{name}: xxx"\nUser name is {username}, you need to call me {username}.\n')
        self.chat_memory = ChatMessageHistory()
        self.history = ChatMessageHistory()
        self.waifu_reply = ''
        self.Kaomoji = waifu.Thoughts.AddKaomoji(self.brain,probability=0.3)

        self.logger = logging.getLogger('Waifu')
        # self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        
        self.load_memory()

    def ask(self, text: str) -> str:
        '''发送信息'''

        # 检测语句和记忆
        if text == '':
            return ''
        message = make_message(text)
        # 第一次检查用户输入文本是否过长
        if self.brain.llm.get_num_tokens_from_messages([message]) >= 256:
            raise ValueError('The text is too long!')
        # 第二次检查 历史记录+用户文本 是否过长
        self.logger.debug(f'历史记录长度: {self.brain.llm.get_num_tokens_from_messages([message]) + self.brain.llm.get_num_tokens_from_messages(self.chat_memory.messages)}')
        if self.brain.llm.get_num_tokens_from_messages([message])\
                + self.brain.llm.get_num_tokens_from_messages(self.chat_memory.messages)>= 1536:
            self.summarize_memory()
        # 第三次检查，如果仍然过长，暴力裁切记忆
        while self.brain.llm.get_num_tokens_from_messages([message])\
                + self.brain.llm.get_num_tokens_from_messages(self.chat_memory.messages)>= 1536:
            self.cut_memory()

        messages = [self.charactor_prompt]

        self.logger.info(f'开始！接收到信息: {text}')

        # 相关记忆检测
        memory = self.brain.extract_memory(text)
        if memory != ['']:
            relative_memory, relativeness = memory
        else:
            self.logger.warning('人设记忆文件似乎为空，将跳过查询相关记忆')
            relative_memory, relativeness = ((),())

        is_full = False
        total_token = 0
        for i in range(len(relative_memory)):
            total_token += self.brain.llm.get_num_tokens(relative_memory[i])
            if(total_token >= 1024):
                is_full = True
        if is_full:
            relative_memory = relative_memory[:i]

        if len(relative_memory) > 0:
            memory_prompt = f'This following message is relative context for your response:\n\n{str(relative_memory)}'
            memory_message = SystemMessage(content=memory_prompt)
            messages.append(memory_message)

            mem_info = ''
            for i in range(len(relative_memory)):
                mem_info += f'{relative_memory[i]}[相关性: {relativeness[i]}]\n'
            self.logger.info(f'查询到相关记忆:\n' + mem_info)

        # 系统信息
        if len(self.chat_memory.messages) >= 2:
            duration = message_period_to_now(self.chat_memory.messages[-2])
            if duration > 1.0:
                system_message = SystemMessage(content=f'Passed {duration} hours since last conversation. You should simulate what you are doing during this period or make corresponding chat responses based on changes in time.')
                messages.append(system_message)
                self.logger.debug(f'引入系统信息: {system_message.content}')

        # 发送消息
        self.chat_memory.messages.append(message)
        self.history.messages.append(message)
        messages.extend(self.chat_memory.messages)
        while self.brain.llm.get_num_tokens_from_messages(messages) > 4096:
            self.cut_memory()
        self.logger.debug(f'LLM query')
        self.reply = self.brain.think(messages)

        old_sentences = divede_sentences(self.reply)
        sentences = []
        for st in old_sentences:
            time.sleep(2)
            if st == '' or st == ' ':
                continue
            st = self.add_kaomoji(st)
            sentences.append(st)
        new_reply = ';;'.join(sentences)

        history = []
        for message in self.chat_memory.messages:
            if isinstance(message, HumanMessage):
                history.append(f'用户: {message.content}')
            else:
                history.append(f'Waifu: {message.content}')
        info = '\n'.join(history)
        self.logger.debug(f'上下文记忆:\n{info}')

        if self.brain.llm.get_num_tokens_from_messages(self.chat_memory.messages)>= 2048:
            self.summarize_memory()

        self.logger.info('结束回复')
        return new_reply


    def finish_ask(self, text: str) -> str:
        '''结束对话并保存记忆'''
        if text == '':
            return ''
        self.chat_memory.add_ai_message(self.reply)
        self.history.add_ai_message(self.reply)
        self.save_memory()
        return ''

    def add_kaomoji(self, text: str) -> str:
        '''返回添加颜文字后的句子'''
        if text == '':
            return ''
        Kaomoji = self.Kaomoji.think(text)
        # print('Kaomoji',Kaomoji)
        return text + Kaomoji


    def analyze_emotion(self, text: str) -> str:
        '''返回情绪分析结果'''
        if text == '':
            return ''
        if self.use_emotion:
            return self.emotion.think(text)
        return ''


    def import_memory_dataset(self, text: str):
        '''导入记忆数据库, text 是按换行符分块的长文本'''
        if text == '':
            return
        chunks = text.split('\n\n')
        self.brain.store_memory(chunks)


    def save_memory_dataset(self, memory: str | list):
        '''保存至记忆数据库, memory 可以是文本列表, 也是可以是文本'''
        self.brain.store_memory(memory)


    def load_memory(self):
        '''读取历史记忆'''
        try:
            if not os.path.isdir('./memory'):
                os.makedirs('./memory')
            with open(f'./memory/{self.name}.json', 'r', encoding='utf-8') as f:
                dicts = json.load(f)
                self.chat_memory.messages = messages_from_dict(dicts)
                self.history.messages = messages_from_dict(dicts)
                while len(self.chat_memory.messages) > 6:
                    self.chat_memory.messages.pop(0)
                    self.chat_memory.messages.pop(0)
        except FileNotFoundError:
            pass


    def cut_memory(self):
        '''删除一轮对话'''
        for i in range(2):
            first = self.chat_memory.messages.pop(0)
            self.logger.debug(f'删除上下文记忆: {first}')


    def save_memory(self):
        '''保存记忆'''
        dicts = messages_to_dict(self.history.messages)
        if not os.path.isdir('./memory'):
            os.makedirs('./memory')
        with open(f'./memory/{self.name}.json', 'w',encoding='utf-8') as f:
            json.dump(dicts, f, ensure_ascii=False)


    def summarize_memory(self):
        '''总结 chat_memory 并保存到记忆数据库中'''
        prompt = ''
        for mes in self.chat_memory.messages:
            if isinstance(mes, HumanMessage):
                prompt += f'{self.username}: {mes.content}\n\n'
            elif isinstance(mes, SystemMessage):
                prompt += f'System Information: {mes.content}\n\n'
            elif isinstance(mes, AIMessage):
                prompt += f'{self.name}: {mes.content}\n\n'
        prompt_template = f"""Write a concise summary of the following, time information should be include:


        {prompt}


        CONCISE SUMMARY IN CHINESE LESS THAN 300 TOKENS:"""
        print('开始总结')
        summary = self.brain.think_nonstream([SystemMessage(content=prompt_template)])
        print('结束总结')
        while len(self.chat_memory.messages) > 4:
            self.cut_memory()
        self.save_memory_dataset(summary)
        self.logger.info(f'总结记忆: {summary}')