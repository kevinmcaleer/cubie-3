from cubie_3 import Cubie3
import asyncio

async def main():
    cubie3 = Cubie3()

    # Forward
    await cubie3.forward(0.2)
    await asyncio.sleep(0.5)
    await cubie3.stop()

    # Backward
    await cubie3.backward(0.2)
    await asyncio.sleep(0.5)
    await cubie3.stop()

    # Strafe left
    await cubie3.strafe_left(0.2)
    await asyncio.sleep(0.5)
    await cubie3.stop()

    # Strafe right
    await cubie3.strafe_right(0.2)
    await asyncio.sleep(0.5)
    await cubie3.stop()

    # Rotate left
    await cubie3.rotate_left(0.2)
    await asyncio.sleep(0.5)
    await cubie3.stop()

    # Rotate right
    await cubie3.rotate_right(0.2)
    await asyncio.sleep(0.5)
    await cubie3.stop()

if __name__ == "__main__":
    asyncio.run(main())