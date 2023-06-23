import json
import random
from langchain.schema import HumanMessage, SystemMessage
from langchain.utilities import GoogleSerperAPIWrapper
from waifu.llm.Brain import Brain

class AddKaomoji():
    '''添加 QQ 表情'''
    def __init__(self, brain: Brain, probability=0.3):
        '''
        初始化类。其中probability为发送表情的概率
        '''
        self.brain = brain
        self.table = json.loads(open('presets/kaomojis.json', 'r', encoding='utf-8').read())['Kaomoji']
        self.list = [item['Kaomoji'] for item in self.table]
        self.probability = probability
        self.role = f'You are an Kaomoji selector that returns a Kaomoji based on the given text. But if there is no suitable context for Kaomoji in the table below, you should return -1. Kaomoji table is "{self.table}".'


    def think(self, text: str):
        message = [
            SystemMessage(content=self.role),
            HumanMessage(content='Select a Kaomoji or return -1 for the following sentence:\n' + text)
        ]

        random_number = random.random()
        if random_number > self.probability:
            return ''
        else:
            reply = self.brain.think(message)
            # print(reply)
            if reply in self.list:
                return reply
            else:
                print('No suitable Kaomoji found.')
        return ''


class Search():
    '''进行谷歌搜索'''
    def __init__(self, brain: Brain, api: str):
        self.brain = brain
        self.search = GoogleSerperAPIWrapper(serper_api_key=api, gl='cn', hl='zh-cn', k=20)
        self.check = '''Check the following text if the text needs to be searched. If you think it needs to be searched, response with "yes", otherwise response with "no".'''
        self.role = '''You are a Chinese search keyword generator now for Google search. You need to generate keywords based on the given text for Google search. Response with a search keywords only within a line, not other sentences.'''


    def think(self, text: str):
        if len(text) <= 6:
            return '', ''
        # check = [
        #     SystemMessage(content=self.check),
        #     HumanMessage(content=f'Chekc the following text:\n"{text}"')
        # ]
        # reply = self.brain.think_nonstream(check)
        # if not reply == 'yes':
        #     return '', ''
        message = [
            SystemMessage(content=self.role),
            HumanMessage(content=f'Make a Chinese search keyword for the following text:\n"{text}"')
        ]
        question = self.brain.think_nonstream(message)
        answer = self.search.run(question)
        if len(answer) >= 256:
            answer = answer[0:256]
        return question, answer


class Emotion():
    '''情绪识别'''
    def __init__(self, brain: Brain):
        self.brain = brain
        self.moods = ['表现自己可爱', '生气', '高兴兴奋', '难过', '平常聊天', '温柔', '尴尬害羞']
        self.role = f'''Analyzes the sentiment of a given text said by a girl. When it comes to intimate behavior, such as sexual activity, one should reply with a sense of shyness. Response with one of {self.moods}.'''


    def think(self, text: str):
        message = [
            SystemMessage(content=self.role),
            HumanMessage(content=f'''Response with one of {self.moods} for the following text:\n"{text}"''')
        ]
        reply = self.brain.think_nonstream(message)
        for mood in self.moods:
            if mood in reply:
                return mood
        return '平常聊天'