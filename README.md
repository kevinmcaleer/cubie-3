# Cubie-3

A Python control library for Cubie 3, a 4-wheeled omnidirectional robot with voice control capabilities.

## Features

- **Omnidirectional Movement**: Forward, backward, strafe left/right, rotate left/right, and spin
- **Voice Control**: Speech-to-text command recognition using Vosk
- **Text-to-Speech**: Audio feedback using Espeak
- **Async Operation**: All movement commands are asynchronous for responsive control

## Requirements

- Python 3.x
- `fusion_hat` library (provides motor control, speech-to-text, and text-to-speech)
- A camera (the AI Lab Inspector demos use a Raspberry Pi Camera via `libcamera`)
- For the AI Lab Inspector: a **GitHub Copilot subscription** (preferred) or an **Anthropic API key** (fallback)

## Installation

Clone the repository:

```bash
git clone https://github.com/kevinmcaleer/cubie-3.git
cd cubie-3
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Authenticating the AI judge

The AI Lab Inspector demos (`demo03_survey.py`, `demo04_patrol.py`) send camera
frames to Claude for judgement. By default they use Claude via your **GitHub
Copilot subscription**, which needs a one-time login on the Pi.

> **Note:** This is *not* the same as `gh auth login`. Copilot rejects classic
> `ghp_` personal access tokens — you need a proper Copilot login.

The Copilot CLI is bundled with the `github-copilot-sdk` package. Log in with:

```bash
# Resolve the bundled Copilot CLI and run its OAuth device-flow login
COPILOT=$(python -c "import copilot, os; print(os.path.dirname(copilot.__file__))")/bin/copilot
"$COPILOT" login
```

Follow the printed URL and device code, then approve with the GitHub account
that holds your Copilot subscription. The token is stored in `~/.copilot/` and
picked up automatically on the next run.

**Alternative — Anthropic API:** if you'd rather use the Anthropic API directly,
set `ANTHROPIC_API_KEY` in your environment and build the judge with
`make_judge(prefer="anthropic")`.

## Usage

### Voice Control Demo

Run the voice-controlled demo:

```bash
python demo02.py
```

The robot will listen for voice commands:
- **"forward"** - Move forward
- **"backward"** - Move backward
- **"strafe left"** - Move sideways left
- **"strafe right"** - Move sideways right
- **"rotate left"** - Rotate counter-clockwise
- **"rotate right"** - Rotate clockwise
- **"stop"** - Stop all motors
- **"goodbye"** - Exit voice control mode

### Movement Demo

Run the programmatic movement demonstration:

```bash
python demo01.py
```

This sequentially demonstrates all movement commands.

### AI Lab Inspector

Cubie judges the tidiness of your workshop using Claude's vision. Requires the
camera and a logged-in AI judge (see [Authenticating the AI judge](#authenticating-the-ai-judge)).

Survey mode — you carry Cubie to each zone and it scores what it sees:

```bash
python demo03_survey.py
```

Patrol mode — Cubie drives a route itself, with a depth-based obstacle guard
that can veto any move:

```bash
python demo04_patrol.py
```

### Programmatic Control

```python
from cubie_3 import Cubie3
import asyncio

async def main():
    robot = Cubie3()

    # Move forward at 30% speed
    await robot.forward(0.3)
    await asyncio.sleep(1)

    # Strafe right
    await robot.strafe_right(0.5)
    await asyncio.sleep(0.5)

    # Stop all motors
    await robot.stop()

asyncio.run(main())
```

## API Reference

### Cubie3 Class

#### Movement Methods

All movement methods accept an optional `speed` parameter (0.0 to 1.0, default 0.5):

| Method | Description |
|--------|-------------|
| `forward(speed)` | Move forward |
| `backward(speed)` | Move backward |
| `strafe_left(speed)` | Move sideways left |
| `strafe_right(speed)` | Move sideways right |
| `rotate_left(speed)` | Rotate counter-clockwise |
| `rotate_right(speed)` | Rotate clockwise |
| `spin_in_place(speed)` | Spin rotation |
| `stop()` | Stop all motors |

#### Voice Control Methods

| Method | Description |
|--------|-------------|
| `listen()` | Start async voice command listener |
| `say(text)` | Speak text using text-to-speech |

## Hardware

Cubie 3 uses 4 motors (M0, M1, M2, M3) arranged to enable omnidirectional movement through the Fusion HAT interface.

## License

MIT License
