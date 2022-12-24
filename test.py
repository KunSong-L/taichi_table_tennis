import numpy as np
import taichi as ti
from Table_tennis import *
from BallPosition import *

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

ti.init(arch=ti.cpu)


# 定义台球游戏中尺寸信息
tb_origin_width = 2830
tb_origin_height = 1550
reduce_scale = 4
tennis_origin_radius = 80 / 2
hole_origin_redius = 150 / 2
tennis_radius = tennis_origin_radius / reduce_scale
hole_radius = hole_origin_redius / reduce_scale

width = tb_origin_width // reduce_scale
height = tb_origin_height // reduce_scale
res = (width, height)


# physics parameter
friction_coeff_ball_table = 1.5
friction_coeff_ball_ball = 0.2
friction_coeff_rotation = tennis_origin_radius * 0.005
delta_t = 0.1

# control
table_tennis = Table_tennis(
    friction_coeff_ball_table,
    friction_coeff_ball_ball,
    friction_coeff_rotation,
    hole_radius,
    tennis_radius,
    width,
    height,
)
num = 1
table_tennis.init(num) #num为所需要的球数量，可以选择1或者15，15球就是正常开局
# GUI

my_gui = ti.GUI("table tennis", res, table_tennis.background_color)
velocity_size = 100.0
dir_angle = 0
gain_angle = 1.0
gain_vel = 10.0

hit_point_x = 0.5
hit_point_z = 0.5
hit_angle = 0

def check_win():
    res = 1
    for i in range(1, 16):
        if table_tennis.roll_in[i] == 0:
            res = 0
            break
    return res


table_canvas = ti.Vector.field(3, ti.f32, shape=res)

test_img = mpimg.imread('./fig/1.png')

for i in range(width):
    for j in range(height):
        table_canvas[i,j] = test_img[i,j,0:3]

print(table_canvas[i,j])
print(table_canvas[200,200])

my_gui.set_image(table_canvas) 

for frame in range(10000):
    my_gui.set_image(table_canvas)
    my_gui.show()