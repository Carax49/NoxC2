# src/commands/base.py

from abc import ABC, abstractmethod

class Command(ABC):
    name = ""
    description = ""

    @abstractmethod
    def execute(self, *args):
        pass