# src/server/commands/agent/agent_commands.py

from config import MessageType as messtype

class Exit:
    @staticmethod
    def execute(*cids):
        from core.client_manager import Manager

        for cid in cids:
            client = Manager.get_client(cid)
            if client is None:
                continue

            client_session = client.session
            client_session.send_request(messtype.COMMAND, 'agent.exit')
