from typing import List

import openai
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import BaseMessage

from waifu.llm.Brain import Brain
from waifu.llm.VectorDB import VectorDB


class GPT(Brain):
    def __init__(self, api_key: str,
                 name: str,
                 stream: bool = False,
                 callback=None,
                 openai_model: str = 'gpt-3.5-turbo',
                 openai_proxy: str = ''):
        self.llm = ChatOpenAI(openai_api_key=api_key,
                              model_name=openai_model,
                              streaming=stream,
                              callbacks=[callback],
                              temperature=0.85)
        self.llm_nonstream = ChatOpenAI(openai_api_key=api_key, model_name=openai_model)
        self.embedding = OpenAIEmbeddings(openai_api_key=api_key)
        # self.embedding = STEmbedding()
        self.vectordb = VectorDB(self.embedding, f'./memory/{name}.csv')
        if openai_proxy != '':
            openai.proxy = openai_proxy

    def think(self, messages: List[BaseMessage]):
        return self.llm(messages).content

    def think_nonstream(self, messages: List[BaseMessage]):
        return self.llm_nonstream(messages).content

    def store_memory(self, text: str | list):
        '''保存记忆 embedding'''
        self.vectordb.store(text)

    def extract_memory(self, text: str, top_n: int = 10):
        '''提取 top_n 条相关记忆'''
        return self.vectordb.query(text, top_n)
