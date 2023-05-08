import abc
from abc import abstractmethod

class Brain(metaclass=abc.ABCMeta):
    '''CyberWaifu's Brain, actually the interface of LLM.'''

    @abstractmethod
    def think(self, messages):
        pass


    @abstractmethod
    def think_nonstream(self, messages):
        pass


    @abstractmethod
    def llm(self):
        pass


    @abstractmethod
    def llm_nonstream(self):
        pass


    @abstractmethod
    def store_memory(self, memory):
        pass


    @abstractmethod
    def extract_memory(self, text, top_n):
        pass