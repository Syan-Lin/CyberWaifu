import azure.cognitiveservices.speech as speechsdk
import json
from termcolor import colored
import random
import configparser

def playSoundWithAzure(role, text):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    if config.get('API', 'azure_speech_key') == '' or config.get('API', 'azure_region') == '':
        print(colored('错误: 未配置 Azure API!', 'red'))
        return

    # mood = None
    # with open("model/mood.json", "r", encoding="utf-8") as f:
    #     mood = json.load(f)

    # random_key, style = random.choice(list(mood.items()))
    # print('情绪：' + random_key)

    ssml = '''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
    <voice name="{0}">
        <mstts:express-as style="{1}" styledegree="2">
            {2}
        </mstts:express-as>
    </voice>
</speak>
'''.format(role, '', text)

    # print(ssml)

    speech_key, service_region = config.get('API', 'azure_speech_key'), config.get('API', 'azure_region')
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    speech_synthesizer.start_speaking_ssml_async(ssml).get()
    # if result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = result.cancellation_details
    #     print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #         if cancellation_details.error_details:
    #             print("Error details: {}".format(cancellation_details.error_details))
    #     print("Did you update the subscription info?")