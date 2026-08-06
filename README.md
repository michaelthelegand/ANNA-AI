# ANNA-AI (Windows Desktop Assistant)

ANNA-AI is a Windows 11 Python desktop assistant with a command-line interface.

## Current status

- Interactive assistant loop through main.py
- Configurable personality and reasoning
- Persistent local memory
- Optional text-to-speech support
- Read-only automation status
- Automation features disabled by default for safety

## Run

Run python main.py to start ANNA. Type help for available commands. Type exit or quit to close ANNA.

## Configuration

Copy .env.example to .env and adjust settings as needed. The .env file is ignored by Git and must never be committed.

## Folder overview

- brain/ - Core logic, memory, reasoning, learning, and personality
- voice/ - Speech-to-text, text-to-speech, and wake-word support
- vision/ - Screen reader and image analysis
- control/ - Mouse, keyboard, Windows, and automation controls
- tools/ - Browser, file, internet, and terminal helpers
- knowledge/ - RAG and vector database layer
- config/ - Application settings
- data/ - Local runtime data
