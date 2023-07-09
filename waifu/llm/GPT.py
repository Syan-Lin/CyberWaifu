from waifu.llm.Brain import Brain
from waifu.llm.VectorDB import VectorDB
from waifu.llm.SentenceTransformer import STEmbedding
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from typing import Any, List, Mapping, Optional
from langchain.schema import BaseMessage
import openai

class GPT(Brain):
    def __init__(self, api_key: str,
                 name: str,
                 stream: bool=False,
                 callback=None,
                 model: str='gpt-3.5-turbo',
                 proxy: str=''):
        self.llm = ChatOpenAI(openai_api_key=api_key,
                        model_name=model,
                        streaming=stream,
                        callbacks=[callback],
                        temperature=0.85)
        self.llm_nonstream = ChatOpenAI(openai_api_key=api_key, model_name=model)
        self.embedding = OpenAIEmbeddings(openai_api_key=api_key)
        # self.embedding = STEmbedding()
        self.vectordb = VectorDB(self.embedding, f'./memory/{name}.csv')
        if proxy != '':
            openai.proxy = proxy


    def think(self, messages: List[BaseMessage]):
        response = self.llm(messages)
        if response.content:
            return response.content
        else:
            # 简化信息后再发送
            simplified_messages = messages[:-1] + [BaseMessage(content="Simplified version of the question", role=messages[-1].role)]
            response = self.llm(simplified_messages)
            return response.content if response.content else "Sorry, I couldn't generate a response."


    def think_nonstream(self, messages: List[BaseMessage]):
        response = self.llm_nonstream(messages)
        if response.content:
            return response.content
        else:
            # 简化信息后再发送
            simplified_messages = messages[:-1] + [BaseMessage(content="Simplified version of the question", role=messages[-1].role)]
            response = self.llm_nonstream(simplified_messages)
            return response.content if response.content else "Sorry, I couldn't generate a response."


    def store_memory(self, text: str | list):
        '''保存记忆 embedding'''
        self.vectordb.store(text)


    def extract_memory(self, text: str, top_n: int = 10):
        '''提取 top_n 条相关记忆'''
        return self.vectordb.query(text, top_n)
