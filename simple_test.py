import ati_m8_serial as ati
import numpy as np

np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
force = ati.atiM8serial(3)

print(force.zero(1000))
print(force.zero(100))
print(force.findRate(100))
