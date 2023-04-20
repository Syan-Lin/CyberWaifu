import re
import torch
from torch import no_grad, LongTensor
from models import SynthesizerTrn
import utils
import commons
from scipy.io.wavfile import write
from text import text_to_sequence
import sys
from termcolor import colored

chinese_model_path = "./model/"
chinese_config_path = "./model/cn_config.json"
japanese_model_path = "./model/"
japanese_config_path = "./model/jp_config.json"

n_symbols = None
emotion_embedding = None
hps_ms = None
net_g_ms = None

# gpu 加速
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == "cuda":
    print("已开启GPU加速!")

def load_model(model_id):
    global n_symbols
    global emotion_embedding
    global hps_ms
    global net_g_ms

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
    print(colored('语音模型加载成功！', 'green'))

def get_text(text, cleaned=False):
    global n_symbols
    global emotion_embedding
    global hps_ms
    global net_g_ms

    if cleaned:
        text_norm = text_to_sequence(text, hps_ms.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps_ms.symbols, hps_ms.data.text_cleaners)
    if hps_ms.data.add_blank:
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

def test():
    print(n_symbols, hps_ms, net_g_ms, chinese_model_path)

def generateSound(inputString, id):
    global n_symbols
    global emotion_embedding
    global hps_ms
    global net_g_ms

    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

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
                    cleaned, text = get_label(text, 'CLEANED')

                    stn_tst = get_text(text, cleaned=cleaned)

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
import time
from winsound import PlaySound

if __name__ == "__main__":
    key = 'alice'
    model_id = 1
    id = 10
    chinese_model_path += key + '/' + key + '.pth'
    japanese_model_path += key + '/' + key + '.pth'
    load_model(model_id)

    while True:
        answer = input()
        # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        device = torch.device('cpu')

        start_time = time.time()
        generateSound(answer, id)
        end_time = time.time()
        cost_time = end_time - start_time
        print(f"GPU程序共耗时：{cost_time:.2f} 秒")
        PlaySound(r'.\output.wav', flags=1)

        input()
        device = torch.device('cpu')

        start_time = time.time()
        generateSound(answer, id)
        end_time = time.time()
        cost_time = end_time - start_time
        print(f"CPU程序共耗时：{cost_time:.2f} 秒")
        PlaySound(r'.\output.wav', flags=1)