from typing import Callable

class TTS():
    '''TTS Warper'''
    def __init__(self, mouth: Callable[[str, str, str], None], voice: str):
        self.mouth = mouth
        self.voice = voice

    def speak(self, text: str, emotion: str):
        '''emotion 字段在 Thoughts.Emotion 中定义'''
        self.mouth(text, self.voice, emotion)