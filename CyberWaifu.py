import json
from scipy.io.wavfile import write
from text import text_to_sequence
from models import SynthesizerTrn
import utils
import commons
import sys
import re
import torch
from torch import no_grad, LongTensor
from winsound import PlaySound
from ChatBot import ChatBot
from translateBaidu import translate_baidu
from tools import *
import os
import datetime
from termcolor import colored
from azure_speech import playSoundWithAzure
import configparser
import Config

# gpu 加速
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == "cuda":
    print("已开启GPU加速!")

chinese_model_path = "./model/"
chinese_config_path = "./model/cn_config.json"
japanese_model_path = "./model/"
japanese_config_path = "./model/jp_config.json"
record_path = "./chat_record/"
character_path = "./characters/"

def get_input():
    print(">>>", end='')
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_input = input() + f'\n[系统时间: {time}]'
    sys.stdout.write('\r' + '信息正在飞快传往异次元...')
    sys.stdout.flush()
    return user_input

def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm

def get_label_value(text, label, default, warning_name='value'):
    value = re.search(rf'\[{label}=(.+?)\]', text)
    if value:
        try:
            text = re.sub(rf'\[{label}=(.+?)\]', '', text, 1)
            value = float(value.group(1))
        except:
            print(f'Invalid {warning_name}!')
            sys.exit(1)
    else:
        value = default
    return value, text

def get_label(text, label):
    if f'[{label}]' in text:
        return True, text.replace(f'[{label}]', '')
    else:
        return False, text

def generateSound(inputString, id, model_id):
    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

    #model = input('0: Chinese')
    #config = input('Path of a config file: ')
    if model_id == 0:
        model = chinese_model_path
        config = chinese_config_path
    elif model_id == 1:
        model = japanese_model_path
        config = japanese_config_path

    hps_ms = utils.get_hparams_from_file(config)
    n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
    emotion_embedding = hps_ms.data.emotion_embedding if 'emotion_embedding' in hps_ms.data.keys() else False

    net_g_ms = SynthesizerTrn(
        n_symbols,
        hps_ms.data.filter_length // 2 + 1,
        hps_ms.train.segment_size // hps_ms.data.hop_length,
        n_speakers=n_speakers,
        emotion_embedding=emotion_embedding,
        **hps_ms.model)
    _ = net_g_ms.eval()
    utils.load_checkpoint(model, net_g_ms)

    if n_symbols != 0:
        if not emotion_embedding:
            #while True:
            if(1 == 1):
                choice = 't'
                if choice == 't':
                    text = inputString
                    if text == '[ADVANCED]':
                        text = "我不会说"

                    length_scale, text = get_label_value(
                        text, 'LENGTH', 1, 'length scale')
                    noise_scale, text = get_label_value(
                        text, 'NOISE', 0.667, 'noise scale')
                    noise_scale_w, text = get_label_value(
                        text, 'NOISEW', 0.8, 'deviation of noise')
                    # length_scale = 1
                    # noise_scale = 0.667
                    # noise_scale_w = 0.8
                    cleaned, text = get_label(text, 'CLEANED')

                    stn_tst = get_text(text, hps_ms, cleaned=cleaned)

                    speaker_id = id
                    out_path = "output.wav"

                    with no_grad():
                        x_tst = stn_tst.unsqueeze(0)
                        x_tst_lengths = LongTensor([stn_tst.size(0)])
                        sid = LongTensor([speaker_id])

                        # GPU 加速
                        x_tst = x_tst.to(device)
                        x_tst_lengths = x_tst_lengths.to(device)
                        sid = sid.to(device)
                        net_g_ms = net_g_ms.to(device)

                        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
                write(out_path, hps_ms.data.sampling_rate, audio)

if __name__ == "__main__":
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    Config.checkApi(config)
    model_id = Config.choseLang(config)
    system_prompt, char_name = Config.choseChar()
    id, key = Config.getModel(model_id)

    if model_id == 0:
        chinese_model_path += key + '/' + key + '.pth'
    elif model_id == 1:
        japanese_model_path += key + '/' + key + '.pth'

    # 检查历史记录
    clear = False
    if not os.path.exists(record_path):
        os.mkdir(record_path)
    record_path += char_name + '.json'
    if os.path.exists(record_path):
        print(colored('检查到历史记录存在，是否继续使用？(y/n)', 'green'),)
        load_record = input('>>>')
        if load_record == 'n':
            os.remove(record_path)
        else:
            os.system('cls')
            clear = True
            with open(record_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                for item in messages:
                    if item['role'] == 'user':
                        print('>>>' + item['content'])
                    elif item['role'] == 'assistant':
                        print(item['content'])
    if not os.path.exists(record_path):
        name = input(f'给{char_name}取一个名字吧: ')
        system_prompt += 'Your name is ' + name + '.'

    gpt = ChatBot(api_key=config.get('API', 'openai_key'),
                  setting=system_prompt,
                  save_path=record_path)

    if not clear:
        os.system('cls')

    while True:
        if model_id == 0:
            answer = gpt.send_message(get_input()).replace('\n','')
            if 'zh-CN' in key:
                sys.stdout.write('\r' + ' '*50 + '\r')
                print(answer, flush=True)
                playSoundWithAzure(key, brackets_delete(answer))
            else:
                generateSound("[ZH]"+ brackets_delete(answer) +"[ZH]", id, model_id)
                sys.stdout.write('\r' + ' '*50 + '\r')
                print(answer, flush=True)
                PlaySound(r'.\output.wav', flags=1)
        elif model_id == 1:
            answer = gpt.send_message(get_input()).replace('\n','')
            trans = translate_baidu(brackets_delete(answer), config.get('API', 'baidu_appid'), config.get('API', 'baidu_secretKey'))
            if trans == None:
                print(colored('错误: 翻译 API 错误！', 'red'))
            generateSound(brackets_delete(trans), id, model_id)
            sys.stdout.write('\r' + ' '*50 + '\r')
            print(answer, flush=True)
            PlaySound(r'.\output.wav', flags=1)