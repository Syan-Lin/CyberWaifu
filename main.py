from waifu.Waifu import Waifu
from waifu.llm.GPT import GPT
from waifu.llm.Claude import Claude
from waifu.Tools import load_prompt, load_memory
from bot.discordbot import discordbot
import configparser

config = configparser.ConfigParser()

# 读取配置文件
config_files = config.read('config.ini', 'utf-8')
if len(config_files) == 0:
    raise FileNotFoundError('配置文件 config.ini 未找到，请检查是否配置正确！')

# CyberWaifu 配置
name 		 = config['CyberWaifu']['name']
username     = config['CyberWaifu']['username']
botkey = config['DiscordBot']['discordbotkey']
charactor 	 = 'Character'
Memory       = 'Muice'

prompt = load_prompt(charactor)

# Thoughts 思考链配置
# emoticons = config.items('Thoughts_Emoticon')
# load_emoticon(emoticons)

# LLM 模型配置
model = config['LLM']['model']
callback = None
if model == 'OpenAI':
    openai_api = config['LLM_OpenAI']['openai_key']
    brain = GPT(openai_api, name, stream=True, callback=callback)
elif model == 'Claude':
	user_oauth_token = config['LLM_Claude']['user_oauth_token']
	bot_id = config['LLM_Claude']['bot_id']
	brain = Claude(bot_id, user_oauth_token, name)

waifu = Waifu(brain=brain,
				prompt=prompt,
				name=name,
                username=username)

# 记忆导入
if Memory != '':
	memory = load_memory(Memory, waifu.name)
	waifu.import_memory_dataset(memory)


if model == 'OpenAI':
	callback.register(waifu)
# make_qq_bot(callback, waifu, send_text, send_voice, tts)

discordbot(botkey, waifu)