# src/server/serializer/base.py

from abc import ABC, abstractmethod

class SerializerBase(ABC):

    @abstractmethod
    def encode(self, data):
        pass

    @abstractmethod
    def decode(self, data):
        pass