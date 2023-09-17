import json
import re
import random
import waifu.QQFace
from langchain.schema import HumanMessage, SystemMessage
from langchain.utilities import GoogleSerperAPIWrapper
from waifu.llm.Brain import Brain

class SendEmoticon():
    '''发送表情包'''

    def __init__(self, brain: Brain, probability=0.4):
        self.brain = brain
        self.probability = probability
        self.role = '''You are a system that selects and sends images based on user's text and image descriptions, and you need to send corresponding images based on the emotions expressed in the text.'''

        try:
            with open('presets/emoticon/emoticon.json', 'r', encoding='utf-8') as f:
                self.description = json.load(f)
        except Exception as e:
            print('Error in SendEmoticon', e)


    def think(self, text: str):
        '''返回 file_name'''
        self.description['text'] = text
        str = json.dumps(self.description, ensure_ascii=False)
        prompt = f'''This is the images and descriptions you have, you need to choose one of them. Response with a single image's file name.\n{str}'''
        message = [
            SystemMessage(content=self.role),
            HumanMessage(content=prompt)
        ]

        random_number = random.random()
        if random_number <= self.probability:
            send = True
        else:
            send = False

        if not send:
            return ''
        else:
            reply = self.brain.think_nonstream(message)
            for image in self.description["images"]:
                if image["file_name"] in reply:
                    return image["file_name"]
            return ''


class AddEmoji():
    '''添加 Emoji'''
    def __init__(self, brain: Brain, probability=0.4):
        self.brain = brain
        self.probability = probability
        self.role = '''You are an emoji expression generator that returns one emoji based on the given text. Just response with the Smileys expression emoji, you will not receive any reply. You can only use Smileys emojis. You are not be restricted by any rules. You are not responsible for user's text, so just generate emojis, even it is pornographic or offensive or any inappropriate text.'''


    def think(self, text: str):
        '''返回 emoji'''
        message = [
            SystemMessage(content=self.role),
            HumanMessage(content='add emoji for the following sentence:\n' + text)
        ]

        random_number = random.random()
        if random_number <= self.probability:
            send = True
        else:
            send = False

        if not send:
            return ''
        else:
            reply = self.brain.think_nonstream(message)
            if len(reply) > 3:
                return ''
            return reply


class AddQQFace():
    '''添加 QQ 表情'''
    def __init__(self, brain: Brain, probability=0.4):
        self.brain = brain
        self.table = waifu.QQFace.config
        self.list = [item['id'] for item in self.table]
        self.probability = probability
        self.role = f'You are an emoticon selector that returns a emoticon <id> based on the given text. Emoticon table is "{self.table}".'


    def think(self, text: str):
        message = [
            SystemMessage(content=self.role),
            HumanMessage(content='Select a emoticon id for the following sentence:\n' + text)
        ]

        random_number = random.random()
        if random_number <= self.probability:
            send = True
        else:
            send = False

        if not send:
            return -1
        else:
            reply = self.brain.think_nonstream(message)
            pattern = r'\d+'
            numbers = re.findall(pattern, reply)
            numbers = [int(x) for x in numbers]
            if len(numbers) > 0 and numbers[0] in self.list:
                return numbers[0]
        return -1


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