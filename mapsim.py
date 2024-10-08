#before running, look at path for excel file
#energyc is not perfect, doesn't take into account (1/2)mv^2, just torque for speeds

import math
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.setrecursionlimit(1000000)


#car-related values
vehicle_mass = 300.0
tire_radius = 0.254
drive_ratio = 4.0
drag_coefficient = 0.8
downforce_coefficient = 0.0
frontal_area = 1.0
drivetrain_efficiency = 0.90
electric_brakes = False

#related to the motor
#specific to device running the code
motor_data = '/users/benny/downloads/Motor Curves.xlsx'
GHCols = pd.read_excel(motor_data, usecols = [6,7])
rpms = GHCols["Motor Speed (RPM)"]
torques = GHCols["Torque (Capped at 80kW) (Nm)"]

#track-related values
g = 9.81
r = 50.0
x = 500.0
xt = x + math.pi * r

max_curve_speed = math.sqrt(g * r)

#unused for now
def GGV_lateral(horizontal):
    return math.sqrt(1 - pow(horizontal, 2))

def GGV_horizontal(lateral):
    return math.sqrt(1 - pow(lateral, 2))


#returns g if car can accelerate, -g if it should decelerate to meet turn speed, sometimes it fluctuates
def acceleration(speedc, disc):
    if disc < 500:
        if g*r > pow(speedc,2) - 2*g*(x-disc):
            return g;
        else:
            return -g
    else:
        return 0;

#perfect time assuming no flaws and that car stays on GG elipse. see napkin math
def lap_time():
    #if the car is able to reach the max speed of the turn by the end of the straight
    if math.sqrt(2 * g * x) > max_curve_speed:
        t3 = 2 * math.pi * r / max_curve_speed
        t2 = (-2*max_curve_speed + math.sqrt(2*g*r + 2000*g)) / (2 * g)
        t1 = t2 + math.sqrt(r/g)

    return t1 + t2 + t3

#variables calculated moment by moment. Advantage is that energy and other values can be taken into account. "c" stands for current

times = []
energies = []
speeds = []
torques2 = []
powers = []
def lap_sim(tic, timec, speedc, disc, energyc):
    dr = speedc * tic
    disc += dr
    a = acceleration(speedc, disc)
    speedc += a * tic
    if electric_brakes:
        energyc += vehicle_mass * (pow(speedc, 2) - pow(speedc - a*tic, 2))
    else:
        if a > 0:
            energyc += vehicle_mass * (pow(speedc, 2) - pow(speedc - a*tic, 2))

    


    # https://www.public.asu.edu/~grover/willys/speed.html#:~:text=Engine%20RPM%20divided%20by%20total,gives%20vehicle's%20speed%20of%20travel.
    #speed = (rpm / 60) / drive_ratio * 2 * tire_radius
    rpm = 60 * speedc * drive_ratio / (2 * tire_radius)

    #get torque value corresponding to motor speed and then use it to find force and add to energy

    found_rpm = False;
    for i in range(52):
        if rpm < rpms.get(i):
            found_rpm = True
            #not sure this is right, got it off of Google. Should their be a pi?
            energyc += torques.get(i) * drive_ratio / tire_radius * dr
            #print(round(timec, 2), "s, ", round(speedc, 2), "m/s", round(a, 2), " N-m ", round(torques.get(i), 2), "m/s^2 ", round(energyc, 2), "j")
            torques2.append(torques.get(i))
            power = torques.get(i) * drive_ratio / tire_radius * speedc
            break;
    if not found_rpm:
        energyc += torques.get(52) * drive_ratio / tire_radius * dr
        #print(round(timec, 2), "s, ", round(speedc, 2), "m/s", round(a, 2), "m/s^2", round(torques.get(52), 2), "N-m ", round(energyc, 2), "j")
        torques2.append(torques.get(52))
        power = torques.get(52) * drive_ratio / tire_radius * speedc

    times.append(timec)
    energies.append(energyc / 2356000)
    speeds.append(speedc)
    powers.append(power)
    #energyc += abs(a) * vehicle_mass * dr
    if disc < 500 + math.pi*r:
        return lap_sim(tic, timec + tic, speedc, disc, energyc)
    else:
        return [round(timec, 2), round(energyc,-1)]

data = lap_sim(.1, 0, 0, 0, 0)
print(data[0], " seconds overall")
print(data[1]/pow(10,3), " kJ used by engine")

#Torque vs Time
if False:
    plt.plot(rpms, torques)
    plt.title("Torque vs RPM")
    plt.xlabel("RPM")
    plt.ylabel("Torque")
    plt.show()

#Energy vs Time
if True:
    plt.plot(times, energies)
    plt.title("Energy Consumption vs Time (friction brakes)")
    plt.xlabel("Time (s)")
    plt.ylabel("Energy Consumed (Big Macs)")
    plt.show()

#Speed vs Time
if False:
    plt.plot(times, speeds)
    plt.title("Speed vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Speed (m/s)")
    plt.show()

#Torque vs Time
if False:
    plt.plot(times, torques2)
    plt.title("Torque vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Torque (N-m)")
    plt.show()

#Power vs Time
if False:
    plt.plot(times, powers)
    plt.title("Power vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Power (N-m/s)")
    plt.show()