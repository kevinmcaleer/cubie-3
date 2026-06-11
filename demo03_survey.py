"""Demo 3 — Lab survey, bench mode (phase 1 of the video).

The floor is too messy to drive on, so Kevin carries Cubie-3 between zones
and it judges each one. No movement, no depth model needed yet.

    python demo03_survey.py
"""

import asyncio

from cubie_3 import Cubie3
from cubie_3.vision import Camera
from cubie_3.judge import make_judge

ZONES = [
    "workbench",
    "3D printer corner",
    "shelf of doom",
    "floor",
]


async def main():
    cubie = Cubie3()
    camera = Camera()
    judge = make_judge()
    await judge.start()

    from cubie_3.inspector import LabInspector
    inspector = LabInspector(cubie, camera, judge)

    try:
        await inspector.survey(ZONES)
    finally:
        await judge.stop()
        camera.close()


if __name__ == "__main__":
    asyncio.run(main())
