from math import sin, pi
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

plt.style.use(['science', 'ieee']) #see SciencePlot repo on github

### C3

NPA = np.loadtxt("../data/NPA_C3.txt")
classical = np.loadtxt("../data/classical_C3_0_2")
seesaw = np.loadtxt("../data/seesaw_C3_0_2")
graphstate = np.loadtxt("../data/graphState_C3_0_2")

n = len(NPA)
stepsize = 0.01

v0 = np.arange(0, 2.01, stepsize)
v1 = 2*np.ones(n) - v0

plt.scatter(v0/(v0 + v1), seesaw, marker='*', s=5, linewidths=0.1, label=r'Seesaw lower bound $(Q)$')

plt.plot(v0/(v0 + v1), NPA, label=r'NPA upper bound $(Q_{\text{corr}})$')
plt.plot(v0/(v0 + v1), classical, label='Best classical SW')
plt.plot(v0/(v0 + v1), graphstate, label='Graph state SW')
plt.xlabel(r'$\frac{v_0}{v_0 + v_1}$')
plt.ylabel("Social welfare")
plt.legend()
plt.savefig('C3.pdf', dpi=300)
plt.show()


### C5

NPA = np.loadtxt("../data/NPA_C5_00.txt")
classical = np.loadtxt("../data/classical_C5_0_2")
seesaw = np.loadtxt("../data/seesaw_C5_0_2")
graphstate = np.loadtxt("../data/graphState_C5_0_2")

n = len(NPA)
stepsize = 0.01

v0 = np.arange(0, 2.01, stepsize)
v1 = 2*np.ones(n) - v0
print(len(v0), len(seesaw))
plt.scatter(v0/(v0 + v1), seesaw, marker='*', s=2, linewidths=0.1, label=r'Seesaw lower bound $(Q)$', zorder=3)

plt.plot(v0/(v0 + v1), NPA, label=r'NPA upper bound $(Q_{\text{corr}})$')
plt.plot(v0/(v0 + v1), classical, label='Best classical SW')

v0 = np.arange(2/3, 2, stepsize)
v1 = 2*np.ones(len(v0)) - v0

plt.plot(v0/(v0 + v1), graphstate, label='Graph state SW')

plt.xlabel(r'$\frac{v_0}{v_0 + v_1}$')
plt.ylabel("Social welfare")
plt.legend()
plt.savefig('C5.pdf', dpi=300)
plt.show()

### C5

NPA = np.loadtxt("../data/NPA_C5_01.txt")
classical = np.loadtxt("../data/classical_C5Ssym_0_2")
seesaw = np.loadtxt("../data/seesaw_C5Sym_0_2")
graphstate = np.loadtxt("../data/graphState_C5Sym_0_2")

n = len(NPA)
stepsize = 0.01

v0 = np.arange(0, 2.01, stepsize)
v1 = 2*np.ones(n) - v0
print(len(v0), len(seesaw))
plt.scatter(v0/(v0 + v1), seesaw, marker='*', s=0.5, linewidths=0.05, label=r'Seesaw lower bound $(Q)$', zorder=3)

plt.plot(v0/(v0 + v1), NPA, label=r'NPA upper bound $(Q_{\text{corr}})$')
plt.plot(v0/(v0 + v1), classical, linewidth = 0.7, label='Best classical SW')

v0 = np.arange(1/2, 2.01, stepsize)
v1 = 2*np.ones(len(v0)) - v0

plt.plot(v0/(v0 + v1), graphstate, label='Graph state SW')

plt.xlabel(r'$\frac{v_0}{v_0 + v_1}$')
plt.ylabel("Social welfare")
plt.legend()
plt.savefig('C5_01.pdf', dpi=300)
plt.show()

