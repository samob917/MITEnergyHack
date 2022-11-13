import pandas as pd
import numpy as np
import seaborn as sns


# parameters of the simulation

MAX_CHARGE = 13600 # Maximum charge of the EV (assumed approx. 50 kWh & 220 V, i.e. level 2) (50,000 * 3600 / 220 / 60) (the final result is the number of minutes it would take to charge the vehicle at a current of 1A)
MAX_CURRENT = 100
MAX_CURRENT_HVAC = 16.6
MAX_CURRENT_WATER = 20.8

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

# TODO: use more sensible functions and maybe produce graphs/simulations for a few different user profiles (i.e. different lists current_appliances)
outside_temp_list = [5 + 10*gaussian(t, 720, 200) for t in range(0,1441)]

def bimodal_appliances(time):
    app_list = []
    for t in range(time):
        if t < 810:
            app_list.append(np.mean(np.random.normal(90-(abs(t-420)/8), 5, 100)))
        else:
            app_list.append(np.mean(np.random.normal(93-(abs(t-1080)/8), 5, 100)))
    return app_list

#current_appliances_list = [50 + 20 * np.sin(t / 200) + np.random.randint(5) for t in range(0,1441)]
# current_appliances_list = list(bimodal_appliances(1441))
current_appliances_list = [15 + 50*gaussian(t, 420, 40) + 65*gaussian(t, 1100, 100) + np.random.randint(3) for t in range(0,1441)]
# The following three functions get the housetemp, change in t, and cost as a result
def heating_function_hvac(time,time_step, house_temp, current_hvac, house_size, outside_temp):
    # TODO: The parameters have to be chosen more realistically (I just sorta picked them at random). If that's too hard, then let's at least push our model to its limits.
    new_house_temp = house_temp + ((current_hvac * time_step)/(0.9 * house_size)) + (house_temp-outside_temp)*(-0.005 * time_step)
    return new_house_temp

def calculate_comfort_temp(outside_temp):
    return (1/3) * outside_temp + 15

def get_delta_t_hvac(new_house_temp, outside_temp):
    return calculate_comfort_temp(outside_temp) - new_house_temp

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
    if new_house_temp > calculate_comfort_temp(outside_temp):
        cost = 0
    return cost 

def heating_function_water(time_step, water_temp, current_water, tank_size, house_temp):
# TODO: The parameters have to be chosen more realistically (I just sorta picked them at random). If that's too hard, then let's at least push our model to its limits.
    new_water_temp = water_temp + ((current_water * time_step)/( 4.2 * tank_size)) + (water_temp-house_temp)*(-0.0002 * time_step)
    return new_water_temp

def get_delta_t_water(new_water_temp):
    delta_t = 60 - new_water_temp 
    return delta_t 

def cost_function_water(time, delta_t):
    if delta_t < 0:
        return 0
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
    return cost 

def get_quick_cost_water(time, time_step, water_temp, current_water, tank_size, house_temp):
    new_water_temp = heating_function_water(time_step, water_temp, current_water, tank_size, house_temp)
    delta_t_water = get_delta_t_water(new_water_temp)
    cost_water = cost_function_water(time, delta_t_water)
    return cost_water

def get_quick_cost_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp):
    new_house_temp = heating_function_hvac(time, time_step, house_temp, current_hvac, house_size, outside_temp)
    delta_t_hvac = get_delta_t_hvac(new_house_temp, outside_temp)
    cost_hvac = cost_function_hvac(time, delta_t_hvac, new_house_temp, outside_temp)
    return cost_hvac

def find_optimal_currents(time, time_step, charge, house_temp, water_temp, tank_size, house_size, outside_temp, current_appliances):
    # if we can afford to turn both on at once, do that
    if current_appliances + MAX_CURRENT_HVAC + MAX_CURRENT_WATER <= MAX_CURRENT:
        cost_water = get_quick_cost_water(time, time_step, water_temp, MAX_CURRENT_WATER, tank_size, house_temp)
        cost_hvac = get_quick_cost_hvac(time, time_step, house_temp, MAX_CURRENT_HVAC, house_size, outside_temp)
        if cost_water <= 0 and cost_hvac > 0:
            current_water = 0
            current_hvac = MAX_CURRENT_HVAC
        elif cost_water <= 0 and cost_hvac <= 0:
            current_water = 0
            current_hvac = 0
        elif cost_water > 0 and cost_hvac <= 0:
            current_water = MAX_CURRENT_WATER
            current_hvac = MAX_CURRENT_HVAC
        elif cost_water > 0 and cost_hvac > 0:
            current_water = MAX_CURRENT_WATER    
            current_hvac = MAX_CURRENT_HVAC

    
    # if we can afford to turn on both, but not at once, figure out which is worthier 
    elif (current_appliances + MAX_CURRENT_WATER <= MAX_CURRENT) and (current_appliances + MAX_CURRENT_HVAC <= MAX_CURRENT):
        # start with both off
        current_water = 0
        current_hvac = 0

        # then evaluate which one is worth more and turn that on
        new_house_temp = heating_function_hvac(time, time_step, house_temp, MAX_CURRENT_HVAC, house_size, outside_temp)
        delta_t_hvac = get_delta_t_hvac(new_house_temp, outside_temp)
        cost_hvac = cost_function_hvac(time, delta_t_hvac, new_house_temp, outside_temp)

        new_water_temp = heating_function_water(time_step, water_temp, MAX_CURRENT_WATER, tank_size, house_temp)
        delta_t_water = get_delta_t_water(new_water_temp)
        cost_water = cost_function_water(time, delta_t_water)
        
        if cost_hvac < cost_water and cost_water > 0 :
            current_water = MAX_CURRENT_WATER
        elif cost_hvac > 0 :
            current_hvac = MAX_CURRENT_HVAC

    # if we can only afford to turn on the heating, do that
    elif current_appliances + MAX_CURRENT_HVAC <= MAX_CURRENT:
        current_water = 0
        cost_hvac = get_quick_cost_hvac(time, time_step, house_temp, MAX_CURRENT_HVAC, house_size, outside_temp)
        if cost_hvac <= 0:
            current_hvac = 0
        else: 
            current_hvac = MAX_CURRENT_HVAC
    
    # if we can only afford to turn on the boiler, do that
    elif current_appliances + MAX_CURRENT_WATER <= MAX_CURRENT:
        current_hvac = 0
        cost_water = get_quick_cost_water(time, time_step, water_temp, MAX_CURRENT_WATER, tank_size, house_temp)
        if cost_water <= 0:
            current_water = 0
        else:
            current_water = MAX_CURRENT_WATER
    
    # if we can't afford to turn on either, keep both off
    else:
        current_hvac = 0
        current_water = 0

    # ev current is leftover if ev not fully charged yet
    if charge < MAX_CHARGE:
        current_ev = MAX_CURRENT - (current_hvac + current_water + current_appliances)
        # max allowed current is 36A
        if current_ev > 36:
            current_ev = 36
    else:
        current_ev = 0
    if time >= 540 and time < 840:
        current_ev = 0
    

    return (current_ev, current_hvac, current_water) # if you really want to, you can put cost_water and cost_hvac back in here

def update_values_that_are_not_currents(time, time_step, charge, house_temp, water_temp, tank_size, house_size, outside_temp, current_ev, current_hvac, current_water):
    new_house_temp = heating_function_hvac(time,time_step, house_temp, current_hvac, house_size, outside_temp)
    new_water_temp = heating_function_water(time_step, water_temp, current_water, tank_size, house_temp)
    # if ev is in, charge it
    if time < 540 or time >= 840:
        new_charge = charge + current_ev * time_step
    # else discharge it
    else:
        new_charge = charge - 18 * time_step
        if new_charge < 0:
            new_charge = 0
    return (new_charge, new_house_temp, new_water_temp)


def simulation(time_step, charge, house_temp, water_temp, current_hvac, current_water, house_size, tank_size):

    outside_temp = outside_temp_list[0]
    current_appliances = current_appliances_list[0]
    comfort_temp = calculate_comfort_temp(outside_temp)

    current_ev, current_hvac, current_water = find_optimal_currents(0, time_step, charge, house_temp, water_temp, tank_size, house_size, outside_temp, current_appliances)
    results = [[0, outside_temp, comfort_temp, current_appliances, current_ev, current_hvac, current_water, charge, house_temp, water_temp]]

    for t in range(1,1441):

        # Update values of charge and both temperatures based on the currents (and outside_temp) of the PRECEDING timestep
        charge, house_temp, water_temp = update_values_that_are_not_currents(t, time_step, charge, house_temp, water_temp, tank_size, house_size, outside_temp, current_ev, current_hvac, current_water)
    
        # Calculate new optimum currents based on CURRENT values of charge and temperatures (including outside temp)
        outside_temp = outside_temp_list[t]
        comfort_temp = calculate_comfort_temp(outside_temp)
        current_appliances = current_appliances_list[t]
        current_ev, current_hvac, current_water= find_optimal_currents(t, time_step, charge, house_temp, water_temp, tank_size, house_size, outside_temp, current_appliances)
    
        results.append([t, outside_temp, comfort_temp, current_appliances, current_ev, current_hvac, current_water, charge, house_temp, water_temp])
    
    df = pd.DataFrame(results, columns=["time", "outside_temp", "comfort_temp", "current_appliances", "current_ev", "current_hvac", "current_water", "charge EV", "house_temp", "water_temp"])
    return df

def plot_lines(df):
    return 


if __name__ == '__main__':
    # DO NOT CHANGE TIME STEP!
    df = simulation(time_step=1, charge=0, house_temp = 16, water_temp = 49, current_hvac = 16.6, current_water=20.8, house_size=555.24, tank_size=200)
    print(df)
    df["hours"] = df["time"]/60
    temp_data = df[["water_temp", "house_temp", "outside_temp", "comfort_temp","hours"]]
    temp_data = temp_data.melt('hours', var_name='cols', value_name='vals')
    plot = sns.lineplot(data=temp_data, y="vals", x="hours", hue="cols", style="cols") 
    plot.set(xlim=(0,24),xlabel="Time (H)", ylabel="Temperature (C)", title="House and Water Temp (C) over 24 hours")
    plot.legend(title='Legend', labels=["Water Temp","House Temp", "Outside Temp", "Comfort Temp"])

    # TODO: charge EV has to be put into a separate plot because the values are too large
    # TODO: plot for the currents that doesn't look awf
    
    fig = plot.get_figure()
    fig.savefig("out.png")
    fig.clf()
    df.to_csv("problem.csv")
    df["total_current"] = df["current_appliances"] + df["current_hvac"] + df["current_ev"] + df["current_water"]

    charge_data = df[["hours","current_appliances", "current_ev", "current_hvac", "current_water","total_current"]]
    charge_data = charge_data.melt('hours', var_name='cols', value_name='vals')
    plot2 = sns.lineplot(data = charge_data, y="vals", x="hours", hue="cols", style="cols" )
    plot2.set(xlim=(0,24),xlabel="Time (H)", ylabel="Current (A)", title="Currents (A) over 24 hours")
    plot2.legend(title='Legend', labels=["Appliance Current","EV Current", "HVAC Current", "Water Current"])
    fig2 = plot2.get_figure()
    fig2.savefig("charge.png", dpi=800)