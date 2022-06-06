import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

loaded_arr = np.load('model.npy')
print(loaded_arr)
