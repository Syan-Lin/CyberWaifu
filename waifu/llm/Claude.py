from waifu.llm.Brain import Brain
from waifu.llm.VectorDB import VectorDB
from waifu.llm.SentenceTransformer import STEmbedding
from slack_sdk.web.client import WebClient
from langchain.chat_models import ChatOpenAI
from slack_sdk.errors import SlackApiError
from typing import List
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
import time

server_token = ''

class SlackClient(WebClient):

    CHANNEL_ID = None
    LAST_TS = None
    CALLBACK = None

    def chat(self, text):
        if not self.CHANNEL_ID:
            raise Exception("Channel not found.")

        resp = self.chat_postMessage(channel=self.CHANNEL_ID, text=text)
        self.LAST_TS = resp["ts"]

    def open_channel(self, bot_id: str):
        if not self.CHANNEL_ID:
            response = self.conversations_open(users=bot_id)
            self.CHANNEL_ID = response["channel"]["id"]


    def get_reply_nonstream(self, bot_id: str):
        for _ in range(150):
            try:
                resp = self.conversations_history(channel=self.CHANNEL_ID, oldest=self.LAST_TS, limit=2)
                msg = [msg["text"] for msg in resp["messages"] if msg["user"] == bot_id]
                if msg and not msg[-1].endswith("Typing…_"):
                    return msg[-1].replace(',', '，').replace('!', '！').replace('?', '？')
            except (SlackApiError, KeyError) as e:
                print(f"Get reply error: {e}")
                return 'Calude Error'
            time.sleep(0.5)


    def get_reply(self, bot_id: str):
        last = ''
        for _ in range(150):
            try:
                resp = self.conversations_history(channel=self.CHANNEL_ID, oldest=self.LAST_TS, limit=2)
                msg = [msg["text"] for msg in resp["messages"] if msg["user"] == bot_id]
                if msg:
                    text = msg[-1].replace('_Typing…_', '').replace('\n', '').replace(' ', '').replace(',', '，')
                    if text:
                        self.CALLBACK.on_llm_new_token(text[len(last):])
                        last = text
                if msg and not msg[-1].endswith("Typing…_"):
                    self.CALLBACK.on_llm_end(text[len(last):])
                    return msg[-1].replace(',', '，').replace('!', '！').replace('?', '？')

            except (SlackApiError, KeyError) as e:
                print(f"Get reply error: {e}")
                return 'Calude Error'
            time.sleep(0.5)

class Claude(Brain):
    '''Claude Brain, 不支持流式输出及回调'''
    def __init__(self, bot_id: str,
                 user_token: str,
                 name: str,
                 stream: bool=True,
                 callback=None):
        self.claude = SlackClient(token=user_token)
        self.claude.CALLBACK = callback
        self.bot_id = bot_id
        self.llm = ChatOpenAI(openai_api_key='sk-xxx') # use for text token count
        self.embedding = STEmbedding()
        self.vectordb = VectorDB(self.embedding, f'./memory/{name}.csv')
        self.claude.open_channel(self.bot_id)


    def think(self, messages: List[BaseMessage] | str):
        '''由于无法同时向 Claude 请求，所以只能以非阻塞方式请求'''
        if isinstance(messages, str):
            self.claude.chat(messages)
            return self.claude.get_reply_nonstream(self.bot_id)
        if len(messages) == 0:
            return ''
        prompt = ''
        for mes in messages:
            if isinstance(mes, HumanMessage):
                prompt += f'Human: ```\n{mes.content}\n```\n\n'
            elif isinstance(mes, SystemMessage):
                prompt += f'System Information: ```\n{mes.content}\n```\n\n'
            elif isinstance(mes, AIMessage):
                prompt += f'AI: ```\n{mes.content}\n```\n\n'
        self.claude.chat(prompt)
        return self.claude.get_reply_nonstream(self.bot_id)


    def think_nonstream(self, messages: List[BaseMessage] | str):
        '''由于无法同时向 Claude 请求，所以只能以非阻塞方式请求'''
        if isinstance(messages, str):
            self.claude.chat(messages)
            return self.claude.get_reply_nonstream(self.bot_id)
        if len(messages) == 0:
            return ''
        prompt = ''
        for mes in messages:
            if isinstance(mes, HumanMessage):
                prompt += f'Human: ```\n{mes.content}\n```\n\n'
            elif isinstance(mes, SystemMessage):
                prompt += f'System Information: ```\n{mes.content}\n```\n\n'
            elif isinstance(mes, AIMessage):
                prompt += f'AI: ```\n{mes.content}\n```\n\n'
        self.claude.chat(prompt)
        return self.claude.get_reply_nonstream(self.bot_id)


    def store_memory(self, text: str | list):
        '''保存记忆 embedding'''
        self.vectordb.store(text)


    def extract_memory(self, text: str, top_n: int = 10):
        '''提取 top_n 条相关记忆'''
        return self.vectordb.query(text, top_n)