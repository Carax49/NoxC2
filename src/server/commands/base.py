# src/commands/base.py

from abc import ABC, abstractmethod

class Command(ABC):
    name = ""
    description = ""
    group = ""

    @abstractmethod
    def execute(self, *args):
        pass