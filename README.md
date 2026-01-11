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

## Installation

Clone the repository:

```bash
git clone https://github.com/kevinmcaleer/cubie-3.git
cd cubie-3
```

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
