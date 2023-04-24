import ast
import openai
import pandas as pd
import json
import os

from scipy import spatial

class Embedding:
    def __init__(self, api_key, save_path, model='gpt-3.5-turbo', emb_model="text-embedding-ada-002" ):
        openai.api_key = api_key
        self.save_path = save_path
        self.model     = model
        self.emb_model = emb_model
        self.chunks    = []


    def make_embeddings(self, user_text, bot_text):
        if user_text == '':
            return
        elif len(user_text) + len(bot_text) < 20:
            return

        chunk = [f'''I said:"{user_text}". You answered:"{bot_text}"''']

        # Calculate embedding
        embeddings = []
        response = openai.Embedding.create(model=self.emb_model, input=chunk)
        for i, be in enumerate(response["data"]):
            assert i == be["index"]  # double check embeddings are in same order as input
        embedding = [e["embedding"] for e in response["data"]]
        embeddings.extend(embedding)

        df = pd.DataFrame({"text": chunk, "embedding": embeddings})
        df.to_csv(self.save_path, mode='a', header=not os.path.exists(self.save_path), index=False)


    def get_relative_text(self, text, top_n):
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y)

        # Load embeddings data
        if not os.path.isfile(self.save_path):
            return [''], [0]
        df = pd.read_csv(self.save_path)
        row = df.shape[0]
        top_n = min(top_n, row)
        df['embedding'] = df['embedding'].apply(ast.literal_eval)

        # Make query
        query_embedding_response = openai.Embedding.create(
            model=self.emb_model,
            input=text,
        )
        query_embedding = query_embedding_response["data"][0]["embedding"]
        strings_and_relatednesses = [
            (row["text"], relatedness_fn(query_embedding, row["embedding"]))
            for i, row in df.iterrows()
        ]

        # Rank
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        strings, relatednesses = zip(*strings_and_relatednesses)
        return strings[:top_n], relatednesses[:top_n]


    def make_embedding_from_library(self, library):
        '''library 是用 \n\n 分段的字符串，记忆库只有首次使用时才会生成'''
        if os.path.exists(self.save_path):
            return

        contents_list = library.split("\n\n")
        chunks = []

        for chunk in contents_list:
            chunks.append(chunk)

        embeddings = []
        for batch_start in range(0, len(chunks), 1024):
            batch_end = batch_start + 1024
            batch = chunks[batch_start:batch_end]
            response = openai.Embedding.create(model=self.emb_model, input=batch)
            for i, be in enumerate(response["data"]):
                assert i == be["index"]  # double check embeddings are in same order as input
            batch_embeddings = [e["embedding"] for e in response["data"]]
            embeddings.extend(batch_embeddings)

        df = pd.DataFrame({"text": chunks, "embedding": embeddings})
        df.to_csv(self.save_path, index=False)


if __name__ == "__main__":
    user_msg = '''{
"user_msg": "游戏很好玩",
"time": "2023-4-21 03:35:57",
"memory": []
}'''
    bot_msg = '''{
"behavior": "reply",
"reply_msg": "是啊，玩的好开心呀",
"thought": "觉得玩游戏很有意思。",
"mood": "开心"
}'''
    api = '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'
    path = 'embedding.csv'
    emb = Embedding(api, path)
    with open('memory/猫娘.txt', 'r', encoding='utf-8') as f:
        library = f.read()
        emb.make_embedding_from_library(library)
    # emb.make_embeddings(user_msg, bot_msg)
    texts, relative = emb.get_relative_text('你还记得我们上次说玩游戏吗', 5)
    # print(texts, relative)
    # with open('memory.json', 'r', encoding='utf-8') as f:
    #     library = json.load(f)
    #     emb.make_embedding_from_library(library)