# tests for fluids utils
import numpy as np
import matplotlib.pyplot as plt

# rankine-hugoniot conditions
from fluids_utils import find_rh_conds

def calc_conserved_quant(u, rho, P, gam):
    c_mass = rho*u
    c_mom = P + rho*u**2
    c_eng = P/rho*gam/(gam-1) + 1/2*rho*u**2

    return c_mass, c_mom, c_eng

# input conditions
u_1 = 5000
rho_1 = 1
P_1 = 1e6
gam = 1.4

# calculate constants to be preserved
c_mass_1, c_mom_1, c_eng_1 = calc_conserved_quant(u_1, rho_1, P_1, gam)

# calculate post shock conditions
u_2, rho_2, P_2 = find_rh_conds(u_1, rho_1, P_1, gam)
c_mass_2, c_mom_2, c_eng_2 = calc_conserved_quant(u_2, rho_2, P_2, gam)

print(f"Input Conditions")
print(f"u_1: {u_1} m/s")
print(f"rho_1: {rho_1} kg/m^2")
print(f"P_1: {P_1} Pa")

print(f"Resulting Conditions")
print(f"u_2: {u_2} m/s")
print(f"rho_2: {rho_2} kg/m^2")
print(f"P_2: {P_2} Pa")

print(f"Conserved Quantities")
print(f"c_mass diff: {c_mass_2 - c_mass_1}")
print(f"c_mom diff: {c_mom_2 - c_mom_1}")
print(f"c_eng diff: {c_eng_2 - c_eng_1}")

################
## Vary Velocity
################
u_1 = np.linspace(500,3000, 20)
rho_1 = np.linspace(1,1, 20)
P_1 = np.linspace(1e6,1e6, 20)



u_2, rho_2, P_2 = find_rh_conds(u_1, rho_1, P_1, gam)

# plot in subplot
fig, axs = plt.subplots(1, 3, figsize=[8,3])
xlab = "u_1"

axs[0].plot(u_1, u_2)
axs[0].set_ylabel('u_2')
axs[0].set_xlabel(xlab)
axs[0].grid(True)

axs[1].plot(u_1, rho_2, 'tab:orange')
axs[1].set_ylabel('rho_2')
axs[1].set_xlabel(xlab)
axs[1].grid(True)

axs[2].plot(u_1, P_2, 'tab:green')
axs[2].set_ylabel('P_2')
axs[2].set_xlabel(xlab)
axs[2].grid(True)

plt.subplots_adjust(wspace=0.4, bottom=0.2)  # Increase the width of the space between subplots
fig.suptitle("Vary Inlet Velocity", fontsize=14)
plt.savefig("rh_test_velocity.png")

################
## Vary Rho
################
u_1 = np.linspace(1000,1000, 200)
rho_1 = np.logspace(-3,1, 200)
P_1 = np.linspace(1e6,1e6, 200)

u_2, rho_2, P_2 = find_rh_conds(u_1, rho_1, P_1, gam)

# plot in subplot
fig, axs = plt.subplots(1, 3, figsize=[8,3])
xlab = "rho_1"

axs[0].plot(rho_1, u_2)
axs[0].set_ylabel('u_2')
axs[0].set_xlabel(xlab)
axs[0].grid(True)
axs[0].set_xscale('log') 

axs[1].plot(rho_1, rho_2, 'tab:orange')
axs[1].set_ylabel('rho_2')
axs[1].set_xlabel(xlab)
axs[1].grid(True)
axs[1].set_xscale('log') 

axs[2].plot(rho_1, P_2, 'tab:green')
axs[2].set_ylabel('P_2')
axs[2].set_xlabel(xlab)
axs[2].grid(True)
axs[2].set_xscale('log') 

plt.subplots_adjust(wspace=0.4, bottom=0.2)  # Increase the width of the space between subplots
fig.suptitle("Vary Inlet Density", fontsize=14)
plt.savefig("rh_test_rho.png")


################
## Vary P
################
u_1 = np.linspace(1000,1000, 20)
rho_1 = np.linspace(1,1, 20)
P_1 = np.logspace(4,7, 20)

u_2, rho_2, P_2 = find_rh_conds(u_1, rho_1, P_1, gam)

# plot in subplot
fig, axs = plt.subplots(1, 3, figsize=[8,3])
xlab = "P_1"

axs[0].plot(P_1, u_2)
axs[0].set_ylabel('u_2')
axs[0].set_xlabel(xlab)
axs[0].grid(True)

axs[1].plot(P_1, rho_2, 'tab:orange')
axs[1].set_ylabel('rho_2')
axs[1].set_xlabel(xlab)
axs[1].grid(True)

axs[2].plot(P_1, P_2, 'tab:green')
axs[2].set_ylabel('P_2')
axs[2].set_xlabel(xlab)
axs[2].grid(True)

plt.subplots_adjust(wspace=0.4, bottom=0.2)  # Increase the width of the space between subplots
fig.suptitle("Vary Inlet Pressure", fontsize=14)
plt.savefig("rh_test_pressure.png")

