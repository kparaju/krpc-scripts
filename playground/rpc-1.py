"""
Takes a 2 stage liquid fuel rocket to orbit.
Some of the code from kRPC Tutorial: https://krpc.github.io/krpc/tutorials/launch-into-orbit.html
"""

import krpc
import time
import logging
import math

MISSION_NAME = "RPC-1"
ADDRESS = "192.168.1.200"
logging.basicConfig(level=logging.DEBUG)
PARKING_ORBIT = 100000
ATMOSPHERE_ALTITUDE = 70000

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
    TODO: assumes we want to go for a 0 inclination orbit
    TODO: more optimizations based on twr and speed
    TODO: add safety nets
    """

    # These values need to be tuned per rocket
    total_pitch = 60
    pitch_start_altitude = 500
    pitch_end_altitude = 20000

    ap = vessel.auto_pilot
    altitude = vessel.flight().mean_altitude
    if altitude < pitch_start_altitude:
        ap.target_pitch_and_heading(90, 90)
    elif altitude < pitch_end_altitude:
        pitch = 90 - total_pitch * (altitude - pitch_start_altitude)/(pitch_end_altitude - pitch_start_altitude)
        ap.target_pitch_and_heading(pitch, 90)
    else:
        # logging.debug('Kerbin Oribtal reference frame (%.10f, %.10f, %.10f)' % vessel.position(vessel.orbit.body.reference_frame))
        # logging.debug('Oribtal reference frame (%.10f, %.10f, %.10f)' % vessel.position(vessel.orbital_reference_frame))
        # logging.debug('Surface reference frame (%.10f, %.10f, %.10f)' % vessel.position(vessel.surface_reference_frame))
        # logging.debug('Autopilot reference frame (%.10f, %.10f, %.10f)' % vessel.position(vessel.auto_pilot.reference_frame))
        ap.reference_frame = vessel.orbital_reference_frame
        ap.target_direction = (0, 1, 0)
        ap.engage()

apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

while apoapsis() < PARKING_ORBIT:
    set_pitch_and_heading_during_ascent(vessel)
    time.sleep(0.1)

vessel.control.throttle = 0



while vessel.flight().mean_altitude < ATMOSPHERE_ALTITUDE:
    time.sleep(0.1)

# TODO: wasted fuel
vessel.control.activate_next_stage()

ut = conn.add_stream(getattr, conn.space_center, 'ut')


print('Planning circularization burn')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = vessel.control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Calculate burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# Orientate ship
print('Orientating ship for circularization burn')
vessel.auto_pilot.reference_frame = node.reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

# Wait until burn
print('Waiting until circularization burn')
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2.)
lead_time = 10
conn.space_center.warp_to(burn_ut - lead_time)

print('Ready to execute burn')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
while time_to_apoapsis() - (burn_time/2.) > 0:
    pass
print('Executing burn')
vessel.control.throttle = 1.0
time.sleep(burn_time - 1)
print('Fine tuning')
vessel.control.throttle = 0.05
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
while remaining_burn()[1] > 0.1:
    pass
vessel.control.throttle = 0.0
node.remove()

print('Launch complete')