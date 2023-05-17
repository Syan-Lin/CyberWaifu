from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Union
from langchain.schema import AgentAction, AgentFinish, LLMResult
from waifu.Tools import get_first_sentence
from pycqBot.cqCode import image, record
from waifu.Waifu import Waifu
from tts.TTS import TTS
import os
import time
import logging

class WaifuCallback(BaseCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def __init__(self, tts: TTS = None, send_text: bool = True, send_voice: bool = False):
        self.text = ''
        self.tts = tts
        self.send_text = send_text
        self.send_voice = send_voice

    def register(self, waifu: Waifu):
        self.waifu = waifu

    def set_sender(self, sender):
        self.sender = sender

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.text = ''

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.text += token
        sentence, self.text = get_first_sentence(self.text)
        if not sentence == '':
            if self.send_text:
                self.sender.send_message(self.waifu.add_emoji(sentence))
                logging.info(f'发送信息: {sentence}')
                time.sleep(0.5)
            if self.send_voice:
                emotion = self.waifu.analyze_emotion(sentence)
                if sentence == '' or sentence == ' ':
                    return
                self.tts.speak(sentence, emotion)
                file_path = './output.wav'
                abs_path = os.path.abspath(file_path)
                mtime = os.path.getmtime(file_path)
                local_time = time.localtime(mtime)
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                self.sender.send_message("%s" % record(file='file:///' + abs_path))
                logging.info(f'发送语音({emotion} {time_str}): {sentence}')

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        if len(self.text) > 0:
            if self.send_text:
                self.sender.send_message(self.waifu.add_emoji(self.text))
                logging.info(f'发送信息: {self.text}')
            if self.send_voice:
                emotion = self.waifu.analyze_emotion(self.text)
                self.tts.speak(self.text, emotion)
                file_path = './output.wav'
                abs_path = os.path.abspath(file_path)
                mtime = os.path.getmtime(file_path)
                local_time = time.localtime(mtime)
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                self.sender.send_message("%s" % record(file='file:///' + abs_path))
                logging.info(f'发送语音({emotion} {time_str}): {self.text}')
        file_name = self.waifu.finish_ask(response.generations[0][0].text)
        if not file_name == '':
            file_path = './presets/emoticon/' + file_name
            abs_path = os.path.abspath(file_path)
            self.sender.send_message("%s" % image(file='file:///' + abs_path))

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when chain errors."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        pass

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: Any) -> None:
        """Run on arbitrary text."""

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent end."""