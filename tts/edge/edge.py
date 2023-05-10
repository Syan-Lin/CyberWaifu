import edge_tts
import asyncio
import json
import configparser
from tts.edge.azure import azure_speak

config = configparser.ConfigParser()
config.read('config.ini', 'utf-8')

api = config['TTS_Edge']['azure_speech_key']
region = config['TTS_Edge']['azure_region']

with open(f'./tts/edge/ssml.json', 'r', encoding='utf-8') as f:
    moods = json.load(f)

def speak(text: str, voice: str, description: str):
    '''api 为空时调用非 API 版本, role 和 style 会被忽略'''
    style = 'chat'
    for item in moods:
        if item['name'] == voice:
            for mood in item['style']:
                if mood['description'] == description:
                    style = mood['name']
                    break
            break
    if api == '':
        communicate = edge_tts.Communicate(text=text, voice=voice, rate='+8%')
        asyncio.run(communicate.save('output.wav'))
    else:
        azure_speak(text, voice, style, api, region)