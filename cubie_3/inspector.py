"""The Lab Inspector — ties the camera, the AI judge, the depth guard and the
motors together.

Two modes, matching the video:
  - survey():  bench mode. Kevin is the taxi; the robot judges each zone.
  - patrol():  floor mode. The robot drives between zones itself, with the
               depth guard able to veto every single move.
"""

import asyncio

PATROL_SPEED = 0.2       # slow and dignified
STEP_SECONDS = 0.4       # drive in short steps, re-checking depth between each


class LabInspector:
    def __init__(self, cubie, camera, judge, guard=None):
        self.cubie = cubie
        self.camera = camera
        self.judge = judge
        self.guard = guard
        self.scores = {}

    async def inspect_zone(self, zone):
        """Photograph the current view, get Claude's judgement, speak it."""
        jpeg = self.camera.capture_jpeg()
        judgement = await self.judge.judge_zone(jpeg, zone)
        self.scores[zone] = judgement.score
        print(f"[{zone}] {judgement.score}/10 — {judgement.verdict}")
        print(f"        suggestion: {judgement.suggestion}")
        self.cubie.say(judgement.verdict)
        await asyncio.sleep(0.5)
        self.cubie.say(f"Suggestion: {judgement.suggestion}")
        return judgement

    async def survey(self, zones):
        """Bench mode: Kevin carries the robot to each zone in turn."""
        results = []
        for zone in zones:
            self.cubie.say(f"Take me to the {zone}.")
            input(f"--> Position Cubie facing the {zone}, then press Enter...")
            results.append(await self.inspect_zone(zone))
        self.cubie.say(
            f"Survey complete. Average score: "
            f"{sum(self.scores.values()) / len(self.scores):.1f} out of ten."
        )
        return results

    async def guarded_move(self, action, duration):
        """Drive in short steps, re-checking the depth map before every step.

        The AI gets opinions; physics gets a veto.
        """
        if self.guard is None:
            raise RuntimeError("Refusing to drive without an ObstacleGuard")

        elapsed = 0.0
        while elapsed < duration:
            clear, near = self.guard.is_path_clear(self.camera.capture())
            if not clear:
                await self.cubie.stop()
                print(f"VETO: path blocked ({near:.0%} of path ROI is near)")
                self.cubie.say("Obstacle. I'm not driving into that.")
                return False
            await action(PATROL_SPEED)
            await asyncio.sleep(STEP_SECONDS)
            await self.cubie.stop()
            elapsed += STEP_SECONDS
        return True

    async def patrol(self, route):
        """Floor mode: drive a route of (move, duration, zone_or_None) legs.

        Example route:
            [("forward", 3.0, "printer corner"),
             ("rotate_left", 1.0, None),
             ("forward", 2.0, "workbench")]
        """
        for move, duration, zone in route:
            action = getattr(self.cubie, move)
            ok = await self.guarded_move(action, duration)
            if not ok:
                self.cubie.say("Patrol aborted. Clear the path and we go again.")
                return False
            if zone:
                await self.inspect_zone(zone)
        self.cubie.say("Patrol complete. I have seen everything.")
        return True
