from sentence_transformers import SentenceTransformer, util

from termcolor import colored

class STEmbedding():
    '''Wraper of Sentence Transformer Eembedding'''

    def __init__(self):
        try:
            self.model = SentenceTransformer('./st_model/')
        except:
            print(colored('Sentence Transformer 模型加载失败！', 'red'))


    def embed_documents(self, documents: list):
        '''返回嵌入向量'''
        return list(self.model.encode(documents).tolist())


    def embed_query(self, text: str):
        return self.model.encode(text).tolist()