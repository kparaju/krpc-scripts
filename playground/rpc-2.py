"""
Grasshopper hover exercise
"""

import krpc
import time
import logging
import math

MISSION_NAME = "RPC-2"
ADDRESS = "192.168.1.200"
logging.basicConfig(level=logging.DEBUG)

conn = krpc.connect(name=f"{MISSION_NAME} Controller", address=ADDRESS)
vessel = conn.space_center.active_vessel
print(f"Vessel name: {vessel.name}")

vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.engage()

print('Launch')
vessel.control.activate_next_stage()


control = vessel.control
flight = vessel.flight(vessel.orbit.body.reference_frame)
ap = vessel.auto_pilot

target = 200 # target altitude above the surface, in meters
g = 9.81

# https://gist.github.com/djungelorm/01b597163491a3ed0bce
while True:
    ap.target_pitch_and_heading(90, 90)
    alt_error = target - flight.surface_altitude
    a = g - flight.vertical_speed + alt_error
    F = vessel.mass * a
    control.throttle = F / vessel.available_thrust
    time.sleep(0.01)


# def close_enough(a, b):
#     return abs(a - b) < 10

# HOVER_TARGET_METERS = 500
# MAX_SPEED = 10
# while True:
#     vessel.auto_pilot.target_pitch_and_heading(90, 90)
#     ref_frame = vessel.orbit.body.reference_frame
#     flight = vessel.flight(ref_frame)

#     altitude = flight.mean_altitude
#     speed = flight.vertical_speed
#     difference = altitude - HOVER_TARGET_METERS
#     print(speed)

#     if speed > MAX_SPEED:
#         vessel.control.throttle = min(vessel.control.throttle - 0.01, 1)
#         continue

#     if close_enough(altitude, HOVER_TARGET_METERS):
#         continue
#     elif altitude > HOVER_TARGET_METERS:
#         vessel.control.throttle = min(vessel.control.throttle - 0.01, 1)
#     elif altitude < HOVER_TARGET_METERS:
#         vessel.control.throttle = max(vessel.control.throttle + 0.01, 0)
