"""Demo 4 — Autonomous patrol with depth perception (phase 2 of the video).

Only run this once the floor is clear! The depth guard re-checks the path
before every 0.4s step and stops the motors if anything is too close.

    python demo04_patrol.py
"""

import asyncio

from cubie_3 import Cubie3
from cubie_3.vision import Camera
from cubie_3.judge import make_judge
from cubie_3.depth import DepthEstimator, ObstacleGuard
from cubie_3.inspector import LabInspector

# (move, seconds, zone to inspect on arrival — or None for a turning leg)
ROUTE = [
    ("forward", 3.0, "printer corner"),
    ("rotate_left", 1.0, None),
    ("forward", 2.5, "workbench"),
    ("rotate_left", 1.0, None),
    ("forward", 2.0, "shelf of doom"),
]


async def main():
    cubie = Cubie3()
    camera = Camera()
    judge = make_judge()
    await judge.start()

    guard = ObstacleGuard(DepthEstimator())
    inspector = LabInspector(cubie, camera, judge, guard=guard)

    cubie.say("Patrol mode. Let's see if you kept it tidy.")
    try:
        await inspector.patrol(ROUTE)
    finally:
        await cubie.stop()
        await judge.stop()
        camera.close()


if __name__ == "__main__":
    asyncio.run(main())
