# src/server/commands/agent/agent_commads.py

from core import Manager
from config import MessageType as messtype

class Exit:
    @staticmethod
    def execute(*cids):
        for cid in cids:
            client_session = Manager.get_client(cid).session
            client_session.send_request(messtype.COMMAND, 'agent.exit')