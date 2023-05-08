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

from langchain.chat_models import ChatOpenAI

if __name__ == "__main__":
    api_key = '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'
    api = 'be6e04a065340e490a32cd9623151788e43422de'
    llm_nonstream = ChatOpenAI(openai_api_key=api_key)
    search = GoogleSerperAPIWrapper(serper_api_key=api, gl='cn', hl='zh-cn', k=10)
    test = ['星穹铁道好好玩', '哈哈哈，你在干嘛呢？', '帮我查一下明天的青岛天气', '如何看待最近很火的孔乙己的长衫？', '推荐几个B站视频', '最近有什么好玩的事情']
    for text in test:
        # check = [
        #     SystemMessage(content='''You need to reply to the information based on the user's input. If you feel the need for search engine assistance, especially when the user's input contains information that you do not know, such as certain nouns or real-time information that are not in your training data. If you need Google, answer "yes", otherwise answer "no"'''),
        #     HumanMessage(content=f'Make a search decision for the following text:\n"{text}"')
        # ]
        # reply = llm_nonstream(check).content
        # print(reply)
        # if 'yes' in reply or 'Yes' in reply:
        message = [
            SystemMessage(content='You are a Chinese search keyword generator now for Google search. You need to generate only one keyword based on the given text for Google search. Response with only one search keyword.'),
            HumanMessage(content=f'Make a Chinese search keyword for the following text:\n"{text}"')
        ]
        reply = llm_nonstream(message).content

        print(f'question:{reply}')
        print(f'answer:{search.run(reply)}')