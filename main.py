from waifu.Waifu import Waifu
from waifu.StreamCallback import WaifuCallback
from waifu.llm.GPT import GPT
from tts.TTS import TTS
from tts.edge.edge import speak
from qqbot.qqbot import make_qq_bot
from waifu.Tools import load_prompt, load_emoticon, load_memory, str2bool
import configparser

config = configparser.ConfigParser()

# 读取配置文件
config_files = config.read('config.ini', 'utf-8')
if len(config_files) == 0:
    raise FileNotFoundError('配置文件 config.ini 未找到，请检查是否配置正确！')

# CyberWaifu 配置
name 		 = config['CyberWaifu']['name']
username     = config['CyberWaifu']['username']
charactor 	 = config['CyberWaifu']['charactor']
send_text    = str2bool(config['CyberWaifu']['send_text'])
send_voice   = str2bool(config['CyberWaifu']['send_voice'])
use_emoji 	 = str2bool(config['Thoughts']['use_emoji'])
use_qqface   = str2bool(config['Thoughts']['use_qqface'])
use_emoticon = str2bool(config['Thoughts']['use_emoticon'])
use_search 	 = str2bool(config['Thoughts']['use_search'])
use_emotion  = str2bool(config['Thoughts']['use_emotion'])
search_api	 = config['Thoughts_GoogleSerperAPI']['api']
voice 		 = config['TTS']['voice']

prompt = load_prompt(charactor)

# 语音配置
tts_model = config['TTS']['model']
if tts_model == 'Edge':
	tts = TTS(speak, voice)
	api = config['TTS_Edge']['azure_speech_key']
	if api == '':
		use_emotion = False

# QQ bot 回调
callback = WaifuCallback(tts, send_text, send_voice)

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
				use_qqface=use_qqface,
                use_emotion=use_emotion,
				use_emoticon=use_emoticon)

# 记忆导入
filename = config['CyberWaifu']['memory']
if filename != '':
	memory = load_memory(filename, waifu.name)
	waifu.import_memory_dataset(memory)

callback.register(waifu)
make_qq_bot(callback, waifu)