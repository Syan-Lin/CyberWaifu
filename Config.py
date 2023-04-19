import sys
import openai
from text.disclaimers import disc
from termcolor import colored
import json
import glob
import os.path

def checkApi(config):
    if config.get('API', 'openai_key') == '':
        print(colored('错误: 请在 config.ini 中填写 openai api key', 'red'))
        input()
        sys.exit(1)
    elif config.get('Proxy', 'proxy') != '':
        openai.proxy = config.get('Proxy', 'proxy')

def choseLang(config):
    disc()
    print('=========================')
    print('ID\t输出语言\n0\t汉语\n1\t日语')
    chose = ''
    while True:
        chose = input('选择输出语言: ')
        if chose == '0' or chose == '1':
            break
        else:
            print(colored('错误: 请输入 0 或 1', 'red'))
    model_id = int(chose)
    if model_id == 1:
        if config.get('API', 'baidu_appid') == '':
            print(colored('错误: 请在 config.ini 中填写百度翻译 API 的 appid', 'red'))
            input()
            sys.exit(1)
        elif config.get('API', 'baidu_secretKey') == '':
            print(colored('错误: 请在 config.ini 中填写百度翻译 API 的 secretKey', 'red'))
            input()
            sys.exit(1)
    return model_id

def choseChar():
    print('=========================')
    file_list = glob.glob('characters/*')
    char_list = []
    for file in file_list:
        file_path = os.path.basename(file)
        file_name, ext = os.path.splitext(file_path)
        char_list.append(file_name)
    print('ID\t人设')
    for i, char in enumerate(char_list):
        if '18' in char:
            print(colored(f'{i}\t{char}', 'red'))
        else:
            print(f'{i}\t{char}')
    chose = ''
    while True:
        chose = input('选择人设: ')
        try:
            num = int(chose)
            if num >= 0 and num < len(char_list):
                break
            else:
                raise ValueError()
        except:
            print(colored('错误: 请输入范围内的数字', 'red'))
    charactor = int(chose)
    char_name = char_list[charactor]

    system_prompt = ''
    try:
        with open(file_list[charactor], "r", encoding="utf-8") as f:
            system_prompt = f.read()
        print(colored('人设加载成功！', 'green'))
    except:
        print(colored(f'人设文件: {file_list[charactor]} 不存在', 'red'))
    return system_prompt, char_name

def getModel(model_id):
    print('=========================')
    print(colored('注意：黄色声线需要配置 Azure API', 'yellow'))
    print('ID\t声线')
    model_info = None
    with open("model/config.json", "r", encoding="utf-8") as f:
        model_info = json.load(f)

    i = 0
    key_list = []
    for key, info in model_info.items():
        if model_id == 0 and info['language'] == 'Chinese':
            key_list.append(key)
            if 'zh-CN' in key:
                print(colored(str(i) + '\t' + info['name_zh'] + '(' + info['describe'] + ')', 'yellow'))
            else:
                print(str(i) + '\t' + info['name_zh'] + '(' + info['describe'] + ')')
            i = i + 1
        elif model_id == 1 and info['language'] == 'Japanese':
            key_list.append(key)
            if 'zh-CN' in key:
                print(colored(str(i) + '\t' + info['name_zh'] + '(' + info['describe'] + ')', 'yellow'))
            else:
                print(str(i) + '\t' + info['name_zh'] + '(' + info['describe'] + ')')
            i = i + 1
    print('=========================')
    chose = ''
    while True:
        chose = input('选择声线: ')
        try:
            num = int(chose)
            if num >= 0 and num < len(key_list):
                break
            else:
                raise ValueError()
        except:
            print(colored('错误: 请输入范围内的数字', 'red'))
    voice = int(chose)
    key = key_list[voice]
    return model_info[key]['sid'], key