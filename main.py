from waifu.Waifu import Waifu
from waifu.StreamCallback import WaifuCallback
from waifu.llm.GPT import GPT
from qqbot.qqbot import make_qq_bot
from waifu.Tools import load_prompt, load_emoticon, load_memory
import configparser

config = configparser.ConfigParser()

# 读取配置文件
config_files = config.read('config.ini', 'utf-8')
if len(config_files) == 0:
    raise FileNotFoundError('配置文件 config.ini 未找到，请检查是否配置正确！')

# QQ bot 回调
callback = WaifuCallback()

# CyberWaifu 配置
name 		 = config['CyberWaifu']['name']
username     = config['CyberWaifu']['username']
charactor 	 = config['CyberWaifu']['charactor']
use_emoji 	 = config['CyberWaifu']['use_emoji']
use_emoticon = config['CyberWaifu']['use_emoticon']
use_search 	 = config['CyberWaifu']['use_search']
search_api	 = config['Thoughts_GoogleSerperAPI']['api']

prompt = load_prompt(charactor)

# Thoughts 思考链配置
emoticons = config.items('Thoughts_Emoticon')
load_emoticon(emoticons)

# LLM 模型配置
model = config['LLM']['model']
if model == 'OpenAI':
    openai_api = config['LLM_OpenAI']['openai_key']
    brain = GPT(openai_api, name, stream=True, callback=callback)

waifu = Waifu(brain=brain,
				prompt=prompt,
				name=name,
                username=username,
				use_search=use_search,
				search_api=search_api,
				use_emoji=use_emoji,
				use_emoticon=use_emoticon)

# 记忆导入
filename = config['CyberWaifu']['memory']
if filename != '':
	memory = load_memory(filename, waifu.name)
	waifu.import_memory_dataset(memory)

callback.register(waifu)
make_qq_bot(callback, waifu)