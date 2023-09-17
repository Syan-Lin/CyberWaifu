import abc
from abc import abstractmethod

class Brain(metaclass=abc.ABCMeta):
    '''CyberWaifu's Brain, actually the interface of LLM.'''

    @abstractmethod
    def think(self, messages: list):
        pass


    @abstractmethod
    def think_nonstream(self, messages: list):
        pass


    @abstractmethod
    def store_memory(self, memory: str | list):
        pass


    @abstractmethod
    def extract_memory(self, text: str, top_n: int):
        pass