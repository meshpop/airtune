# Airtune

Identify the currently playing song from any radio stream.

## Install

```bash
bash install.sh
```

## Usage

```bash
airtune install                                  # set up dirs (first run)
airtune start                                    # start services
airtune status                                   # check health
airtune recognize https://stream.example.com/radio
```

## Web UI

```bash
python3 server.py
# open http://localhost:8000
```

Enter any radio stream URL and hit **Recognize**.

## Uninstall

```bash
bash uninstall.sh
```
