import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

arr = np.load('model.npy')
print(np.amin(arr))
