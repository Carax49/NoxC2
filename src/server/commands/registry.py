REGCOMMANDS = {}    # {command_name : command_class}

def register(command):
    if command not in REGCOMMANDS:
        REGCOMMANDS[command.name] = command()
    return command