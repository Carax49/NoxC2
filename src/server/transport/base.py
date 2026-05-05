# src/transport/base.py

from abc import ABC, abstractmethod

class BaseTransport(ABC):

    @abstractmethod
    def start(self):  
        pass

    @abstractmethod
    def send(self, *args):
        pass

    @abstractmethod
    def receive(self, *args):
        pass

    @abstractmethod
    def stop(self):
        pass