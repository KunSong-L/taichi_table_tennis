import numpy as np
import taichi as ti
from ball import *
from table import *
from player import *


@ti.data_oriented
class Table_tennis:  # all ball number = 15+1
    def __init__(
        self,
        friction_coeff_ball_table,
        friction_coeff_ball_ball,
        friction_coeff_rotation,
        hole_radius,
        ball_radius,
        width,
        height,
    ):

        self.ball = ball(ball_radius)
        self.table = table(hole_radius, width, height)
        self.z = ti.Vector([0, 0, 1])

        self.roll_in = ti.field(ti.i32, shape=16)  # notice 0:not in   1: roll in
        self.last_rollin = ti.field(ti.i32, shape=16)

        self.score = ti.field(ti.f32, shape=())
        self.friction_coeff_ball_table = friction_coeff_ball_table
        self.friction_coeff_ball_ball = friction_coeff_ball_ball
        self.friction_coeff_rotation = friction_coeff_rotation

        self.background_color = 0x3CB371
        self.hole_color = 0x000000

        self.line_color = ti.field(ti.i32, shape=2)
        self.line_color[0] = 0xB22222
        self.line_color[1] = 0xFFA500

        self.ball_choose = ti.field(ti.i32, shape=1)
        self.ball_choose[0] = 0  # 0未选色，1已经选色
        self.now_player = ti.field(ti.i32, shape=1)
        self.now_player[0] = 0  # 选择0或者1

        self.player = player([-1, -1], self.line_color)

        # self.in_hit = 0 #在一次击球过程中
        self.first_collision = 0  # 白球是否发生了第一次碰撞

        # self.first_hit = ti.field(ti.i32, shape=1)
        # self.first_hit[0] = 0 #第一个碰到的球
        self.first_hit = -1
        self.game_state = ti.field(ti.i32, shape=1)
        self.game_state[0] = -1  # -1: not end;0:player 1 win; 1:player 2 win

    def init(self):
        self.score[None] = 0

        self.ball.init(self.table.width, self.table.height)
        self.table.init()

        for k in range(16):
            self.ball.vel[k] = ti.Vector([0.0, 0.0, 0.0])
            self.ball.rot[k] = ti.Vector([0.0, 0.0, 0.0])
            self.ball.angle[k] = ti.Vector([0.1, 0.1, 0.1])  # Gimbal Lock
            self.roll_in[k] = 0

    @ti.func
    def collision_balls(self):
        for i in range(16):
            if self.roll_in[i] == 0:
                posA = self.ball.pos[i]
                velA = self.ball.vel[i]
                rotA = self.ball.rot[i]
                for j in range(i + 1, 16):
                    if self.roll_in[i] == 0:
                        posB = self.ball.pos[j]
                        velB = self.ball.vel[j]
                        rotB = self.ball.rot[j]
                        dir = posA - posB
                        delta_x = dir.norm()
                        if delta_x < 2 * self.ball.ball_radius:
                            # !! need to deal with ball inside
                            dir = dir / delta_x  # point to A
                            normaldir = ti.Vector([dir.y, -dir.x, 0])

                            deltaV = (
                                -ti.Vector.cross(rotA + rotB, dir)
                                * self.ball.ball_radius
                            )
                            deltaVPar = self.friction_coeff_ball_ball * (
                                deltaV - deltaV.dot(self.z) * self.z
                            )

                            self.ball.vel[i] = (
                                velB.dot(dir) * dir
                                + (velA.dot(normaldir) + deltaVPar) * normaldir
                            )
                            self.ball.vel[j] = (
                                velA.dot(dir) * dir
                                + (velB.dot(normaldir) - deltaVPar) * normaldir
                            )
                            deltaRot = (
                                ti.Vector.cross(deltaV, dir)
                                * 5
                                / 2
                                / self.ball.ball_radius
                                * self.friction_coeff_ball_ball
                            )
                            self.ball.rot[i] = self.ball.rot[i] - deltaRot
                            self.ball.rot[j] = self.ball.rot[j] + deltaRot

                            offset = dir * (2 * self.ball.ball_radius - delta_x) * 0.5
                            self.ball.pos[i] += offset
                            self.ball.pos[j] -= offset

    def collision_white_balls(self):
        # 还没使用
        if self.first_collision == 0:

            posA = self.ball.pos[0]
            for j in range(1, 16):
                if self.roll_in[0] == 0:
                    posB = self.ball.pos[j]
                    dir = posA - posB
                    delta_x = dir.norm()
                    if delta_x < 2 * self.ball.ball_radius:
                        if self.first_collision == 0:  # 检测第一个碰到的球
                            self.first_hit = j
                            self.first_collision = 1

    @ti.func
    def check_boundary(self, index):
        if (
            self.ball.pos[index].x > self.table.width - self.ball.ball_radius
            or self.ball.pos[index].x < self.ball.ball_radius
        ):
            self.ball.vel[index].x *= -1
        elif (
            self.ball.pos[index].y < self.ball.ball_radius
            or self.ball.pos[index].y > self.table.height - self.ball.ball_radius
        ):
            self.ball.vel[index].y *= -1

    @ti.func
    def check_roll_in(self, index) -> ti.i32:
        res = 0
        for j in range(6):  # check roll in
            dis = self.table.hole_pos[j] - self.ball.pos[index]
            if dis.norm() < self.table.hole_radius:
                self.roll_in[index] += 1
                self.score[None] += 1
                self.ball.vel[index] = ti.Vector([0.0, 0.0, 0.0])
                res = 1
                break
        return res

    @ti.func
    def collision_boundary(self):
        for i in range(16):
            if self.roll_in[i] == 0:
                self.check_roll_in(i)
                self.check_boundary(i)

    def hit_finish(self):
        # 结束一次击球，需要判断击球是否犯规
        print("first hit ball is ", self.first_hit)
        hit_result = self.change_player()
        if hit_result == 2:
            self.game_state[0] = 1 - self.now_player[0]
        elif hit_result == 3:
            self.game_state[0] = self.now_player[0]
        elif hit_result == 1:
            self.now_player[0] = 1 - self.now_player[0]
        else:
            pass

        print("now player is ", self.now_player[0])
        for i in range(1, 16):
            self.last_rollin[i] = self.roll_in[i]

    def change_player(self) -> ti.i16:
        # 先进行是否选了花色判断
        # 返回0，继续击球，返回1，交换击球，返回2，直接结束游戏（比赛输了；返回3，进黑八，比赛赢了
        change_id = 0
        wrong_hit_flag = 1
        if self.player.ball_choose_finish == 1:
            if self.player.ball_choose[self.now_player[0]] == 0:  # 打花色球1-7
                if self.first_hit >= 1 and self.first_hit <= 7:
                    wrong_hit_flag = 0
            if self.player.ball_choose[self.now_player[0]] == 1:  # 打全色球9-15
                if self.first_hit >= 9 and self.first_hit <= 15:
                    wrong_hit_flag = 0

            if self.roll_in[8] == 1:  # 进黑八直接结束
                if self.player.hit_black[self.now_player[0]] == 1:
                    change_id = 3
                    print("犯规：打进黑八，游戏结束，失败")
                else:
                    change_id = 2
                    print("游戏结束")
            elif self.roll_in[0] == 1:  # 进了白球
                self.free_ball()
                self.roll_in[0] = 0
                change_id = 1
                print("犯规：白球落袋，自由球")
            elif wrong_hit_flag:  # 先碰到了别人球
                self.free_ball()
                change_id = 1
                print("犯规：击打对方球，自由球")
            else:  # 正常击球
                flag = 0
                for i in range(0, 16):
                    if self.last_rollin[i] != self.roll_in[i]:
                        if (
                            i
                            >= self.player.target_ball[
                                self.player.ball_choose[self.now_player[0]], 0
                            ]
                            and i
                            <= self.player.target_ball[
                                self.player.ball_choose[self.now_player[0]], 6
                            ]
                        ):

                            change_id = 0
                            flag = 1
                if flag == 0:
                    change_id = 1
                    print("正常击球，交换球权")
                else:
                    print("进入目标球，继续击球")
        else:  # 没选花色
            if self.roll_in[8] == 1:  # 进黑八直接结束
                change_id = 2
            elif self.roll_in[0] == 1:  # 进了白球
                self.free_ball()
                self.roll_in[0] = 0
                change_id = 1
            elif self.first_hit == 8:  # 碰了黑八
                self.free_ball()
                change_id = 1
            else:  # 正常击球
                # 首先击中的球进了，那么就选色成功，没进就交换
                if self.first_hit >= 1 and self.first_hit <= 7:
                    flag = 0
                    for i in range(7):
                        if self.last_rollin[i + 1] != self.roll_in[i + 1]:
                            flag = 1

                    if flag == 1:  # 选色成功
                        self.player.ball_choose[self.now_player[0]] = 0
                        self.player.ball_choose[1 - self.now_player[0]] = 1
                        self.player.ball_choose_finish = 1
                        change_id = 0
                        print("选色成功，玩家", self.now_player[0], "击打花色球")
                    else:
                        change_id = 1
                elif self.first_hit >= 9 and self.first_hit <= 15:
                    flag = 0
                    for i in range(7):
                        if self.last_rollin[i + 9] != self.roll_in[i + 9]:
                            flag = 1

                    if flag == 1:  # 选色成功
                        self.player.ball_choose[self.now_player[0]] = 1
                        self.player.ball_choose[1 - self.now_player[0]] = 0
                        self.player.ball_choose_finish = 1
                        change_id = 0
                        print("选色成功，玩家", 1 - self.now_player[0], "击打花色球")
                    else:
                        change_id = 1
                else:  # 没达到球
                    self.free_ball()
                    change_id = 1
                    print("first hit = ", self.first_hit)
                    print("没打到球")

        # print('change id = ', change_id)
        return change_id

    # 这里需要可以手动选择位置

    def free_ball(self):  # 自由球
        self.ball.pos[0] = ti.Vector([0.2 * self.table.width, 0.5 * self.table.height])

    @ti.func
    def update_pos(self, delta_t):
        for i in range(16):
            """print(i)  #used for test
            print(self.roll_in[i])
            print(self.ball.vel[i])"""
            if self.roll_in[i] == 0:
                vel = self.ball.vel[i]
                rot = self.ball.rot[i]
                EAngle = self.ball.angle[i]
                if (
                    vel.norm() < delta_t * self.friction_coeff_ball_table
                    and rot.norm() < delta_t * self.friction_coeff_rotation
                ):
                    self.ball.vel[i] = ti.Vector([0.0, 0.0, 0.0])
                    self.ball.rot[i] = ti.Vector([0.0, 0.0, 0.0])
                else:
                    sinphi = ti.sin(EAngle[1])
                    cosphi = ti.cos(EAngle[1])
                    tantheta = ti.tan(EAngle[0])
                    costheta = ti.sin(EAngle[0])
                    m = ti.Matrix(
                        [
                            [1, sinphi * tantheta, cosphi * tantheta],
                            [0, cosphi, -sinphi],
                            [0, sinphi / costheta, cosphi / costheta],
                        ]
                    )
                    rotPal = rot - rot.dot(self.z) * self.z
                    vs = vel + ti.Vector.cross(self.z, rotPal) * self.ball.ball_radius
                    s = vs / vs.norm()

                    new_vel = vel - self.friction_coeff_ball_table * s * delta_t
                    self.ball.pos[i] += new_vel * delta_t

                    new_angle = EAngle + m @ self.ball.rot[i]
                    pi = 3.1415926535
                    if new_angle.x > pi:
                        new_angle.x -= (new_angle.x // (pi * 2) + 1) * (pi * 2)
                    if new_angle.x < -pi:
                        new_angle.x -= (new_angle.x // (pi * 2)) * (pi * 2)
                    if new_angle.y > pi:
                        new_angle.y -= (new_angle.y // (pi * 2) + 1) * (pi * 2)
                    if new_angle.y < -pi:
                        new_angle.y -= (new_angle.y // (pi * 2)) * (pi * 2)
                    if new_angle.z > pi:
                        new_angle.z -= (new_angle.z // (pi * 2) + 1) * (pi * 2)
                    if new_angle.z < -pi:
                        new_angle.z -= (new_angle.z // (pi * 2)) * (pi * 2)

                    new_rot = rot + (
                        self.friction_coeff_ball_table
                        * delta_t
                        / 2
                        / self.ball.ball_radius
                        * 5
                        * ti.Vector.cross(self.z, s)
                    )

                    new_rot_norm = new_rot.norm()
                    if new_rot_norm > self.friction_coeff_rotation * delta_t:
                        new_rot -= (
                            new_rot
                            / new_rot_norm
                            * self.friction_coeff_rotation
                            * delta_t
                        )
                    else:
                        new_rot == ti.Vector([0.0, 0.0, 0.0])

                    self.ball.angle[i] = new_angle
                    if new_vel.norm() < self.friction_coeff_ball_table * delta_t * 5:
                        self.ball.vel[i] = ti.Vector([0.0, 0.0, 0.0])
                    else:
                        self.ball.vel[i] = new_vel

                    if new_rot.norm() < self.friction_coeff_rotation * delta_t * 1.5:
                        self.ball.rot[i] = ti.Vector([0.0, 0.0, 0.0])
                    else:
                        self.ball.rot[i] = new_rot
                    # print("rot=", self.ball.rot[i], "vel=", self.ball.vel[i])

    @ti.kernel
    def update(self, delta_t: ti.f32):
        self.update_pos(delta_t)
        self.collision_balls()
        self.collision_boundary()

    def hit(
        self, velocity: ti.f32, dir_x: ti.f32, dir_y: ti.f32, hit_point_x, hit_point_z
    ):
        dir = ti.Vector([dir_x, dir_y, 0.0])
        dir = dir / dir.norm()
        self.ball.vel[0] = dir * velocity

        omega_k = 5 * velocity / 2 / self.ball.ball_radius
        self.ball.rot[0] = omega_k * ti.Vector([-hit_point_z, 0, hit_point_x])
        rot_mat = ti.Matrix([[dir[1], -dir[0], 0], [dir[0], dir[1], 0], [0, 0, 1]])
        self.ball.rot[0] = rot_mat @ self.ball.rot[0]

    def check_static(self) -> ti.f32:
        res = 0.0
        for i in range(16):
            if self.roll_in[i] == 0:
                res += self.ball.vel[i].norm()
        return res

    def display(self, gui, velocity_size, dir_angle):
        pos_np = self.ball.pos.to_numpy()
        pos_np[:, 0] /= self.table.width
        pos_np[:, 1] /= self.table.height

        for i in range(0, 16):
            if self.roll_in[i] == 0:
                gui.circle(
                    pos_np[i, 0:2],
                    radius=self.ball.ball_radius,
                    color=self.ball.color[i],
                )

        hole_np = self.table.hole_pos.to_numpy()
        hole_np[:, 0] /= self.table.width
        hole_np[:, 1] /= self.table.height
        gui.circles(
            hole_np[:, 0:2], radius=self.table.hole_radius, color=self.hole_color
        )
        gui.text(
            content=f"score = {self.score}", pos=(0, 0.90), color=0xFFAA77, font_size=24
        )
        gui.text(
            content=f"velocity = {velocity_size}",
            pos=(0, 0.80),
            color=0xFFAA77,
            font_size=24,
        )
        gui.text(
            content=f"angle = {dir_angle:.2f}",
            pos=(0, 0.70),
            color=0xFFAA77,
            font_size=24,
        )
        gui.show()
