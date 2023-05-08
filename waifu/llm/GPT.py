from waifu.llm.Brain import Brain
from waifu.llm.VectorDB import VectorDB
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

class GPT(Brain):
    def __init__(self, api_key, name, stream=False, callback=None, model='gpt-3.5-turbo'):
        self.llm = ChatOpenAI(openai_api_key=api_key,
                        model_name=model,
                        streaming=stream,
                        callbacks=[callback])
        self.llm_nonstream = ChatOpenAI(openai_api_key=api_key, model_name=model)
        self.embedding = OpenAIEmbeddings(openai_api_key=api_key)
        self.vectordb = VectorDB(self.embedding, f'./memory/{name}.csv')


    def think(self, messages):
        return self.llm(messages)


    def think_nonstream(self, messages):
        return self.llm_nonstream(messages)


    def llm(self):
        return self.llm


    def llm_nonstream(self):
        return self.llm_nonstream


    def store_memory(self, text):
        '''保存记忆 embedding'''
        self.vectordb.store(text)


    def extract_memory(self, text, top_n=10):
        '''提取 top_n 条相关记忆'''
        return self.vectordb.query(text, top_n)