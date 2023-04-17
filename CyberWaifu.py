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
from text.disclaimers import disc
from azure_speech import playSoundWithAzure

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
        **hps_ms.model).to(device)
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
                        x_tst = stn_tst.unsqueeze(0).to(device)
                        x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
                        sid = LongTensor([speaker_id]).to(device)
                        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
                write(out_path, hps_ms.data.sampling_rate, audio)

if __name__ == "__main__":
    # Check
    api_info = None
    with open("api.json", "r", encoding="utf-8") as f:
        api_info = json.load(f)
    if api_info['openai_key'] == '':
        print(colored('错误: 请在 api.json 中填写 openai api key', 'red'))
        input()
        sys.exit(1)
    elif api_info['baidu_appid'] == '':
        print(colored('错误: 请在 api.json 中填写百度翻译 API 的 appid', 'red'))
        input()
        sys.exit(1)
    elif api_info['baidu_secretKey'] == '':
        print(colored('错误: 请在 api.json 中填写百度翻译 API 的 secretKey', 'red'))
        input()
        sys.exit(1)

    disc()
    print('=========================')
    print('ID\t输出语言\n0\t汉语\n1\t日语')
    model_id = int(input('选择语音语言: '))

    # 获取人设
    print('=========================')
    char_json = None
    with open("characters/config.json", "r", encoding="utf-8") as f:
        char_json = json.load(f)
    print('ID\t人设')
    char_list = list(char_json.keys())
    for i, char in enumerate(char_list):
        if '18' in char:
            print(colored(f'{i}\t{char}', 'red'))
        else:
            print(f'{i}\t{char}')
    charactor = int(input('选择人设: '))
    char_name = char_json[char_list[charactor]]
    char_path = './characters/' + char_name + '.txt'

    system_prompt = ''
    try:
        with open(char_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        print(colored('人设加载成功！', 'green'))
    except:
        print(colored(f'人设文件: {char_path} 不存在', 'red'))

    # 获取模型地址
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
    voice = int(input('选择声线: '))
    key = key_list[voice]

    if model_id == 0:
        chinese_model_path += key + '/' + key + '.pth'
    elif model_id == 1:
        japanese_model_path += key + '/' + key + '.pth'
    id = model_info[key]['sid']

    # 检查历史记录
    clear = False
    if not os.path.exists(record_path):
        os.mkdir(record_path)
    record_path += char_name + '.json'
    if os.path.exists(record_path):
        print(colored('检查到历史记录存在，是否继续使用？(y/n)', 'green'),)
        load_record = input('>>>')
        if load_record == 'y':
            os.system('cls')
            clear = True
            with open(record_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                for item in messages:
                    if item['role'] == 'user':
                        print('>>>' + item['content'])
                    elif item['role'] == 'assistant':
                        print(item['content'])
        elif load_record == 'n':
            os.remove(record_path)
    if not os.path.exists(record_path):
        name = input(f'给{char_list[charactor]}取一个名字吧: ')
        system_prompt += 'Your name is ' + name + '.'

    gpt = ChatBot(api_key=api_info['openai_key'],
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
            trans = translate_baidu(brackets_delete(answer), api_info['baidu_appid'], api_info['baidu_secretKey'])
            if trans == None:
                print(colored('错误: 翻译 API 错误！', 'red'))
            generateSound(brackets_delete(trans), id, model_id)
            sys.stdout.write('\r' + ' '*50 + '\r')
            print(answer, flush=True)
            PlaySound(r'.\output.wav', flags=1)