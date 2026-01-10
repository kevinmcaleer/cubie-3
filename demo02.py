from cubie_3 import Cubie3
import asyncio

async def main():
    cubie3 = Cubie3()
    await cubie3.tts.say("Starting movement demo.")
    await cubie3.listen()

if __name__ == "__main__":
    asyncio.run(main())