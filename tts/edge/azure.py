import azure.cognitiveservices.speech as speechsdk

def azure_speak(text: str, voice: str, style: str, api: str, region: str):
    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
    <voice name="{voice}"><prosody rate="+7%">
        <mstts:express-as style="{style}">
            {text}
        </mstts:express-as>
    </prosody></voice>
</speak>
'''

    speech_config = speechsdk.SpeechConfig(subscription=api, region=region)
    audio_config = speechsdk.audio.AudioOutputConfig(filename="./output.wav")

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    # speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_ssml_async(ssml).get()
    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
        print("Did you update the subscription info?")