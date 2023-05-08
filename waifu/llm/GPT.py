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

# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# from langchain.schema import AIMessage, HumanMessage, SystemMessage

if __name__ == "__main__":
    # api_key = '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'
    # gpt = GPT(api_key, '小柔', stream=True, callback=StreamingStdOutCallbackHandler())

    # print('start')
    # print(gpt.think([HumanMessage(content='你好')]))
    # print('end')

    # gpt.store_memory('我是小柔')
    # gpt.store_memory('姐姐')
    # gpt.store_memory('你好')
    # gpt.store_memory('AI助手')
    # gpt.store_memory('玄幻小说')
    # gpt.store_memory('科幻小说')
    # gpt.store_memory('今天的天气真好')
    # gpt.store_memory('明天的气温很热')
    # gpt.store_memory('昨天下雪了')
    # gpt.store_memory('今天的学生很多')
    # gpt.store_memory('老师的眼睛很好看')
    # gpt.store_memory('尿不湿很贵')
    # gpt.store_memory('电脑屏幕很大')
    # gpt.store_memory('显卡内存很多')
    # print(gpt.extract_memory('小柔是谁？'))
    pass