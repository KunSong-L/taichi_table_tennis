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
    res
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

# 写法1速度慢
# table_canvas = ti.Vector.field(3, ti.f32, shape=res)
# bg_color = np.array([0x3C/255,0xB3/255,0x71/255])
# for i in range(res[0]):
#     for j in range(res[1]):
#         table_canvas[i,j] = bg_color

# 初始化桌面，可以在桌面上绘制图形
# table_canvas = ti.Vector.field(3, ti.f32, shape=res)

# @ti.kernel
# def init_canvas():
#     #桌面
#     for i in range(res[0]):
#         for j in range(res[1]):
#             table_canvas[i,j][0] = 0x3C/255
#             table_canvas[i,j][1] = 0xB3/255
#             table_canvas[i,j][2] = 0x71/255

# init_canvas()
# my_gui.set_image(table_canvas) 

first_static = 0
while my_gui.running:
    while table_tennis.check_static() < 0.1:
        if first_static == 1:
            table_tennis.hit_finish()
            table_tennis.first_collision = 0
            table_tennis.first_hit = -1
            first_static = 0
            print("stop")
            if table_tennis.game_state == 0:
                print("Player 1 win")
                exit()
            if table_tennis.game_state == 1:
                print("Player 2 win")
                exit()

        for e in my_gui.get_events(ti.GUI.PRESS):
            if e.key == ti.GUI.ESCAPE:
                exit()
            elif e.key == "r":
                table_tennis.init()
            elif e.key == "a":
                dir_angle += 1 * gain_angle
                dir_angle %= 360
            elif e.key == "d":
                dir_angle -= 1 * gain_angle
                dir_angle %= 360
            elif e.key == "w":
                velocity_size += 1.0 * gain_vel
                velocity_size = min(velocity_size, 200)
            elif e.key == "s":
                velocity_size -= 1.0 * gain_vel
                velocity_size = max(0.0, velocity_size)
            elif e.key == 'c': #choose position
                hit_point_x,hit_point_z,hit_angle = BP() #X:A;  y: b
                # print('hit_point_x = ',hit_point_x)
                # print('hit_point_y=', hit_point_z)
                # print('hit angle=',hit_angle)
            elif e.key == "1":
                gain_angle += 10.0
            elif e.key == "2":
                gain_angle -= 10.0
            elif e.key == "3":
                gain_vel += 10.0
            elif e.key == "4":
                gain_vel -= 10.0
            elif e.key == "z":
                radian = dir_angle * 2 * np.pi / 360
                table_tennis.hit(velocity_size, np.cos(radian), np.sin(radian), hit_point_x - 0.5, hit_point_z - 0.5, hit_angle)
                table_tennis.in_hit = 1
                table_tennis.first_collision = 0
                table_tennis.first_hit = 0
                first_static = 1

        
        table_tennis.display(my_gui, velocity_size, dir_angle, 1 )

    for e in my_gui.get_events(ti.GUI.PRESS):
        if e.key == ti.GUI.ESCAPE:
            exit()
        elif e.key == "r":
            table_tennis.init()
    table_tennis.update(delta_t)
    table_tennis.collision_white_balls()
    # table_tennis.draw_ball_in_canvas()
    table_tennis.display(my_gui, velocity_size, dir_angle, 0)
