# src/server/commands/agent/exit.py

from commands import Command
from core import ClientSession
from config import HeaderType

class Exit(Command):


    def execute(self, cid):
        request = {
            HeaderType.COMMAND : 'exit',
            'data' : 'exit'
        }
    # To be continued