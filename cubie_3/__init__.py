import asyncio
from fusion_hat.motor import Motor
from fusion_hat.stt import Vosk as STT
from fusion_hat.tts import Espeak


class Cubie3:
    def __init__(self):
        # Setup motors
        self.m0 = Motor(0)
        self.m1 = Motor(1)
        self.m2 = Motor(2)
        self.m3 = Motor(3)

        # Setup speech-to-text and text-to-speech
        self.stt = STT(language="en-us")
        self.tts = Espeak()

        # Set amplitude 0-200, default 100
        self.tts.set_amp(200)
        # Set speed 80-260, default 150
        self.tts.set_speed(150)
        # Set gap 0-200, default 1
        self.tts.set_gap(1)
        # Set pitch 0-99, default 80
        self.tts.set_pitch(80)

    async def forward(self, speed=0.5):
        self.m0.forward(speed)
        self.m1.forward(speed)
        self.m2.forward(speed)
        self.m3.forward(speed)

    async def backward(self, speed=0.5):
        self.m0.backward(speed)
        self.m1.backward(speed)
        self.m2.backward(speed)
        self.m3.backward(speed)

    async def stop(self):
        self.m0.stop()
        self.m1.stop()
        self.m2.stop()
        self.m3.stop()
        
    async def strafe_left(self, speed=0.5):
        self.m0.backward(speed)
        self.m1.forward(speed)
        self.m2.forward(speed)
        self.m3.backward(speed)

    async def strafe_right(self, speed=0.5):
        self.m0.forward(speed)
        self.m1.backward(speed)
        self.m2.backward(speed)
        self.m3.forward(speed)

    async def rotate_left(self, speed=0.5):
        self.m0.backward(speed)
        self.m1.forward(speed)
        self.m2.backward(speed)
        self.m3.forward(speed)

    async def rotate_right(self, speed=0.5):
        self.m0.forward(speed)
        self.m1.backward(speed)
        self.m2.forward(speed)
        self.m3.backward(speed)

    async def spin_in_place(self, speed=0.5):
        await self.rotate_right(speed)
  
    async def listen(self):
        while True:
            print("Say something")
            for result in self.stt.listen(stream=True):
                if result["done"]:
                    print(f"\r\x1b[Kfinal: {result['final']}")
                    command = result['final'].lower()

                else:
                    print(f"\r\x1b[Kpartial: {result['partial']}", end="", flush=True)
                    command = result['partial'].lower() 

                if command in ["forward", "backward", "strafe left", "strafe right", "rotate left", "rotate right", "stop"]:
                    print(f"Executing command: {command}")
                    if command == "forward":
                        await self.forward(0.6)
                    elif command == "backward":
                        await self.backward(0.6)
                    elif command == "strafe left":
                        await self.strafe_left(0.6)
                    elif command == "strafe right":
                        await self.strafe_right(0.6)
                    elif command == "rotate left":
                        await self.rotate_left(0.6)
                    elif command == "rotate right":
                        await self.rotate_right(0.6)
                    elif command == "stop":
                        await self.stop()

                    await asyncio.sleep(2)
                await self.stop()

    def say(self, text):
        """ Use text-to-speech to say the given text """
        self.tts.say(text)
        

    def start(self):
        asyncio.run(self.listen())

