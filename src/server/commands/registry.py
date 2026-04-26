# src/server/commands/registry.py

# -- {command_name : instance} --
GENERAL_COMMANDS = {}
HOST_COMMANDS = {}
AGENT_COMMANDS = {}

GROUPS = {
    'general' : GENERAL_COMMANDS,
    'host'    : HOST_COMMANDS,
    'agent'   : AGENT_COMMANDS,
}

def register(command):
    group = command.group
    GROUPS[group][command.name] = command()
    return command