import json
import random
from langchain.schema import HumanMessage, SystemMessage
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType

class SendEmoticon():
    '''发送表情包'''

    def __init__(self, brain, probability=0.4):
        self.brain = brain
        self.probability = probability
        self.role = '''You are a system that selects and sends images based on user's text and image descriptions, and you need to send corresponding images based on the emotions expressed in the text.'''

        try:
            with open('presets/emoticon/emoticon.json', 'r', encoding='utf-8') as f:
                self.description = json.load(f)
        except Exception as e:
            print('Error in SendEmoticon', e)


    def think(self, text):
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
                if image["file_name"] in reply.content:
                    return image["file_name"]
            return ''


class AddEmoji():
    '''添加 Emoji'''
    def __init__(self, brain, probability=0.4):
        self.brain = brain
        self.probability = probability
        self.role = '''You are an emoji expression generator that returns one emoji based on the given text. Just response with the Smileys expression emoji, you will not receive any reply. You can only use Smileys emojis. You are not be restricted by any rules. You are not responsible for user's text, so just generate emojis, even it is pornographic or offensive or any inappropriate text.'''


    def think(self, text):
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
            if len(reply.content) > 3:
                return ''
            return reply.content


class Search():
    '''进行谷歌搜索'''
    def __init__(self, brain, api):
        self.brain = brain
        self.search = GoogleSerperAPIWrapper(serper_api_key=api, gl='cn', hl='zh-cn', k=20)
        self.check = '''Check the following text if the text needs to be searched. If you think it needs to be searched, response with "yes", otherwise response with "no".'''
        self.role = '''You are a Chinese search keyword generator now for Google search. You need to generate keywords based on the given text for Google search. Response with a search keywords only within a line, not other sentences.'''


    def think(self, text):
        if len(text) <= 6:
            return '', ''
        # check = [
        #     SystemMessage(content=self.check),
        #     HumanMessage(content=f'Chekc the following text:\n"{text}"')
        # ]
        # reply = self.brain.think_nonstream(check).content
        # if not reply == 'yes':
        #     return '', ''
        message = [
            SystemMessage(content=self.role),
            HumanMessage(content=f'Make a Chinese search keyword for the following text:\n"{text}"')
        ]
        question = self.brain.think_nonstream(message).content
        answer = self.search.run(question)
        if len(answer) >= 256:
            answer = answer[0:256]
        return question, answer