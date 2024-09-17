import math
import sys

sys.setrecursionlimit(1000000)


#car-related values
vehicle_mass = 300.0
tire_radius = 0.254
drive_ratio = 4.0
drag_coefficient = 0.8
downforce_coefficient = 0.0
frontal_area = 1.0
drivetrain_efficiency = 0.90

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
    if g*r > pow(speedc,2) - 2*g*(x-disc):
        return g;
    else:
        return -g

#perfect time assuming no flaws and that car stays on GG elipse. see napkin math
def lap_time():
    #if the car is able to reach the max speed of the turn by the end of the straight
    if math.sqrt(2 * g * x) > max_curve_speed:
        t3 = 2 * math.pi * r / max_curve_speed
        t2 = (-2*max_curve_speed + math.sqrt(2*g*r + 2000*g)) / (2 * g)
        t1 = t2 + math.sqrt(r/g)

    return t1 + t2 + t3

#time calculated moment by moment. Advantage is that energy and other values can be taken into account. "c" stands for current
def lap_sim(tic, timec, speedc, disc, energyc):
    dr = speedc * tic
    disc += dr
    a = acceleration(speedc, disc)
    speedc += a * tic
    energyc += abs(a) * vehicle_mass * dr
    if disc < 500:
        return lap_sim(tic, timec + tic, speedc, disc, energyc)
    else:
        return [round(timec + (math.pi*r/max_curve_speed), 2), round(energyc,-1)]

data = lap_sim(.001, 0, 0, 0, 0)
print(data[0], " seconds overall")
print(data[1]/pow(10,3), " kJ used by engine")