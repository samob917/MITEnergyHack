import pandas as pd



timestep = 1
max_current = 100
max_charge = 1

heat_pump_current = 1
boiler_current = 1


def do_one_timestep(current_state):
    
    # extract params of current state
    time = current_state[0]
    charge = current_state[5]
    house_temperature = current_state[6]
    warm_water_volume = current_state[7]


def find_optimal_currents(time, charge, house_temperature, warm_water_volume, current_appliances):
    # if we can afford to turn both on at once, do that
    if current_appliances + heat_pump_current + boiler_current <= max_current:
        current_heating = heat_pump_current
        current_water = boiler_current
    
    # if we can afford to turn on both, but not at once, figure out which is worthier 
    elif (current_appliances + heat_pump_current <= max_current) and (current_appliances + boiler_current <= max_current):
        # evaluate which one is worth more and turn that on
    
    # if we can only afford to turn on the heating, do that
    elif current_appliances + heat_pump_current <= max_current:
        current_heating = heat_pump_current
        current_water = 0
    
    # if we can only afford to turn on the boiler, do that
    elif current_appliances + boiler_current <= max_current:
        current_heating = 0
        current_water = boiler_current
    
    # if we can't afford to turn on either, keep both off
    else:
        current_heating = 0
        current_water = 0
    
    # ev current is leftover if ev not fully charged yet
    if charge < max_charge:
        current_ev = max_current - (current_heating + current_water)
    else:
        current_ev = 0

    return (current_ev, current_heating, current_water)


def calculate_inconvenience(time, charge, house_temperature, warm_water_volume):
    return charge_inconvenience(time, charge) + house_temperature_inconvenience(time, house_temperature) + warm_water_volume_inconvenience(time, warm_water_volume)

def charge_inconvenience(time, charge):
    return 1

def house_temperature_inconvenience(time, house_temperature):
    return 1

def warm_water_volume_inconvenience(time, warm_water_volume):
    return 1 

if __name__ == '__main__':
    # time, current_ev, current_heating, current_water, charge, house_temperature, warm_water_volume
    time = 0
    charge = 1
    house_temperature = 1
    warm_water_volume = 1
    output = pd.DataFrame()
    for time
    output.concat([1,2,3])