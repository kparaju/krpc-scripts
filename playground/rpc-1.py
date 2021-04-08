import krpc
import time

MISSION_NAME = "RPC-1"
ADDRESS = "172.17.160.1"


conn = krpc.connect(name=f"{MISSION_NAME} Controller", address=ADDRESS)
vessel = conn.space_center.active_vessel
print(f"Vessel name: {vessel.name}")

vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.engage()

vessel.control.throttle = 1
time.sleep(1)

print('Launch!')
vessel.control.activate_next_stage()

fuel_amount = conn.get_call(vessel.resources.amount, 'LiquidFuel')
expr = conn.krpc.Expression.less_than(
    conn.krpc.Expression.call(fuel_amount),
    conn.krpc.Expression.constant_float(0.1))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()
print('Staging')
vessel.control.activate_next_stage()

mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
expr = conn.krpc.Expression.greater_than(
    conn.krpc.Expression.call(mean_altitude),
    conn.krpc.Expression.constant_double(10000))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()

print('Gravity turn')
vessel.auto_pilot.target_pitch_and_heading(60, 90)

apoapsis_altitude = conn.get_call(getattr, vessel.orbit, 'apoapsis_altitude')
expr = conn.krpc.Expression.greater_than(
    conn.krpc.Expression.call(apoapsis_altitude),
    conn.krpc.Expression.constant_double(100000))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()

print('Launch stage separation')
vessel.control.throttle = 0
time.sleep(1)
vessel.control.activate_next_stage()
vessel.auto_pilot.disengage()

srf_altitude = conn.get_call(getattr, vessel.flight(), 'surface_altitude')
expr = conn.krpc.Expression.less_than(
    conn.krpc.Expression.call(srf_altitude),
    conn.krpc.Expression.constant_double(1000))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()

vessel.control.activate_next_stage()