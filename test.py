import numpy as np
import taichi as ti
from billiards import *
from BallPosition import *

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

ti.init(arch=ti.cpu)

a = ti.Vector([1,2])
b = ti.Vector([3,4])

b[0]=100

print(a)
print(b)
