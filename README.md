# krpc-scripts
kRPC Scripts

# Ascent Profile Notes
* Look into Unified Powered Flight Guidance (Space Shuttle Guidance).
Implemented in [kOS](https://github.com/Noiredd/PEGAS) here.
* A [simpler](https://www.reddit.com/r/Kos/comments/86atoq/an_equation_for_a_gravity_turn/dw5dh92/),
more "KSP" alogrithm that should be easier to implement.

# Code Notes
Wait until the fuel for current stage runs out
```
fuel_amount = conn.get_call(vessel.resources_in_decouple_stage(vessel.control.current_stage - 1).amount, 'LiquidFuel')
expr = conn.krpc.Expression.less_than(
    conn.krpc.Expression.call(fuel_amount),
    conn.krpc.Expression.constant_float(0.1))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()
print('Staging')
vessel.control.activate_next_stage()
```
