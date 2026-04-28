# src/server/commands/agent/agent_commads.py

from core import Manager
from config import HeaderType as header

class Exit:
    @staticmethod
    def execute(*cids):
        for cid in cids:
            client_session = Manager.get_client(cid).session
            client_session.send_request(header.COMMAND, 'agent.exit')