import krpc
import time

MISSION_NAME = "RPC-1"
ADDRESS = "192.168.1.200"

conn = krpc.connect(name=f"{MISSION_NAME} Controller", address=ADDRESS)
vessel = conn.space_center.active_vessel
print(f"Vessel name: {vessel.name}")

vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.engage()

vessel.control.throttle = 1
time.sleep(1)

print('Launch')
vessel.control.activate_next_stage()

def set_pitch_and_heading_during_ascent(vessel):
    """
    Idea from: https://www.reddit.com/r/Kos/comments/86atoq/an_equation_for_a_gravity_turn/dw5dh92/
    TODO: assumes we want to go for a 0 inclination orbit
    TODO: more optimizations based on twr and speed
    TODO: add safety nets
    """
    total_pitch = 30
    pitch_start_altitude = 500
    pitch_end_altitude = 30000

    ap = vessel.auto_pilot
    altitude = vessel.flight().mean_altitude
    if altitude < pitch_start_altitude:
        ap.target_pitch_and_heading(90, 90)
    elif altitude < pitch_end_altitude:
        pitch = 90 - total_pitch * (altitude - pitch_start_altitude)/(pitch_end_altitude - pitch_start_altitude)
        ap.target_pitch_and_heading(pitch, 90)

while True:
    set_pitch_and_heading_during_ascent(vessel)
    time.sleep(0.1)