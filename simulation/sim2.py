import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def hvac_cost(time):
    if 0 <= time <= 240:
        cost = 0.2
    elif 241 <= time <= 420:
        cost = (0.8/240)*2 +0.2
    elif 421 <= time <= 480:
        cost = 1
    elif 481 <= time <= 540:
        cost = -(0.5/60)*2 + 4.5
    elif 541 <= time <= 960:
        cost = 0.5
    elif 961 <= time <= 1020:
        cost = -(0.5/60)*2 - 8.5 
    elif 1021 <= time <= 1320:
        cost = 1
    elif 1321 <= time <= 1440:
        cost = -(1/120)*2 + 12
    else:
        cost = 0.3
    return cost
def water_cost(time):
    if 0 <= time <= 240:
        cost = 0.2
    elif 241 <= time <= 420:
        cost = (0.4/240)*2 +0.2
    elif 421 <= time <= 480:
        cost = 2
    elif 481 <= time <= 540:
        cost = -(0.1/60)*2 + 4.5
    elif 541 <= time <= 960:
        cost = 0.7
    elif 961 <= time <= 1020:
        cost = -(0.5/60)*2 - 8.5 
    elif 1021 <= time <= 1320:
        cost = 1.2
    elif 1321 <= time <= 1440:
        cost = -(1/100)*2 + 12
    else:
        cost = 0.3
    return cost


def give_hvac_power(hvac_bool,temp):
    if hvac_bool == True:
        temp = temp+1
    else:
        temp = temp-1
    return temp

def give_water_power(water_bool,temp):
    if water_bool == True:
        temp = temp+1
    else:
        temp = temp-1
    return temp
def sim(hvac_temp, water_temp):
    to_list = []
    for t in range(1,1440):
        hc = hvac_cost(t)
        wc = water_cost(t)
        if hc < wc:
            water_temp = give_water_power(True, water_temp)
            hvac_temp = give_hvac_power(False, hvac_temp)

        elif hc > wc:
            water_temp = give_water_power(False, water_temp)
            hvac_temp = give_hvac_power(True, hvac_temp)

        else:
            water_temp = np.random.randint(25,35)
            hvac_temp = np.random.randint(20,40)

        to_list.append([hc,wc, hvac_temp, water_temp])
    df = pd.DataFrame(to_list, columns=["hvac_cost", "water_cost", "hvac_temp", "water_temp"])
    return df


if __name__ == '__main__':
    df = sim(20,24)
    plot = sns.lineplot(data=df[["hvac_temp","water_temp"]])
    fig = plot.get_figure()
    fig.savefig("out2.png")
    df.to_csv("problem2.csv")
    