# **NoxC2**

*A tiny Command and Control framework developed for educational purposes.*
## Status
*In development ...*

## Directory Layout

```bash
NoxC2/src/server
│ 
├── commands
│   ├── __init__.py
│   ├── agent
│   │   ├── __init__.py
│   │   └── agent_commands.py
│   ├── base.py
│   ├── help.py
│   ├── hosts
│   │   ├── __init__.py
│   │   ├── drop_client.py
│   │   ├── remove_client.py
│   │   ├── select_client.py
│   │   └── show_clients.py
│   ├── interact
│   │   ├── __init__.py
│   │   └── shell.py
│   └── registry.py
├── config
│   ├── __init__.py
│   ├── banner.py
│   └── config.py
├── core
│   ├── __init__.py
│   ├── client_manager.py
│   ├── client_session.py
│   └── server.py
│ 
├── serializer
│   ├── __init__.py
│   ├── base.py
│   └── json.py
├── transport
│   ├── __init__.py
│   ├── base.py
│   └── http_transport.py
│
└── main.py
```

## Features

- [x] Shell interaction
- [x] Host discovery
- [x] Multi-client support
- [x] HTTP Transport
- [ ] Encryption
- [ ] Sleep + Jitter
- [ ] File Transfer

## Setup

#### Clone repo
```bash
git clone https://github.com/Carax49/NoxC2.git
cd NoxC2
```

#### Activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows
```

#### Dependencies
```bash
pip install -r requirements.txt
```

#### Run server
```bash
cd src/server
python3 main.py
```

## Usage

Once the server is running, type 'help' to get started.
