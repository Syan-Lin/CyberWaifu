import re
import os
import json
import datetime
from typing import List
from dateutil.parser import parse
from langchain.schema import HumanMessage, BaseMessage
from termcolor import colored

def get_first_sentence(text: str):
    sentences = re.findall(r'.*?[~。！？…]+', text)
    if len(sentences) == 0:
        return '', text
    first_sentence = sentences[0]
    after = text[len(first_sentence):]
    return first_sentence, after


def divede_sentences(text: str) -> List[str]:
    sentences = re.findall(r'.*?[~。！？…]+', text)
    if len(sentences) == 0:
        return [text]
    return sentences


def make_message(text: str):
    data = {
        "msg": text,
        "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return HumanMessage(content=json.dumps(data, ensure_ascii=False))


def message_period_to_now(message: BaseMessage):
    '''返回最后一条消息到现在的小时数'''
    last_time = json.loads(message.content)['time']
    last_time = parse(last_time)
    now_time = parse(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    duration = (now_time - last_time).total_seconds() / 3600
    return duration


def load_prompt(filename: str):
    file_path = f'./presets/charactor/{filename}.txt'
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        print(colored(f'人设文件加载成功！({file_path})', 'green'))
    except:
        print(colored(f'人设文件: {file_path} 不存在', 'red'))
    return system_prompt


def load_emoticon(emoticons: list):
    data = {'images': []}
    files = []
    for i in range(0, len(emoticons), 2):
        data['images'].append({
            'file_name': emoticons[i][1],
            'description': emoticons[i+1][1]
        })
        files.append(f'./presets/emoticon/{emoticons[i][1]}')
    try:
        with open(f'./presets/emoticon/emoticon.json', 'w',encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        for file in files:
            if not os.path.exists(file):
                raise FileNotFoundError(file)
        print(colored(f'表情包加载成功！({len(files)} 个表情包文件)', 'green'))
    except FileNotFoundError as e:
        print(colored(f'表情包加载失败，图片文件 {e} 不存在！', 'red'))
    except:
        print(colored(f'表情包加载失败，请检查配置', 'red'))


def load_memory(filename: str, waifuname):
    file_path = f'./presets/charactor/{filename}.txt'
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            memory = f.read()
        if os.path.exists(f'./memory/{waifuname}.csv'):
            print(colored(f'记忆数据库存在，不导入记忆', 'yellow'))
            return ''
        else:
            chunks = memory.split('\n\n')
            print(colored(f'记忆导入成功！({len(chunks)} 条记忆)', 'green'))
    except:
        print(colored(f'记忆文件文件: {file_path} 不存在', 'red'))

    return memory


def str2bool(text: str):
    if text == 'True' or text == 'true':
        return True
    elif text == 'False' or text == 'false':
        return False
    else:
        print(colored(f'无法将 {text} 转换为布尔值，请检查配置文件！'))
        raise ValueError()