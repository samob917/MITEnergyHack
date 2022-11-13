import pandas as pd
import numpy as np
import seaborn as sns



timestep = 1
max_current = 100
max_charge = 1

#current_hvac = 16.6
#current_water = 20.8



def do_one_timestep(current_state):
    
    # extract params of current state
    time = current_state[0]
    charge = current_state[5]
    house_temperature = current_state[6]
    warm_water_volume = current_state[7]






def calculate_inconvenience(time, charge, house_temperature, warm_water_volume):
    return charge_inconvenience(time, charge) + house_temperature_inconvenience(time, house_temperature) + warm_water_volume_inconvenience(time, warm_water_volume)
def hvac_inconvenience(time, house_temperature):


    return 
def charge_inconvenience(time, charge):
    return 1

def house_temperature_inconvenience(time, house_temperature):
    return 1

def warm_water_volume_inconvenience(time, warm_water_volume):
    return 1 

# The following three functions get the housetemp, change in t, and cost as a result
def heating_function_hvac(time,time_step, house_temp, current_hvac, house_size, outside_temp):
    new_house_temp = house_temp + ((current_hvac * time_step)/(0.9 * house_size)) + (house_temp-outside_temp)*(-10 * time_step * house_size)
    return new_house_temp
def get_delta_t_hvac(new_house_temp, outside_temp):
    delta_t = ((1/3) * outside_temp + 15)-new_house_temp
    return delta_t 
def cost_function_hvac(time, delta_t, new_house_temp, outside_temp):
    if 0 <= time <= 240:
        cost = 0.2
    elif 241 <= time <= 420:
        cost = (0.8/240)*delta_t +0.2
    elif 421 <= time <= 480:
        cost = 1
    elif 481 <= time <= 540:
        cost = -(0.5/60)*delta_t + 4.5
    elif 541 <= time <= 960:
        cost = 0.5
    elif 961 <= time <= 1020:
        cost = -(0.5/60)*delta_t - 8.5 
    elif 1021 <= time <= 1320:
        cost = 1
    elif 1321 <= time <= 1440:
        cost = -(1/120)*delta_t + 12
    if new_house_temp > ((1/3) * outside_temp + 15):
        cost = 0
    return cost 


def heating_function_water(time, time_step, water_temp, current_water, tank_size, house_temp):
    new_water_temp = water_temp + ((current_water * time_step)/( 4.2 * tank_size)) + (water_temp-house_temp)*(-2 * time_step * tank_size)
    return new_water_temp
def get_delta_t_water(new_water_temp):
    delta_t = 60 - new_water_temp 
    return delta_t 
def cost_function_water(time, delta_t,new_water_temp):
    if 0 <= time <= 240:
        cost = 0.2
    elif 241 <= time <= 420:
        cost = (0.8/240)*delta_t +0.2
    elif 421 <= time <= 480:
        cost = 1
    elif 481 <= time <= 540:
        cost = -(0.5/60)*delta_t + 4.5
    elif 541 <= time <= 960:
        cost = 0.5
    elif 961 <= time <= 1020:
        cost = -(0.5/60)*delta_t - 8.5 
    elif 1021 <= time <= 1320:
        cost = 1
    elif 1321 <= time <= 1440:
        cost = -(1/120)*delta_t + 12
    if new_water_temp >= 60:
        cost = 0
    return cost 

def cost_ev_func(t):
    return t

def get_quick_cost_water(time, time_step, water_temp, current_water, tank_size, house_temp):
    new_water_temp = heating_function_water(time, time_step, water_temp, current_water, tank_size, house_temp)
    delta_t_water = get_delta_t_water(new_water_temp)
    cost_water = cost_function_water(time, delta_t_water ,new_water_temp)
    return cost_water

def get_quick_cost_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp):
    new_house_temp = heating_function_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp)
    delta_t_hvac = get_delta_t_hvac(new_house_temp, outside_temp)
    cost_hvac = cost_function_hvac(time, delta_t_hvac, new_house_temp, outside_temp)
    return cost_hvac

def find_optimal_currents(time, time_step, charge, house_temp, water_temp, current_hvac, current_water, tank_size, house_size, outside_temp, current_appliances):
    # if we can afford to turn both on at once, do that
    cost_water = 0
    cost_hvac = 0
    if current_appliances + current_hvac + current_water <= charge:
        cost_water = get_quick_cost_water(time, time_step, water_temp, current_water, tank_size, house_temp)
        cost_hvac = get_quick_cost_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp)
        if cost_water <= 0 and cost_hvac > 0:
            current_water = 0
            new_water_temp = heating_function_water(time, time_step, water_temp, 0, tank_size, house_temp)
            current_hvac = current_hvac
            new_house_temp = heating_function_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp)
        elif cost_water <= 0 and cost_hvac <= 0:
            current_water = 0
            new_water_temp = heating_function_water(time, time_step, water_temp, 0, tank_size, house_temp)
            current_hvac = 0
            new_house_temp = heating_function_hvac(time, time_step, house_temp, 0, house_size, outside_temp)
        elif cost_water > 0 and cost_hvac <= 0:
            current_water = current_water
            new_water_temp = heating_function_water(time, time_step, water_temp, current_water, tank_size, house_temp)
        
            current_hvac = current_hvac
            new_house_temp = heating_function_hvac(time, time_step, house_temp, 0, house_size, outside_temp)
        elif cost_water > 0 and cost_hvac > 0:
            current_water = current_water
            new_water_temp = heating_function_water(time, time_step, water_temp, current_water, tank_size, house_temp)
        
            current_hvac = current_hvac
            new_house_temp = heating_function_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp)
    
    # if we can afford to turn on both, but not at once, figure out which is worthier 
    elif (current_appliances + current_water <= charge) and (current_appliances + current_hvac <= charge):
        # evaluate which one is worth more and turn that on
        cost_ev = cost_ev_func(time)


        new_house_temp = heating_function_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp)
        delta_t_hvac = get_delta_t_hvac(new_house_temp, outside_temp)
        cost_hvac = cost_function_hvac(time, delta_t_hvac,new_house_temp,outside_temp)

        new_water_temp = heating_function_water(time, time_step, water_temp, current_water, tank_size, house_temp)
        delta_t_water = get_delta_t_water(new_water_temp)
        cost_water = cost_function_water(time, delta_t_water,new_water_temp)

        if cost_hvac < cost_water and cost_water > 0 :
            current_water = current_water
            new_water_temp = heating_function_water(time,time_step,  water_temp, current_water, tank_size, house_temp)
            current_hvac = 0
            new_house_temp = heating_function_hvac(time, time_step, house_temp, 0, house_size, outside_temp)
        elif cost_hvac > 0 :
            current_hvac = current_hvac
            new_house_temp = heating_function_hvac(time,time_step,  house_temp, current_hvac, house_size, outside_temp)
            current_water = 0
            new_water_temp = heating_function_water(time, time_step, water_temp, 0, tank_size, house_temp)

    # if we can only afford to turn on the heating, do that
    elif current_appliances + current_hvac <= charge:
        
        cost_hvac = get_quick_cost_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp)
        if cost_hvac <= 0:
            current_hvac = 0
            new_house_temp = heating_function_hvac(time,time_step, house_temp, 0, house_size, outside_temp)
            current_water = 0
            new_water_temp = heating_function_water(time,time_step, water_temp, 0, tank_size, house_temp)
        else: 
            current_hvac = current_hvac
            new_house_temp = heating_function_hvac(time,time_step, house_temp, current_hvac, house_size, outside_temp)
            current_water = 0
            new_water_temp = heating_function_water(time,time_step, water_temp, 0, tank_size, house_temp)

    
    # if we can only afford to turn on the boiler, do that
    elif current_appliances + current_water <= charge:
        cost_water = get_quick_cost_water(time, time_step, water_temp, current_water, tank_size, house_temp)
        if cost_water <= 0:
            current_water = 0
            new_water_temp = heating_function_water(time, time_step,water_temp, 0, tank_size, house_temp)
            current_hvac = 0
            new_house_temp = heating_function_hvac(time, time_step,house_temp, 0, house_size, outside_temp)
        else:
            current_water = current_water
            new_water_temp = heating_function_water(time, time_step,water_temp, current_water, tank_size, house_temp)
            current_hvac = 0
            new_house_temp = heating_function_hvac(time, time_step,house_temp, 0, house_size, outside_temp)
    # if we can't afford to turn on either, keep both off
    else:
        current_hvac = 0
        new_house_temp = heating_function_hvac(time,time_step, house_temp, 0, house_size, outside_temp)
        current_water = 0
        new_water_temp = heating_function_water(time,time_step, water_temp, 0, tank_size, house_temp)
    
    # ev current is leftover if ev not fully charged yet
    if current_water + current_appliances + current_hvac < charge:
        current_ev = charge - (current_hvac + current_water + current_appliances)
    else:
        current_ev = 0
    
    cost_ev = cost_ev_func(time)

    
    

    return (current_ev, current_hvac, current_water, new_house_temp, new_water_temp, cost_hvac, cost_ev, cost_water)

def simulation(time_step, charge, house_temp, water_temp, current_hvac, current_water, house_size, tank_size, outside_temp, current_appliances):
    new_house_temp = house_temp
    new_water_temp = water_temp
    #results = [[0,charge-current_appliances, 0, 0, new_house_temp, new_water_temp, 0,0,0]]
    results = []
    for t in range(0,1440, timestep):
        current_ev, current_hvac, current_water, new_house_temp, new_water_temp, cost_hvac, cost_ev, cost_water= find_optimal_currents(t, time_step, charge, new_house_temp, new_water_temp, current_hvac, current_water, house_size,tank_size, outside_temp, current_appliances)
        results.append([t,current_ev,current_hvac, current_water,new_house_temp,new_water_temp,cost_hvac, cost_ev, cost_water ])
    df = pd.DataFrame(results, columns=["time","current_ev", "current_hvac", "current_water", "house_temp", "water_temp", "cost_hvac", "cost_ev", "cost_water"])
    return df

def plot_lines(df):
    return 


if __name__ == '__main__':
    df = simulation(time_step=1, charge=100,house_temp = 16,water_temp = 55, current_hvac = 16.6, current_water=20.8, house_size=555.24,tank_size=200 ,outside_temp=7, current_appliances=70)
    print(df)
    plot = sns.lineplot(data=df[["water_temp","house_temp", "cost_hvac", "cost_water"]])
    fig = plot.get_figure()
    fig.savefig("out.png")
    df.to_csv("problem.csv")