# **NoxC2**

*A tiny Command and Control framework developed for educational purposes.*

## Status
*In development ...*

## Directory Layout

```bash
NoxC2/
├── .AI/                          # Documentation and guides
│   ├── advance.md                # Advanced roadmap & TLS direction
│   ├── agent.md                  # Complete architecture documentation
│   └── hdsd.md                   # Web dashboard usage guide
│
├── .claude/                      # Architecture & technical specifications
│   ├── architecture_fontend.md   # Frontend architecture specification
│   └── db.md                     # SQLite database design & specifications
│
├── src/
│   ├── agent/                    # Agent (implant) code
│   │   ├── test.py               # Agent prototype with reconnect logic
│   │   ├── upload_handler.py     # Handle file upload from server
│   │   └── download_handler.py   # Handle file download to server
│   │
│   └── server/                   # Server (C2) code
│       ├── main.py               # Server entry point
│       │
│       ├── commands/             # Command system
│       │   ├── __init__.py
│       │   ├── base.py           # Base Command class
│       │   ├── registry.py       # Command registration system
│       │   ├── help.py           # Help command
│       │   │
│       │   ├── agent/            # Agent-related commands
│       │   │   ├── __init__.py
│       │   │   ├── agent_commands.py    # Exit command
│       │   │   ├── file_upload.py       # Upload file to agent
│       │   │   ├── file_download.py     # Download file from agent
│       │   │   └── remote_shell.py      # Shell command dispatch
│       │   │
│       │   ├── hosts/            # Client management commands
│       │   │   ├── __init__.py
│       │   │   ├── drop_client.py       # Deselect clients
│       │   │   ├── remove_client.py     # Disconnect clients
│       │   │   ├── select_client.py     # Select clients
│       │   │   └── show_clients.py      # List clients
│       │   │
│       │   └── interact/         # Interactive shell
│       │       ├── __init__.py
│       │       └── shell.py      # Main CLI shell loop
│       │
│       ├── config/               # Configuration
│       │   ├── __init__.py
│       │   ├── banner.py         # ASCII art banners
│       │   └── config.py         # Server config (HOST, PORT, DB_PATH, etc.)
│       │
│       ├── core/                 # Core server components
│       │   ├── __init__.py
│       │   ├── client_manager.py # Manage connected clients
│       │   ├── client_session.py # Client communication session
│       │   └── server.py         # Main server class
│       │
│       ├── db/                   # SQLite database persistence layer
│       │   ├── __init__.py       # Database singleton & connection manager
│       │   ├── schema.py         # DDL scripts and schema initialization
│       │   └── repository.py     # Repositories (Agent, Task, FileTransfer, Log)
│       │
│       ├── downloads/            # Downloaded files from agents
│       │   └── <agent-uuid>/     # One folder per agent
│       │
│       ├── frontend/             # Web dashboard
│       │   └── index.html        # Single-page web UI (dark terminal theme)
│       │
│       ├── serializer/           # Message serialization
│       │   ├── __init__.py
│       │   ├── base.py           # Base serializer interface
│       │   └── json.py           # JSON serializer
│       │
│       └── transport/            # Network transport layer
│           ├── __init__.py
│           ├── base.py           # Base transport interface
│           ├── http_transport.py # HTTP / HTTPS long-poll transport
│           └── api.py            # REST API + SSE for web dashboard
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Features

- [x] Shell interaction
- [x] Agent shell command dispatch
- [x] Multi-client support
- [x] HTTP / HTTPS Transport
- [x] File Transfer (Upload & Download)
- [x] Web Dashboard & REST API
- [x] SQLite Data Persistence (WAL Mode)

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

Example workflow:

```bash
client.show -a
client.select <client-id>
shell whoami
client.drop -a
```
