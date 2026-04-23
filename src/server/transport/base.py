# src/transport/base.py

from abc import ABC, abstractmethod

class BaseTransport(ABC):

    @abstractmethod
    def start(self):  
        pass

    @abstractmethod
    def accept(self):
        pass

    @abstractmethod
    def send(self, conn, data):
        pass

    @abstractmethod
    def receive(self, conn):
        pass

    @abstractmethod
    def stop(self):
        pass