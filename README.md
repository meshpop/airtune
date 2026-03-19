# Airtune

**Hear a song on the radio. Know what it is in seconds.**

Paste any radio stream URL and Airtune tells you the artist, song, and how confident it is. Works from the command line or a browser.

---

## Install

```bash
curl -s https://raw.githubusercontent.com/meshpop/airtune/main/install.sh | bash
```

That's it. No configuration needed.

---

## Usage

Start Airtune:

```bash
airtune start
```

Identify a song:

```bash
airtune recognize https://stream.example.com/radio
```

Check that everything is running:

```bash
airtune status
```

---

## Example

```
$ airtune recognize https://stream.radioparadise.com/aac-128

  NOW PLAYING
  ────────────────────────────────────
  Artist   Queen
  Song     Bohemian Rhapsody
  Match    ████████████████░░░░  94%
```

---

## Web UI

Prefer a browser? Run the local server:

```bash
python3 ~/airtune/server.py
```

Then open **http://localhost:8000** — paste a URL, click Recognize.

---

## Commands

| Command | What it does |
|---|---|
| `airtune install` | Set up Airtune on this machine |
| `airtune start` | Start background services |
| `airtune status` | Check what's running |
| `airtune recognize <url>` | Identify the song on a stream |

---

## Requirements

- Python 3.7+
- Linux or macOS
- Internet connection

No external packages required.

---

## Uninstall

```bash
bash ~/airtune/uninstall.sh
```

---

## License

MIT
